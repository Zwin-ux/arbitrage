from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import typer

from .arbitrage import ArbitrageAnalyzer
from .config import RecorderSettings
from .logging import configure_logging
from .replay import ReplayEngine
from .service import RecorderService
from .storage import DuckDBStorage
from .verify import RecorderVerifier
from .wlfi import WLFI_BENCHMARK_SYMBOLS, WLFIMarketScanner
from market_data_recorder_desktop.app_types import BenchmarkInstrumentType
from market_data_recorder_desktop.benchmark_lab import (
    BenchmarkAuditService,
    BenchmarkStore,
    BenchmarkSyncService,
    FinancialDatasetsProvider,
    resolve_benchmark_api_key,
)
from market_data_recorder_desktop.bot_services import PaperRunStore

app = typer.Typer(no_args_is_help=True)
benchmark_app = typer.Typer(no_args_is_help=True, help="Lab-only benchmark sync and audit tools.")
app.add_typer(benchmark_app, name="benchmark")
wlfi_app = typer.Typer(no_args_is_help=True, help="World Liberty Fi market discovery and benchmark presets.")
app.add_typer(wlfi_app, name="wlfi")


def _settings() -> RecorderSettings:
    settings = RecorderSettings()
    configure_logging(settings.log_level)
    return settings


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _benchmark_db_path(profile_dir: Path | None, db_path: Path | None) -> Path:
    if db_path is not None:
        return db_path
    if profile_dir is not None:
        return profile_dir / "market_data.duckdb"
    raise typer.BadParameter("Use either --profile-dir or --db-path.")


@app.command()
def discover(
    write_json: Path | None = typer.Option(default=None, help="Optional JSON output path."),
    max_pages: int | None = typer.Option(default=None, help="Cap discovery pagination for development runs."),
    persist_metadata: bool = typer.Option(
        default=False,
        help="Persist discovered event/market metadata into DuckDB.",
    ),
) -> None:
    settings = _settings()

    async def _run() -> None:
        service = RecorderService(settings)
        try:
            snapshot = await service.discover(
                max_pages=max_pages,
                persist_metadata=persist_metadata,
            )
            payload = {
                "discovered_at": snapshot.discovered_at.isoformat(),
                "markets": len(snapshot.items),
                "asset_ids": len(snapshot.asset_ids),
            }
            if write_json is not None:
                write_json.parent.mkdir(parents=True, exist_ok=True)
                write_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            typer.echo(json.dumps(payload, indent=2))
        finally:
            await service.close()

    asyncio.run(_run())


@app.command()
def record(
    runtime_seconds: float | None = typer.Option(
        default=None,
        help="Optional runtime cap. Omit to run until interrupted.",
    ),
    asset_id: list[str] = typer.Option(
        default_factory=list,
        help="Explicit asset IDs to subscribe to instead of discovery output.",
    ),
    max_pages: int | None = typer.Option(
        default=None,
        help="Cap initial discovery pagination when --asset-id is not used.",
    ),
    persist_discovery_metadata: bool = typer.Option(
        default=False,
        help="Persist discovery metadata during market-wide recordings.",
    ),
) -> None:
    settings = _settings()

    async def _run() -> None:
        service = RecorderService(settings)
        try:
            await service.record(
                runtime_seconds=runtime_seconds,
                asset_ids=asset_id or None,
                max_pages=max_pages,
                persist_discovery_metadata=persist_discovery_metadata,
            )
        finally:
            await service.close()

    asyncio.run(_run())


@app.command()
def replay(
    db_path: Path | None = typer.Option(default=None, help="Override DuckDB path."),
    limit: int | None = typer.Option(default=None, help="Limit message count."),
    output_jsonl: Path | None = typer.Option(default=None, help="Optional JSONL export path."),
) -> None:
    settings = _settings()
    storage = DuckDBStorage(db_path or settings.duckdb_path, read_only=True)
    try:
        engine = ReplayEngine(storage)
        if output_jsonl is not None:
            count = engine.export_jsonl(output_jsonl, limit=limit)
            typer.echo(json.dumps({"exported_messages": count, "output_path": str(output_jsonl)}))
            return
        typer.echo(engine.replay_summary(limit=limit).model_dump_json(indent=2))
    finally:
        storage.close()


@app.command()
def verify(
    db_path: Path | None = typer.Option(default=None, help="Override DuckDB path."),
) -> None:
    settings = _settings()
    storage = DuckDBStorage(db_path or settings.duckdb_path, read_only=True)
    try:
        verifier = RecorderVerifier(storage)
        report = verifier.verify()
        typer.echo(report.model_dump_json(indent=2))
        if report.snapshot_hash_failures or report.stream_hash_failures or report.best_bid_ask_failures:
            raise typer.Exit(code=1)
    finally:
        storage.close()


@app.command()
def arbitrage(
    db_path: Path | None = typer.Option(default=None, help="Override DuckDB path."),
    min_edge: str = typer.Option(
        default="0",
        help="Minimum guaranteed profit required to report an opportunity.",
    ),
    market_id: list[str] = typer.Option(
        default_factory=list,
        help="Limit analysis to one or more market IDs.",
    ),
) -> None:
    settings = _settings()
    storage = DuckDBStorage(db_path or settings.duckdb_path, read_only=True)
    try:
        analyzer = ArbitrageAnalyzer(storage)
        opportunities = analyzer.find_opportunities(
            min_edge=min_edge,
            market_ids=market_id or None,
        )
        typer.echo(json.dumps([item.model_dump(mode="json") for item in opportunities], indent=2))
    finally:
        storage.close()


@benchmark_app.command("sync")
def benchmark_sync(
    symbol: str = typer.Option(..., help="Exact benchmark symbol to sync, e.g. SPY or BTC-USD."),
    instrument_type: BenchmarkInstrumentType = typer.Option(
        default="stock",
        help="Reference instrument type.",
    ),
    interval: str = typer.Option(default="1m", help="Benchmark interval: 1m or 1d."),
    start_at: str = typer.Option(..., help="ISO8601 UTC start timestamp."),
    end_at: str = typer.Option(..., help="ISO8601 UTC end timestamp."),
    profile_dir: Path | None = typer.Option(default=None, help="Profile data dir that owns market_data.duckdb."),
    db_path: Path | None = typer.Option(default=None, help="Explicit benchmark DuckDB path."),
) -> None:
    api_key = resolve_benchmark_api_key()
    if not api_key:
        raise typer.BadParameter(
            "No benchmark API key found. Set SUPERIOR_BENCHMARK_API_KEY or FINANCIAL_DATASETS_API_KEY."
        )
    benchmark_db = _benchmark_db_path(profile_dir, db_path)
    service = BenchmarkSyncService(FinancialDatasetsProvider(), BenchmarkStore(benchmark_db))
    result = service.sync_symbol(
        symbol=symbol,
        instrument_type=instrument_type,
        interval=cast(Any, interval),
        start_at=_parse_iso_datetime(start_at),
        end_at=_parse_iso_datetime(end_at),
        api_key=api_key,
    )
    typer.echo(json.dumps(result, indent=2))


@benchmark_app.command("audit")
def benchmark_audit(
    profile_id: str = typer.Option(..., help="Profile id that owns the paper session."),
    run_id: str | None = typer.Option(default=None, help="Run id to audit."),
    session_id: str | None = typer.Option(default=None, help="Session id to read existing audits for."),
    profile_dir: Path | None = typer.Option(default=None, help="Profile data dir that owns DuckDB files."),
    db_path: Path | None = typer.Option(default=None, help="Explicit benchmark DuckDB path."),
    state_db_path: Path | None = typer.Option(default=None, help="Explicit superior_state DuckDB path."),
) -> None:
    benchmark_db = _benchmark_db_path(profile_dir, db_path)
    store = BenchmarkStore(benchmark_db)
    if session_id:
        audits = BenchmarkAuditService(store).audits_for_session(profile_id, session_id)
        typer.echo(json.dumps([audit.model_dump(mode="json") for audit in audits], indent=2))
        return
    if not run_id:
        raise typer.BadParameter("Use --run-id to compute a run audit or --session-id to read session audits.")
    resolved_state_db = state_db_path or (
        (profile_dir / "superior_state.duckdb") if profile_dir is not None else None
    )
    if resolved_state_db is None:
        raise typer.BadParameter("Use either --profile-dir or --state-db-path.")
    paper_store = PaperRunStore(state_db_path=resolved_state_db)
    runs = [
        run for run in paper_store.list_runs_for_profile_id(profile_id)
        if run.run_id == run_id
    ]
    if not runs:
        raise typer.BadParameter(f"No run found for profile {profile_id} and run id {run_id}.")
    audits = BenchmarkAuditService(store).audit_latest_run(profile_id, runs[0])
    typer.echo(json.dumps([audit.model_dump(mode="json") for audit in audits], indent=2))


@wlfi_app.command("scan")
def wlfi_scan(
    db_path: Path | None = typer.Option(default=None, help="Override DuckDB path for the local discovery snapshot."),
    live: bool = typer.Option(
        default=False,
        help="Fetch a fresh discovery page from the Gamma API instead of using the local snapshot.",
    ),
    max_pages: int | None = typer.Option(
        default=5,
        help="Cap Gamma API pagination when --live is set.",
    ),
    keyword: list[str] = typer.Option(
        default_factory=list,
        help="Extra keywords to match in addition to the built-in WLFI keyword list.",
    ),
) -> None:
    """Scan for Polymarket prediction markets related to World Liberty Fi.

    Without --live the command reads the locally stored discovery metadata
    (markets/events tables).  With --live it queries the Gamma API directly.

    Output is a JSON array of matching markets with their event title,
    market question, slug, and asset IDs.
    """
    settings = _settings()
    if keyword:
        from .wlfi import WLFI_MARKET_KEYWORDS  # noqa: PLC0415
        scanner = WLFIMarketScanner(keywords=WLFI_MARKET_KEYWORDS + list(keyword))
    else:
        scanner = WLFIMarketScanner()

    if live:
        from .clients.gamma import GammaClient  # noqa: PLC0415

        async def _run() -> list[dict[str, Any]]:
            gamma = GammaClient(base_url=settings.gamma_api_url)
            try:
                items = await scanner.fetch(gamma, max_pages=max_pages)
            finally:
                await gamma.close()
            return _serialize_markets(items)

        typer.echo(json.dumps(asyncio.run(_run()), indent=2))
        return

    # --- local snapshot path ---
    storage = DuckDBStorage(db_path or settings.duckdb_path, read_only=True)
    try:
        from .models import DiscoverySnapshot, DiscoveredMarket, PolymarketEvent, PolymarketMarket  # noqa: PLC0415
        from datetime import datetime, timezone  # noqa: PLC0415

        rows = storage.fetch_discovered_markets()

        items: list[DiscoveredMarket] = []
        for row in rows:
            (
                event_id, ticker, event_slug, title,
                event_active, event_closed,
                market_id, condition_id, question, market_slug,
                active, closed, accepting_orders, enable_order_book,
                neg_risk, fees_enabled, order_min_size, tick_size,
                clob_token_ids_json, outcomes_json,
            ) = row
            event = PolymarketEvent(
                event_id=event_id or "",
                ticker=ticker,
                slug=event_slug,
                title=title,
                active=bool(event_active),
                closed=bool(event_closed),
                markets=[],
            )
            market = PolymarketMarket(
                market_id=market_id,
                condition_id=condition_id,
                question=question,
                slug=market_slug,
                active=bool(active),
                closed=bool(closed),
                accepting_orders=accepting_orders,
                enable_order_book=bool(enable_order_book),
                neg_risk=neg_risk,
                fees_enabled=fees_enabled,
                order_min_size=order_min_size,
                order_price_min_tick_size=tick_size,
                clob_token_ids=json.loads(clob_token_ids_json or "[]"),
                outcomes=json.loads(outcomes_json or "[]"),
            )
            items.append(DiscoveredMarket(event=event, market=market))

        snapshot = DiscoverySnapshot(
            discovered_at=datetime.now(timezone.utc),
            items=items,
        )
        matched = scanner.scan(snapshot)
        typer.echo(json.dumps(_serialize_markets(matched), indent=2))
    finally:
        storage.close()


@wlfi_app.command("benchmarks")
def wlfi_benchmarks() -> None:
    """Print pre-configured WLFI benchmark symbol presets.

    Each entry shows the symbol and instrument type accepted by
    ``market-data-recorder benchmark sync``.
    """
    result = [{"symbol": symbol, "instrument_type": itype} for symbol, itype in WLFI_BENCHMARK_SYMBOLS]
    typer.echo(json.dumps(result, indent=2))


def _serialize_markets(items: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "event_title": item.event.title,
                "event_slug": item.event.slug,
                "market_id": item.market.market_id,
                "question": item.market.question,
                "slug": item.market.slug,
                "asset_ids": item.market.clob_token_ids,
            }
        )
    return out
