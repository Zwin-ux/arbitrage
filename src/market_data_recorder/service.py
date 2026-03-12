from __future__ import annotations

import asyncio
from contextlib import suppress
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timezone
from typing import Any, Protocol

import structlog

from .clients.clob import ClobClient
from .clients.gamma import GammaClient
from .clients.websocket import MarketWebSocketClient
from .config import RecorderSettings
from .models import DiscoverySnapshot, HealthIssue
from .processor import EventProcessor
from .storage import DuckDBStorage
from .utils import dedupe_preserve_order


class GammaClientProtocol(Protocol):
    async def discover_markets(
        self,
        *,
        limit: int,
        order: str,
        ascending: bool,
        max_pages: int | None = None,
    ) -> DiscoverySnapshot: ...

    async def close(self) -> None: ...


class ClobClientProtocol(Protocol):
    async def get_books_batched(
        self,
        asset_ids: Sequence[str],
        *,
        batch_size: int,
    ) -> list[Any]: ...

    async def close(self) -> None: ...


class MarketWebSocketClientProtocol(Protocol):
    async def run(
        self,
        asset_ids: Sequence[str],
        *,
        on_message: Callable[[dict[str, Any], datetime], Awaitable[None]],
        on_reconnect: Callable[[], Awaitable[None]] | None = None,
    ) -> None: ...


class RecorderService:
    def __init__(
        self,
        settings: RecorderSettings,
        *,
        storage: DuckDBStorage | None = None,
        gamma_client: GammaClientProtocol | None = None,
        clob_client: ClobClientProtocol | None = None,
        websocket_client: MarketWebSocketClientProtocol | None = None,
    ) -> None:
        self._settings = settings
        self._storage = storage or DuckDBStorage(settings.duckdb_path)
        self._gamma_client = gamma_client or GammaClient(settings.gamma_api_url)
        self._clob_client = clob_client or ClobClient(settings.clob_api_url)
        self._websocket_client = websocket_client or MarketWebSocketClient(
            url=settings.market_ws_url,
            ping_interval_seconds=settings.ws_ping_interval_seconds,
            ping_timeout_seconds=settings.ws_ping_timeout_seconds,
            retry=settings.retry,
        )
        self._processor = EventProcessor(self._storage)
        self._logger = structlog.get_logger(self.__class__.__name__)

    @property
    def storage(self) -> DuckDBStorage:
        return self._storage

    async def close(self) -> None:
        await self._gamma_client.close()
        await self._clob_client.close()
        self._storage.close()

    async def discover(
        self,
        *,
        max_pages: int | None = None,
        persist_metadata: bool = False,
    ) -> DiscoverySnapshot:
        snapshot = await self._gamma_client.discover_markets(
            limit=self._settings.discovery_limit,
            order=self._settings.discovery_order,
            ascending=self._settings.discovery_ascending,
            max_pages=max_pages if max_pages is not None else self._settings.discovery_max_pages,
        )
        if persist_metadata:
            self._storage.store_discovery_snapshot(
                snapshot.items,
                recorded_at=snapshot.discovered_at,
            )
        return snapshot

    async def backfill_assets(self, asset_ids: list[str], *, source: str) -> None:
        unique_asset_ids = dedupe_preserve_order(asset_ids)
        if not unique_asset_ids:
            return
        snapshots = await self._clob_client.get_books_batched(
            unique_asset_ids,
            batch_size=self._settings.bootstrap_batch_size,
        )
        self._processor.apply_bootstrap(
            snapshots,
            source=source,
            recorded_at=datetime.now(timezone.utc),
        )

    async def record(
        self,
        *,
        runtime_seconds: float | None = None,
        asset_ids: list[str] | None = None,
        max_pages: int | None = None,
        persist_discovery_metadata: bool = False,
        stop_requested: Callable[[], bool] | None = None,
    ) -> None:
        use_discovery = asset_ids is None
        if use_discovery:
            discovered = await self.discover(
                max_pages=max_pages,
                persist_metadata=persist_discovery_metadata,
            )
            target_asset_ids = dedupe_preserve_order(discovered.asset_ids)
        else:
            assert asset_ids is not None
            target_asset_ids = dedupe_preserve_order(asset_ids)
        await self.backfill_assets(target_asset_ids, source="bootstrap")

        restart_event = asyncio.Event()
        stop_event = asyncio.Event()

        async def on_ws_message(payload: dict[str, Any], recorded_at: datetime) -> None:
            result = self._processor.handle_message(payload, recorded_at=recorded_at)
            if result.backfill_asset_ids:
                await self.backfill_assets(result.backfill_asset_ids, source="resync")
            if result.new_asset_ids and self._settings.auto_subscribe_new_markets:
                added = False
                for new_asset_id in result.new_asset_ids:
                    if new_asset_id not in target_asset_ids:
                        target_asset_ids.append(new_asset_id)
                        added = True
                if added:
                    await self.backfill_assets(result.new_asset_ids, source="new_market")
                    restart_event.set()
            if result.resolved_asset_ids and self._settings.unsubscribe_resolved_markets:
                remaining = [
                    tracked_asset
                    for tracked_asset in target_asset_ids
                    if tracked_asset not in set(result.resolved_asset_ids)
                ]
                if remaining != target_asset_ids:
                    target_asset_ids[:] = remaining
                    restart_event.set()

        async def on_reconnect() -> None:
            await self.backfill_assets(list(target_asset_ids), source="reconnect")

        async def stale_book_loop() -> None:
            stale_after_ms = int(self._settings.stale_after_seconds * 1000)
            while not stop_event.is_set():
                if stop_requested is not None and stop_requested():
                    stop_event.set()
                    return
                await asyncio.sleep(self._settings.stale_check_interval_seconds)
                now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                stale_assets = self._processor.get_stale_asset_ids(
                    now_ms=now_ms,
                    stale_after_ms=stale_after_ms,
                )
                if not stale_assets:
                    continue
                for stale_asset in stale_assets:
                    issue = HealthIssue(
                        issue_type="stale_book",
                        asset_id=stale_asset,
                        message="No update received before stale threshold; forcing REST backfill.",
                        timestamp=str(now_ms),
                    )
                    self._storage.store_health_issue(
                        issue,
                        recorded_at=datetime.now(timezone.utc),
                    )
                await self.backfill_assets(stale_assets, source="stale_backfill")

        async def rediscovery_loop() -> None:
            while not stop_event.is_set():
                if stop_requested is not None and stop_requested():
                    stop_event.set()
                    return
                await asyncio.sleep(self._settings.rediscovery_interval_seconds)
                snapshot = await self.discover(
                    max_pages=max_pages,
                    persist_metadata=persist_discovery_metadata,
                )
                new_assets = [
                    discovered_asset
                    for discovered_asset in dedupe_preserve_order(snapshot.asset_ids)
                    if discovered_asset not in target_asset_ids
                ]
                if not new_assets:
                    continue
                target_asset_ids.extend(new_assets)
                await self.backfill_assets(new_assets, source="rediscovery")
                restart_event.set()

        stale_task = asyncio.create_task(stale_book_loop())
        rediscovery_task = (
            asyncio.create_task(rediscovery_loop()) if use_discovery else None
        )

        async def run_current_subscription() -> None:
            await self._websocket_client.run(
                list(target_asset_ids),
                on_message=on_ws_message,
                on_reconnect=on_reconnect,
            )

        ws_task = asyncio.create_task(run_current_subscription())
        runtime_task = (
            asyncio.create_task(asyncio.sleep(runtime_seconds))
            if runtime_seconds is not None
            else None
        )
        external_stop_task = (
            asyncio.create_task(self._wait_for_stop_request(stop_requested, stop_event))
            if stop_requested is not None
            else None
        )

        try:
            while True:
                restart_waiter = asyncio.create_task(restart_event.wait())
                wait_set = {ws_task, restart_waiter}
                if runtime_task is not None:
                    wait_set.add(runtime_task)
                if external_stop_task is not None:
                    wait_set.add(external_stop_task)
                done, pending = await asyncio.wait(wait_set, return_when=asyncio.FIRST_COMPLETED)
                if runtime_task is not None and runtime_task in done:
                    stop_event.set()
                    for task in pending:
                        if task is runtime_task:
                            continue
                        task.cancel()
                        with suppress(asyncio.CancelledError):
                            await task
                    break
                if external_stop_task is not None and external_stop_task in done:
                    stop_event.set()
                    for task in pending:
                        if task is runtime_task or task is external_stop_task:
                            continue
                        task.cancel()
                        with suppress(asyncio.CancelledError):
                            await task
                    break
                if restart_waiter in done:
                    restart_event.clear()
                    ws_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await ws_task
                    ws_task = asyncio.create_task(run_current_subscription())
                if ws_task in done:
                    exc = ws_task.exception()
                    if exc is not None:
                        raise exc
                for task in pending:
                    if task is runtime_task:
                        continue
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task
        finally:
            stop_event.set()
            ws_task.cancel()
            stale_task.cancel()
            if rediscovery_task is not None:
                rediscovery_task.cancel()
            with suppress(asyncio.CancelledError):
                await ws_task
            with suppress(asyncio.CancelledError):
                await stale_task
            if rediscovery_task is not None:
                with suppress(asyncio.CancelledError):
                    await rediscovery_task
            if external_stop_task is not None:
                external_stop_task.cancel()
                with suppress(asyncio.CancelledError):
                    await external_stop_task

    async def _wait_for_stop_request(
        self,
        stop_requested: Callable[[], bool],
        stop_event: asyncio.Event,
    ) -> None:
        while not stop_event.is_set():
            if stop_requested():
                return
            await asyncio.sleep(0.2)
