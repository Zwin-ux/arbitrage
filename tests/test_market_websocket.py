from __future__ import annotations

import asyncio
import json
from collections import deque
from datetime import datetime

import pytest

from market_data_recorder.clients.websocket import MarketWebSocketClient
from market_data_recorder.config import RetrySettings


class FakeWebSocket:
    def __init__(self, messages: list[str], *, fail_after_messages: bool = False):
        self._messages = deque(messages)
        self._fail_after_messages = fail_after_messages
        self.sent_messages: list[dict[str, object]] = []

    async def send(self, data: str) -> None:
        self.sent_messages.append(json.loads(data))

    def __aiter__(self) -> "FakeWebSocket":
        return self

    async def __anext__(self) -> str:
        if self._messages:
            return self._messages.popleft()
        if self._fail_after_messages:
            raise RuntimeError("socket dropped")
        await asyncio.sleep(3600)
        raise StopAsyncIteration


class FakeContextManager:
    def __init__(self, websocket: FakeWebSocket):
        self.websocket = websocket

    async def __aenter__(self) -> FakeWebSocket:
        return self.websocket

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


@pytest.mark.asyncio
async def test_market_websocket_reconnects_and_resubscribes() -> None:
    first = FakeWebSocket(
        ['[{"event_type":"book","asset_id":"asset-1","market":"market-1","bids":[],"asks":[],"timestamp":"1","hash":"x"}]'],
        fail_after_messages=True,
    )
    second = FakeWebSocket(
        ['{"event_type":"book","asset_id":"asset-1","market":"market-1","bids":[],"asks":[],"timestamp":"2","hash":"x"}']
    )
    contexts = deque([FakeContextManager(first), FakeContextManager(second)])
    received: list[tuple[dict[str, object], datetime]] = []
    reconnects = 0

    def connector(*args: object, **kwargs: object) -> FakeContextManager:
        return contexts.popleft()

    async def on_message(payload: dict[str, object], recorded_at: datetime) -> None:
        received.append((payload, recorded_at))

    async def on_reconnect() -> None:
        nonlocal reconnects
        reconnects += 1

    client = MarketWebSocketClient(
        url="wss://example.test/ws",
        ping_interval_seconds=1,
        ping_timeout_seconds=1,
        retry=RetrySettings(initial_seconds=0.01, max_seconds=0.01),
        connector=connector,
    )

    task = asyncio.create_task(
        client.run(
            ["asset-1"],
            on_message=on_message,
            on_reconnect=on_reconnect,
        )
    )

    try:
        while len(received) < 2:
            await asyncio.sleep(0.01)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert len(received) == 2
    assert reconnects == 1
    assert first.sent_messages[0]["assets_ids"] == ["asset-1"]
    assert second.sent_messages[0]["custom_feature_enabled"] is True
