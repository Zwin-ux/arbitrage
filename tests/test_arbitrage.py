from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from typer.testing import CliRunner

from market_data_recorder.arbitrage import ArbitrageAnalyzer
from market_data_recorder.cli import app
from market_data_recorder.models import BestBidAskEvent
from market_data_recorder.storage import DuckDBStorage


def _store_best_bid_ask(
    storage: DuckDBStorage,
    *,
    market: str,
    asset_id: str,
    best_bid: str,
    best_ask: str,
    timestamp: str,
) -> None:
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id=asset_id,
                market=market,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=None,
            timestamp=timestamp,
        ),
        recorded_at=datetime.now(timezone.utc),
    )


def test_arbitrage_finds_buy_bundle_opportunity() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="yes-token",
            best_bid="0.45",
            best_ask="0.48",
            timestamp="1000",
        )
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="no-token",
            best_bid="0.49",
            best_ask="0.50",
            timestamp="1000",
        )

        analyzer = ArbitrageAnalyzer(storage)
        opportunities = analyzer.find_opportunities(min_edge="0.01")

        assert len(opportunities) == 1
        assert opportunities[0].market == "market-1"
        assert opportunities[0].strategy == "buy_all_outcomes"
        assert opportunities[0].total_price == "0.98"
        assert opportunities[0].guaranteed_profit == "0.02"
    finally:
        storage.close()


def test_arbitrage_uses_latest_quote_per_asset() -> None:
    storage = DuckDBStorage(Path(":memory:"))
    try:
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="yes-token",
            best_bid="0.45",
            best_ask="0.55",
            timestamp="1000",
        )
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="yes-token",
            best_bid="0.51",
            best_ask="0.52",
            timestamp="1010",
        )
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="no-token",
            best_bid="0.54",
            best_ask="0.55",
            timestamp="1010",
        )

        analyzer = ArbitrageAnalyzer(storage)
        opportunities = analyzer.find_opportunities(min_edge="0.001")

        assert len(opportunities) == 1
        assert opportunities[0].timestamp == "1010"
        assert opportunities[0].total_price == "1.05"
        assert opportunities[0].strategy == "sell_all_outcomes"
        assert opportunities[0].guaranteed_profit == "0.05"
    finally:
        storage.close()


def test_arbitrage_cli_outputs_json(tmp_path: Path) -> None:
    db_path = tmp_path / "market_data.duckdb"
    storage = DuckDBStorage(db_path)
    try:
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="yes-token",
            best_bid="0.45",
            best_ask="0.48",
            timestamp="1000",
        )
        _store_best_bid_ask(
            storage,
            market="market-1",
            asset_id="no-token",
            best_bid="0.49",
            best_ask="0.50",
            timestamp="1000",
        )
    finally:
        storage.close()

    runner = CliRunner()
    result = runner.invoke(app, ["arbitrage", "--db-path", str(db_path), "--min-edge", "0.01"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == [
        {
            "market": "market-1",
            "strategy": "buy_all_outcomes",
            "timestamp": "1000",
            "total_price": "0.98",
            "guaranteed_profit": "0.02",
            "outcome_count": 2,
            "legs": [
                {
                    "asset_id": "no-token",
                    "outcome": None,
                    "best_bid": "0.49",
                    "best_ask": "0.50",
                },
                {
                    "asset_id": "yes-token",
                    "outcome": None,
                    "best_bid": "0.45",
                    "best_ask": "0.48",
                },
            ],
        }
    ]
