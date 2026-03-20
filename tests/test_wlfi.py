from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest
from typer.testing import CliRunner

from market_data_recorder.cli import app
from market_data_recorder.models import (
    DiscoveredMarket,
    DiscoverySnapshot,
    PolymarketEvent,
    PolymarketMarket,
)
from market_data_recorder.wlfi import (
    WLFI_BENCHMARK_SYMBOLS,
    WLFI_MARKET_KEYWORDS,
    WLFIMarketScanner,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_market(
    *,
    event_title: str = "",
    event_slug: str = "",
    question: str = "",
    market_slug: str = "",
    market_id: str = "mkt-1",
    asset_ids: list[str] | None = None,
) -> DiscoveredMarket:
    event = PolymarketEvent(
        event_id="evt-1",
        ticker=None,
        slug=event_slug or None,
        title=event_title or None,
        active=True,
        closed=False,
        markets=[],
    )
    market = PolymarketMarket(
        market_id=market_id,
        condition_id=None,
        question=question or None,
        slug=market_slug or None,
        active=True,
        closed=False,
        enable_order_book=True,
        clob_token_ids=asset_ids or ["token-a", "token-b"],
        outcomes=["Yes", "No"],
    )
    return DiscoveredMarket(event=event, market=market)


def _snapshot(items: list[DiscoveredMarket]) -> DiscoverySnapshot:
    return DiscoverySnapshot(discovered_at=datetime(2026, 1, 1, tzinfo=timezone.utc), items=items)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_wlfi_market_keywords_not_empty() -> None:
    assert len(WLFI_MARKET_KEYWORDS) > 0
    assert all(isinstance(k, str) and k == k.lower() for k in WLFI_MARKET_KEYWORDS)


def test_wlfi_benchmark_symbols_not_empty() -> None:
    assert len(WLFI_BENCHMARK_SYMBOLS) > 0
    for symbol, itype in WLFI_BENCHMARK_SYMBOLS:
        assert isinstance(symbol, str) and symbol
        assert itype in {"crypto", "stock", "etf", "index", "macro", "unknown"}


def test_scanner_matches_event_title() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(event_title="World Liberty Fi ETH purchase", question="Will ETH reach $5000?"),
        _make_market(event_title="Random election market", question="Who wins 2026?"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 1
    assert matched[0].market.question == "Will ETH reach $5000?"


def test_scanner_matches_usd1_in_question() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(question="Will USD1 depeg from $1.00?"),
        _make_market(question="Will BTC reach $200k?"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 1
    assert "USD1" in (matched[0].market.question or "")


def test_scanner_matches_wlfi_in_slug() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(market_slug="wlfi-token-price-2026"),
        _make_market(market_slug="unrelated-market-slug"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 1
    assert matched[0].market.slug == "wlfi-token-price-2026"


def test_scanner_case_insensitive() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(event_title="WORLDLIBERTYFI governance vote"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 1


def test_scanner_no_match_returns_empty() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(question="Will rain fall in London?"),
        _make_market(question="Will the Fed cut rates in Q1 2026?"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert matched == []


def test_scanner_custom_keywords() -> None:
    scanner = WLFIMarketScanner(keywords=["custom-kw"])
    items = [
        _make_market(question="This mentions custom-kw somewhere"),
        _make_market(question="No match here"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 1


def test_scanner_empty_snapshot() -> None:
    scanner = WLFIMarketScanner()
    matched = scanner.scan(_snapshot([]))
    assert matched == []


def test_scanner_multiple_matches() -> None:
    scanner = WLFIMarketScanner()
    items = [
        _make_market(question="Will WLFI token hit $1?", market_id="mkt-1"),
        _make_market(event_title="USD1 stablecoin depeg event", market_id="mkt-2"),
        _make_market(question="Will it rain tomorrow?", market_id="mkt-3"),
    ]
    matched = scanner.scan(_snapshot(items))
    assert len(matched) == 2
    matched_ids = {m.market.market_id for m in matched}
    assert "mkt-1" in matched_ids
    assert "mkt-2" in matched_ids


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_wlfi_benchmarks_cli_outputs_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["wlfi", "benchmarks"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert len(payload) > 0
    for entry in payload:
        assert "symbol" in entry
        assert "instrument_type" in entry


def test_wlfi_scan_cli_local_db_returns_matches(tmp_path: Any) -> None:
    from pathlib import Path
    from market_data_recorder.storage import DuckDBStorage
    from market_data_recorder.models import DiscoveredMarket

    db_path = tmp_path / "market_data.duckdb"

    # Seed a local discovery snapshot with one WLFI market and one unrelated one.
    wlfi_event = PolymarketEvent(
        event_id="evt-wlfi",
        title="World Liberty Fi token price 2026",
        active=True,
        closed=False,
        markets=[],
    )
    wlfi_market = PolymarketMarket(
        market_id="mkt-wlfi-1",
        question="Will WLFI token hit $1 by end of 2026?",
        slug="wlfi-token-hit-1-2026",
        active=True,
        closed=False,
        enable_order_book=True,
        clob_token_ids=["tok-yes", "tok-no"],
        outcomes=["Yes", "No"],
    )
    other_event = PolymarketEvent(
        event_id="evt-other",
        title="General election",
        active=True,
        closed=False,
        markets=[],
    )
    other_market = PolymarketMarket(
        market_id="mkt-other-1",
        question="Who wins the 2026 midterms?",
        slug="2026-midterms",
        active=True,
        closed=False,
        enable_order_book=True,
        clob_token_ids=["tok-r", "tok-d"],
        outcomes=["Republican", "Democrat"],
    )
    storage = DuckDBStorage(db_path)
    try:
        storage.store_discovery_snapshot(
            [
                DiscoveredMarket(event=wlfi_event, market=wlfi_market),
                DiscoveredMarket(event=other_event, market=other_market),
            ]
        )
    finally:
        storage.close()

    runner = CliRunner()
    result = runner.invoke(app, ["wlfi", "scan", "--db-path", str(db_path)])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["market_id"] == "mkt-wlfi-1"
    assert "wlfi" in payload[0]["slug"].lower()
