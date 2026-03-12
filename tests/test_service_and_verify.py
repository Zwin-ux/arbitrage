from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path

import pytest

from market_data_recorder.config import RecorderSettings
from market_data_recorder.hashing import generate_orderbook_hash
from market_data_recorder.models import BookSnapshot, DiscoveredMarket, DiscoverySnapshot, PolymarketEvent
from market_data_recorder.replay import ReplayEngine
from market_data_recorder.service import RecorderService
from market_data_recorder.storage import DuckDBStorage
from market_data_recorder.verify import RecorderVerifier


def make_snapshot(asset_id: str = "asset-1") -> BookSnapshot:
    snapshot = BookSnapshot.model_validate(
        {
            "asset_id": asset_id,
            "market": "market-1",
            "timestamp": "1",
            "bids": [{"price": "0.49", "size": "100"}],
            "asks": [{"price": "0.51", "size": "100"}],
            "min_order_size": "5",
            "tick_size": "0.01",
            "neg_risk": False,
            "last_trade_price": "0.50",
            "hash": "",
        }
    )
    snapshot.hash = generate_orderbook_hash(snapshot)
    return snapshot


class FakeGammaClient:
    def __init__(self, asset_id: str = "asset-1"):
        self.asset_id = asset_id

    async def discover_markets(
        self,
        *,
        limit: int,
        order: str,
        ascending: bool,
        max_pages: int | None = None,
    ) -> DiscoverySnapshot:
        event = PolymarketEvent.model_validate(
            {
                "id": "event-1",
                "ticker": "t",
                "slug": "slug",
                "title": "title",
                "description": "desc",
                "active": True,
                "closed": False,
                "markets": [
                    {
                        "id": "market-1",
                        "conditionId": "condition-1",
                        "question": "question",
                        "slug": "slug",
                        "description": "desc",
                        "active": True,
                        "closed": False,
                        "acceptingOrders": True,
                        "enableOrderBook": True,
                        "orderPriceMinTickSize": 0.01,
                        "orderMinSize": 5,
                        "negRisk": False,
                        "feesEnabled": False,
                        "outcomes": '["Yes","No"]',
                        "clobTokenIds": f'["{self.asset_id}","asset-2"]',
                    }
                ],
            }
        )
        return DiscoverySnapshot(
            discovered_at=datetime.now(timezone.utc),
            items=[DiscoveredMarket(event=event, market=event.markets[0])],
        )

    async def close(self) -> None:
        return None


class FakeClobClient:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    async def get_books_batched(
        self,
        asset_ids: Sequence[str],
        *,
        batch_size: int,
    ) -> list[BookSnapshot]:
        self.calls.append(list(asset_ids))
        return [make_snapshot(asset_id) for asset_id in asset_ids]

    async def close(self) -> None:
        return None


class SleepingWebSocketClient:
    async def run(
        self,
        asset_ids: Sequence[str],
        *,
        on_message: Callable[[dict[str, object], datetime], Awaitable[None]],
        on_reconnect: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        await asyncio.sleep(3600)


@pytest.mark.asyncio
async def test_service_stale_books_force_backfill() -> None:
    settings = RecorderSettings(
        duckdb_path=Path(":memory:"),
        stale_after_seconds=0.01,
        stale_check_interval_seconds=0.01,
        rediscovery_interval_seconds=60,
        bootstrap_batch_size=10,
    )
    storage = DuckDBStorage(Path(":memory:"))
    clob = FakeClobClient()
    service = RecorderService(
        settings,
        storage=storage,
        gamma_client=FakeGammaClient(),
        clob_client=clob,
        websocket_client=SleepingWebSocketClient(),  # type: ignore[arg-type]
    )
    try:
        await service.record(runtime_seconds=0.05)
        assert len(clob.calls) >= 2
        row = storage._connection.execute(  # noqa: SLF001
            "SELECT COUNT(*) FROM health_events WHERE issue_type = 'stale_book'"
        ).fetchone()
        assert row is not None
        stale_count = row[0]
        assert stale_count >= 1
    finally:
        await service.close()


def test_replay_and_verify_work_on_clean_stream() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        snapshot = make_snapshot()
        storage.store_raw_message(
            source="bootstrap",
            event_type="book",
            market=snapshot.market,
            asset_id=snapshot.asset_id,
            payload=snapshot.model_dump(mode="json"),
            recorded_at=datetime.now(timezone.utc),
        )
        storage.store_book_snapshot(snapshot, source="bootstrap", recorded_at=datetime.now(timezone.utc))

        replay = ReplayEngine(storage)
        summary = replay.replay_summary()
        verifier = RecorderVerifier(storage)
        report = verifier.verify()

        assert summary.raw_messages == 1
        assert summary.final_books == 1
        assert report.snapshot_hash_failures == 0
        assert report.stream_hash_failures == 0
    finally:
        storage.close()
