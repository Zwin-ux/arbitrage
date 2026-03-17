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
