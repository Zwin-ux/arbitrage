from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from market_data_recorder.hashing import generate_orderbook_hash
from market_data_recorder.models import BookSnapshot
from market_data_recorder.processor import EventProcessor
from market_data_recorder.storage import DuckDBStorage


def make_snapshot(*, asset_id: str = "asset-1", market: str = "market-1") -> BookSnapshot:
    snapshot = BookSnapshot.model_validate(
        {
            "asset_id": asset_id,
            "market": market,
            "timestamp": "1000",
            "bids": [{"price": "0.49", "size": "100"}],
            "asks": [{"price": "0.51", "size": "120"}],
            "min_order_size": "5",
            "tick_size": "0.01",
            "neg_risk": False,
            "last_trade_price": "0.50",
            "hash": "",
        }
    )
    snapshot.hash = generate_orderbook_hash(snapshot)
    return snapshot


def test_processor_resyncs_on_price_change_hash_mismatch() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        processor = EventProcessor(storage)
        snapshot = make_snapshot()
        processor.apply_bootstrap(
            [snapshot],
            source="bootstrap",
            recorded_at=datetime.now(timezone.utc),
        )

        result = processor.handle_message(
            {
                "event_type": "price_change",
                "market": snapshot.market,
                "timestamp": "1010",
                "price_changes": [
                    {
                        "asset_id": snapshot.asset_id,
                        "price": "0.50",
                        "size": "80",
                        "side": "BUY",
                        "hash": "bad-hash",
                        "best_bid": "0.50",
                        "best_ask": "0.51",
                    }
                ],
            },
            recorded_at=datetime.now(timezone.utc),
        )

        assert result.backfill_asset_ids == [snapshot.asset_id]
        assert any(issue.issue_type == "price_change_hash_mismatch" for issue in result.health_issues)
    finally:
        storage.close()


def test_tick_size_change_is_persisted() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        processor = EventProcessor(storage)
        snapshot = make_snapshot()
        processor.apply_bootstrap(
            [snapshot],
            source="bootstrap",
            recorded_at=datetime.now(timezone.utc),
        )

        processor.handle_message(
            {
                "event_type": "tick_size_change",
                "asset_id": snapshot.asset_id,
                "market": snapshot.market,
                "old_tick_size": "0.01",
                "new_tick_size": "0.001",
                "timestamp": "1020",
            },
            recorded_at=datetime.now(timezone.utc),
        )

        row = storage._connection.execute(  # noqa: SLF001
            "SELECT new_tick_size FROM tick_size_changes"
        ).fetchone()
        assert row is not None
        stored_tick_size = row[0]
        assert stored_tick_size == "0.001"
    finally:
        storage.close()


def test_websocket_book_is_enriched_from_existing_state() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        processor = EventProcessor(storage)
        snapshot = make_snapshot()
        processor.apply_bootstrap(
            [snapshot],
            source="bootstrap",
            recorded_at=datetime.now(timezone.utc),
        )
        websocket_snapshot = snapshot.model_copy(deep=True)
        websocket_snapshot.timestamp = "2000"
        websocket_snapshot.hash = generate_orderbook_hash(websocket_snapshot)
        websocket_snapshot.min_order_size = None
        websocket_snapshot.tick_size = None
        websocket_snapshot.neg_risk = None
        websocket_snapshot.last_trade_price = None

        result = processor.handle_message(
            websocket_snapshot.model_dump(mode="json"),
            recorded_at=datetime.now(timezone.utc),
        )

        assert result.health_issues == []
    finally:
        storage.close()


def test_market_resolved_returns_resolved_assets() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        processor = EventProcessor(storage)
        result = processor.handle_message(
            {
                "event_type": "market_resolved",
                "id": "1031769",
                "question": "Will X happen?",
                "market": "market-1",
                "slug": "will-x-happen",
                "description": "desc",
                "assets_ids": ["asset-1", "asset-2"],
                "outcomes": ["Yes", "No"],
                "winning_asset_id": "asset-1",
                "winning_outcome": "Yes",
                "event_message": {"id": "125819"},
                "timestamp": "2000",
            },
            recorded_at=datetime.now(timezone.utc),
        )

        assert result.resolved_asset_ids == ["asset-1", "asset-2"]
        row = storage._connection.execute(  # noqa: SLF001
            "SELECT COUNT(*) FROM market_lifecycle WHERE event_type = 'market_resolved'"
        ).fetchone()
        assert row is not None
        count = row[0]
        assert count == 1
    finally:
        storage.close()
