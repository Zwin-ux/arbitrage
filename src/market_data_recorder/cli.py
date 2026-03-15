from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer

from .arbitrage import ArbitrageAnalyzer
from .config import RecorderSettings
from .logging import configure_logging
from .replay import ReplayEngine
from .service import RecorderService
from .storage import DuckDBStorage
from .verify import RecorderVerifier

app = typer.Typer(no_args_is_help=True)


def _settings() -> RecorderSettings:
    settings = RecorderSettings()
    configure_logging(settings.log_level)
    return settings


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
