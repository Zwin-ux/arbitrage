from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from market_data_recorder_desktop.app_types import AppProfile, BenchmarkBar, PaperExecutionSummary, PaperPosition, PaperRunResult
from market_data_recorder_desktop.benchmark_lab import (
    BenchmarkAuditService,
    BenchmarkLinkService,
    BenchmarkStore,
    FinancialDatasetsProvider,
)
from market_data_recorder_desktop.credentials import CredentialVault
from market_data_recorder_desktop.profiles import ProfileStore


def test_financial_benchmark_key_uses_keyring_only(app_paths: Any, fake_keyring: Any) -> None:
    store = ProfileStore(app_paths)
    profile = store.create_profile(display_name="Bench", template="Guided", enabled_venues=["Polymarket"])
    vault = CredentialVault(backend=fake_keyring)

    result = vault.save(
        profile.id,
        "financial_benchmark",
        {"provider_name": "Financial Datasets", "api_key": "fd-demo-key"},
    )

    assert result.status == "validated"
    assert "fd-demo-key" not in store.profiles_path.read_text(encoding="utf-8")
    assert vault.status(profile.id, "financial_benchmark").status == "validated"


def test_financial_datasets_provider_normalizes_search_bars_and_quote() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/stock-search-data"):
            return httpx.Response(200, json={"data": [{"ticker": "SPY", "name": "SPDR S&P 500 ETF", "instrument_type": "etf"}]})
        if request.url.path.endswith("/crypto-search-data"):
            return httpx.Response(200, json={"data": []})
        if request.url.path.endswith("/stock-prices"):
            return httpx.Response(
                200,
                json={
                    "prices": [
                        {"time": "2026-03-15T10:00:00Z", "open": 500.0, "high": 501.0, "low": 499.0, "close": 500.5, "volume": 1000},
                        {"time": "2026-03-15T10:01:00Z", "open": 500.5, "high": 502.0, "low": 500.0, "close": 501.5, "volume": 1100},
                    ]
                },
            )
        if request.url.path.endswith("/price-snapshot"):
            return httpx.Response(200, json={"data": [{"time": "2026-03-15T10:01:00Z", "price": 501.5, "bid": 501.4, "ask": 501.6}]})
        raise AssertionError(f"Unexpected path: {request.url.path}")

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.financialdatasets.ai")
    provider = FinancialDatasetsProvider(client=client)

    instruments = provider.search_symbol("SPY", api_key="test-key")
    bars = provider.fetch_bars(
        "SPY",
        instrument_type="etf",
        start_at=datetime(2026, 3, 15, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 3, 15, 10, 2, tzinfo=timezone.utc),
        interval="1m",
        api_key="test-key",
    )
    quote = provider.fetch_latest_quote("SPY", instrument_type="etf", api_key="test-key")

    assert instruments[0].symbol == "SPY"
    assert bars[-1].close == 501.5
    assert quote is not None
    assert quote.price == 501.5


def test_benchmark_audit_marks_aligned_when_link_and_bars_exist(app_paths: Any) -> None:
    profile = AppProfile(
        id="bench-profile",
        display_name="Benchmark",
        data_dir=app_paths.data_dir / "bench-profile",
        enabled_venues=["Polymarket"],
        lab_enabled=True,
    )
    db_path = profile.data_dir / "market_data.duckdb"
    store = BenchmarkStore(db_path)
    link_service = BenchmarkLinkService(store)
    link_service.save_manual_link(
        profile_id=profile.id,
        market_slug="spy-close",
        symbol="SPY",
        instrument_type="etf",
        interval_preference="1m",
        notes="Benchmark for ETF close market",
    )
    start_at = datetime(2026, 3, 15, 10, 0, tzinfo=timezone.utc)
    store.upsert_bars(
        [
            BenchmarkBar(
                symbol="SPY",
                instrument_type="etf",
                interval="1m",
                recorded_at=start_at,
                open=500.0,
                high=501.0,
                low=499.0,
                close=500.5,
            ),
            BenchmarkBar(
                symbol="SPY",
                instrument_type="etf",
                interval="1m",
                recorded_at=start_at + timedelta(minutes=1),
                open=500.5,
                high=502.0,
                low=500.0,
                close=501.5,
            ),
        ]
    )
    run = PaperRunResult(
        run_id="run-bench-1",
        profile_id=profile.id,
        executed_at=start_at + timedelta(minutes=1),
        strategy_ids=["internal-binary"],
        candidate_ids=["cand-1"],
        status="completed",
        deployed_capital_cents=1500,
        expected_edge_bps=72,
        realized_pnl_cents=12,
        realized_edge_bps=81,
        opportunity_quality_score=76,
        notes="benchmark audit",
        positions=[
            PaperPosition(
                market_slug="spy-close",
                strategy_id="internal-binary",
                venue_labels=["Polymarket"],
                deployed_capital_cents=1500,
                expected_edge_bps=72,
                realized_pnl_cents=12,
            )
        ],
        execution=PaperExecutionSummary(fill_ratio=1.0, realized_edge_bps=81, slippage_bps=12, notes="ok"),
    )

    audits = BenchmarkAuditService(store).audit_latest_run(profile.id, run)

    assert audits[0].verdict == "Aligned"
    assert audits[0].symbol == "SPY"
    assert store.recent_audits(profile.id, limit=1)[0].audit_id == audits[0].audit_id


def test_benchmark_audit_is_not_comparable_without_link(app_paths: Any) -> None:
    profile = AppProfile(
        id="bench-profile-2",
        display_name="Benchmark Missing",
        data_dir=app_paths.data_dir / "bench-profile-2",
        enabled_venues=["Polymarket"],
        lab_enabled=True,
    )
    store = BenchmarkStore(profile.data_dir / "market_data.duckdb")
    run = PaperRunResult(
        run_id="run-bench-2",
        profile_id=profile.id,
        executed_at=datetime(2026, 3, 15, 10, 1, tzinfo=timezone.utc),
        strategy_ids=["internal-binary"],
        candidate_ids=["cand-2"],
        status="completed",
        deployed_capital_cents=1000,
        expected_edge_bps=50,
        realized_pnl_cents=7,
        realized_edge_bps=44,
        opportunity_quality_score=60,
        notes="no link",
        positions=[
            PaperPosition(
                market_slug="unmapped-market",
                strategy_id="internal-binary",
                venue_labels=["Polymarket"],
                deployed_capital_cents=1000,
                expected_edge_bps=50,
                realized_pnl_cents=7,
            )
        ],
        execution=PaperExecutionSummary(fill_ratio=1.0, realized_edge_bps=44, slippage_bps=8, notes="ok"),
    )

    audits = BenchmarkAuditService(store).audit_latest_run(profile.id, run)

    assert audits[0].verdict == "Not comparable"
    assert audits[0].coverage_state == "no_coverage"
