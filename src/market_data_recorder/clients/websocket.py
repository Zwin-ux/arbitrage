from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timezone
from typing import Any, Protocol

import structlog
import websockets

from ..config import RetrySettings
from ..models import SubscriptionMessage


class WebSocketConnection(Protocol):
    async def send(self, data: str) -> None: ...

    def __aiter__(self) -> Any: ...


MessageHandler = Callable[[dict[str, Any], datetime], Awaitable[None]]
ReconnectHandler = Callable[[], Awaitable[None]]


class MarketWebSocketClient:
    def __init__(
        self,
        *,
        url: str,
        ping_interval_seconds: float,
        ping_timeout_seconds: float,
        retry: RetrySettings,
        connector: Callable[..., Any] | None = None,
    ):
        self._url = url
        self._ping_interval_seconds = ping_interval_seconds
        self._ping_timeout_seconds = ping_timeout_seconds
        self._retry = retry
        self._connector = connector or websockets.connect
        self._logger = structlog.get_logger(self.__class__.__name__)

    async def run(
        self,
        asset_ids: Sequence[str],
        *,
        on_message: MessageHandler,
        on_reconnect: ReconnectHandler | None = None,
    ) -> None:
        first_connection = True
        delay = self._retry.initial_seconds
        while True:
            try:
                async with self._connector(
                    self._url,
                    ping_interval=self._ping_interval_seconds,
                    ping_timeout=self._ping_timeout_seconds,
                    max_size=None,
                ) as websocket:
                    await websocket.send(
                        SubscriptionMessage(
                            assets_ids=list(asset_ids),
                            custom_feature_enabled=True,
                        ).model_dump_json()
                    )
                    if not first_connection and on_reconnect is not None:
                        await on_reconnect()
                    first_connection = False
                    delay = self._retry.initial_seconds
                    async for raw_message in websocket:
                        payload = json.loads(raw_message)
                        recorded_at = datetime.now(timezone.utc)
                        if isinstance(payload, list):
                            for item in payload:
                                if isinstance(item, dict):
                                    await on_message(item, recorded_at)
                            continue
                        if isinstance(payload, dict):
                            await on_message(payload, recorded_at)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._logger.warning(
                    "market_ws_error",
                    error=str(exc),
                    reconnect_in_seconds=delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._retry.max_seconds)
