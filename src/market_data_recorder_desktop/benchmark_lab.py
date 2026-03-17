from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import duckdb
import httpx

from market_data_recorder.storage import DuckDBStorage

from .app_types import (
    BenchmarkAudit,
    BenchmarkBar,
    BenchmarkCoverage,
    BenchmarkInstrumentType,
    BenchmarkInterval,
    BenchmarkQuote,
    MarketBenchmarkLink,
    PaperBotSession,
    PaperRunResult,
    ReferenceInstrument,
)
from .credentials import CredentialVault


BENCHMARK_ENV_VARS = ("SUPERIOR_BENCHMARK_API_KEY", "FINANCIAL_DATASETS_API_KEY")


def resolve_benchmark_api_key(
    *,
    vault: CredentialVault | None = None,
    profile_id: str | None = None,
) -> str | None:
    for env_var in BENCHMARK_ENV_VARS:
        value = os.getenv(env_var, "").strip()
        if value:
            return value
    if vault is None or profile_id is None:
        return None
    return vault.load(profile_id, "financial_benchmark").get("api_key", "").strip() or None


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        scale = 1000 if value > 10_000_000_000 else 1
        return datetime.fromtimestamp(value / scale, tz=timezone.utc)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    raise TypeError(f"Unsupported timestamp payload: {type(value)!r}")


def _to_utc(value: datetime) -> datetime:
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _naive_utc(value: datetime) -> datetime:
    return _to_utc(value).replace(tzinfo=None)


def _as_float(value: Any) -> float:
    return float(value)


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("results", "data", "prices", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, dict)]
        return [payload]
    return []


def _guess_instrument_type(value: str) -> BenchmarkInstrumentType:
    normalized = value.strip().lower()
    if normalized in {"crypto", "coin", "token"}:
        return "crypto"
    if normalized in {"stock", "equity"}:
        return "stock"
    if normalized == "etf":
        return "etf"
    if normalized == "index":
        return "index"
    if normalized == "macro":
        return "macro"
    return "unknown"


class BenchmarkProvider(ABC):
    provider_id: str
    provider_label: str

    @abstractmethod
    def search_symbol(self, query: str, *, api_key: str) -> list[ReferenceInstrument]:
        raise NotImplementedError

    @abstractmethod
    def fetch_bars(
        self,
        symbol: str,
        *,
        instrument_type: BenchmarkInstrumentType,
        start_at: datetime,
        end_at: datetime,
        interval: BenchmarkInterval,
        api_key: str,
    ) -> list[BenchmarkBar]:
        raise NotImplementedError

    @abstractmethod
    def fetch_latest_quote(
        self,
        symbol: str,
        *,
        instrument_type: BenchmarkInstrumentType,
        api_key: str,
    ) -> BenchmarkQuote | None:
        raise NotImplementedError


class FinancialDatasetsProvider(BenchmarkProvider):
    provider_id = "financial_datasets"
    provider_label = "Financial Datasets"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        base_url: str = "https://api.financialdatasets.ai",
    ) -> None:
        self._client = client or httpx.Client(timeout=20.0)
        self._base_url = base_url.rstrip("/")

    def search_symbol(self, query: str, *, api_key: str) -> list[ReferenceInstrument]:
        query = query.strip()
        if not query:
            return []
        records: list[dict[str, Any]] = []
        for path, instrument_type in (
            ("/stock-search-data", "stock"),
            ("/crypto-search-data", "crypto"),
        ):
            try:
                response = self._request(path, api_key=api_key, params={"query": query, "limit": 5})
            except httpx.HTTPError:
                continue
            records.extend(
                item | {"instrument_type": item.get("instrument_type", instrument_type)}
                for item in _records(response)
            )
        if not records and query.isascii():
            inferred = "crypto" if "-" in query or query.upper().endswith("USD") else "stock"
            return [
                ReferenceInstrument(
                    symbol=query.upper(),
                    name=query.upper(),
                    instrument_type=cast(BenchmarkInstrumentType, inferred),
                    source_provider=self.provider_id,
                )
            ]
        instruments: list[ReferenceInstrument] = []
        for item in records:
            symbol = str(item.get("symbol") or item.get("ticker") or "").upper()
            if not symbol:
                continue
            instruments.append(
                ReferenceInstrument(
                    symbol=symbol,
                    name=str(item.get("name") or symbol),
                    instrument_type=_guess_instrument_type(str(item.get("instrument_type") or "")),
                    exchange=str(item.get("exchange") or "") or None,
                    currency=str(item.get("currency") or "USD") or None,
                    source_provider=self.provider_id,
                )
            )
        return instruments

    def fetch_bars(
        self,
        symbol: str,
        *,
        instrument_type: BenchmarkInstrumentType,
        start_at: datetime,
        end_at: datetime,
        interval: BenchmarkInterval,
        api_key: str,
    ) -> list[BenchmarkBar]:
        endpoint = "/crypto-prices" if instrument_type == "crypto" else "/stock-prices"
        payload = self._request(
            endpoint,
            api_key=api_key,
            params={
                "ticker": symbol,
                "symbol": symbol,
                "interval": interval,
                "start_date": start_at.astimezone(timezone.utc).isoformat(),
                "end_date": end_at.astimezone(timezone.utc).isoformat(),
            },
        )
        bars: list[BenchmarkBar] = []
        for item in _records(payload):
            bars.append(
                BenchmarkBar(
                    symbol=symbol.upper(),
                    instrument_type=instrument_type,
                    interval=interval,
                    recorded_at=_parse_timestamp(
                        item.get("time")
                        or item.get("datetime")
                        or item.get("timestamp")
                        or item.get("date")
                    ),
                    open=_as_float(item.get("open")),
                    high=_as_float(item.get("high")),
                    low=_as_float(item.get("low")),
                    close=_as_float(item.get("close")),
                    volume=float(item["volume"]) if item.get("volume") is not None else None,
                    source_provider=self.provider_id,
                )
            )
        return sorted(bars, key=lambda item: item.recorded_at)

    def fetch_latest_quote(
        self,
        symbol: str,
        *,
        instrument_type: BenchmarkInstrumentType,
        api_key: str,
    ) -> BenchmarkQuote | None:
        payload = self._request(
            "/price-snapshot",
            api_key=api_key,
            params={"ticker": symbol, "symbol": symbol, "market": instrument_type},
        )
        rows = _records(payload)
        if not rows:
            return None
        item = rows[0]
        quoted_at = item.get("quoted_at") or item.get("time") or item.get("datetime") or datetime.now(timezone.utc)
        price = item.get("price") or item.get("last") or item.get("close")
        if price is None:
            return None
        bid = item.get("bid")
        ask = item.get("ask")
        return BenchmarkQuote(
            symbol=symbol.upper(),
            instrument_type=instrument_type,
            quoted_at=_parse_timestamp(quoted_at),
            price=float(price),
            bid=float(bid) if bid is not None else None,
            ask=float(ask) if ask is not None else None,
            source_provider=self.provider_id,
        )

    def _request(self, path: str, *, api_key: str, params: dict[str, Any]) -> Any:
        response = self._client.get(
            f"{self._base_url}{path}",
            headers={"X-API-KEY": api_key},
            params=params,
        )
        response.raise_for_status()
        return response.json()


class BenchmarkStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def upsert_instruments(self, instruments: list[ReferenceInstrument]) -> None:
        if not instruments:
            return
        connection = self._connect()
        try:
            for item in instruments:
                connection.execute("DELETE FROM benchmark_instruments WHERE symbol = ?", [item.symbol])
                connection.execute(
                    "INSERT INTO benchmark_instruments VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        item.symbol,
                        item.name,
                        item.instrument_type,
                        item.exchange,
                        item.currency,
                        item.source_provider,
                        _naive_utc(datetime.now(timezone.utc)),
                    ],
                )
        finally:
            connection.close()

    def upsert_bars(self, bars: list[BenchmarkBar]) -> None:
        if not bars:
            return
        connection = self._connect()
        try:
            for item in bars:
                connection.execute(
                    "DELETE FROM benchmark_bars WHERE symbol = ? AND interval = ? AND recorded_at = ?",
                    [item.symbol, item.interval, _naive_utc(item.recorded_at)],
                )
                connection.execute(
                    "INSERT INTO benchmark_bars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        item.symbol,
                        item.instrument_type,
                        item.interval,
                        _naive_utc(item.recorded_at),
                        item.open,
                        item.high,
                        item.low,
                        item.close,
                        item.volume,
                        item.source_provider,
                    ],
                )
        finally:
            connection.close()

    def upsert_quote(self, quote: BenchmarkQuote) -> None:
        connection = self._connect()
        try:
            connection.execute(
                "DELETE FROM benchmark_quotes WHERE symbol = ? AND quoted_at = ?",
                [quote.symbol, _naive_utc(quote.quoted_at)],
            )
            connection.execute(
                "INSERT INTO benchmark_quotes VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    quote.symbol,
                    quote.instrument_type,
                    _naive_utc(quote.quoted_at),
                    quote.price,
                    quote.bid,
                    quote.ask,
                    quote.source_provider,
                ],
            )
        finally:
            connection.close()

    def save_link(self, link: MarketBenchmarkLink) -> MarketBenchmarkLink:
        connection = self._connect()
        try:
            connection.execute(
                "DELETE FROM market_benchmark_links WHERE profile_id = ? AND market_slug = ?",
                [link.profile_id, link.market_slug],
            )
            connection.execute(
                "INSERT INTO market_benchmark_links VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    link.link_id,
                    link.profile_id,
                    link.market_slug,
                    link.market_id,
                    link.symbol,
                    link.instrument_type,
                    link.interval_preference,
                    link.mapping_confidence,
                    link.notes,
                    _naive_utc(link.created_at),
                    _naive_utc(link.updated_at),
                ],
            )
        finally:
            connection.close()
        return link

    def list_links(self, profile_id: str) -> list[MarketBenchmarkLink]:
        if not self._db_path.exists():
            return []
        connection = self._connect(read_only=True)
        try:
            rows = connection.execute(
                """
                SELECT
                  link_id,
                  profile_id,
                  market_slug,
                  market_id,
                  symbol,
                  instrument_type,
                  interval_preference,
                  mapping_confidence,
                  notes,
                  created_at,
                  updated_at
                FROM market_benchmark_links
                WHERE profile_id = ?
                ORDER BY updated_at DESC, market_slug
                """,
                [profile_id],
            ).fetchall()
        finally:
            connection.close()
        return [
            MarketBenchmarkLink(
                link_id=row[0],
                profile_id=row[1],
                market_slug=row[2],
                market_id=row[3],
                symbol=row[4],
                instrument_type=row[5],
                interval_preference=row[6],
                mapping_confidence=int(row[7]),
                notes=row[8] or "",
                created_at=_to_utc(row[9]),
                updated_at=_to_utc(row[10]),
            )
            for row in rows
        ]

    def link_for_market(self, profile_id: str, market_slug: str, market_id: str | None = None) -> MarketBenchmarkLink | None:
        for link in self.list_links(profile_id):
            if link.market_slug == market_slug:
                return link
            if market_id is not None and link.market_id == market_id:
                return link
        return None

    def bars_for_symbol(
        self,
        symbol: str,
        *,
        interval: BenchmarkInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[BenchmarkBar]:
        if not self._db_path.exists():
            return []
        connection = self._connect(read_only=True)
        try:
            rows = connection.execute(
                """
                SELECT symbol, instrument_type, interval, recorded_at, open, high, low, close, volume, source_provider
                FROM benchmark_bars
                WHERE symbol = ? AND interval = ? AND recorded_at BETWEEN ? AND ?
                ORDER BY recorded_at
                """,
                [symbol.upper(), interval, _naive_utc(start_at), _naive_utc(end_at)],
            ).fetchall()
        finally:
            connection.close()
        return [
            BenchmarkBar(
                symbol=row[0],
                instrument_type=row[1],
                interval=row[2],
                recorded_at=_to_utc(row[3]),
                open=float(row[4]),
                high=float(row[5]),
                low=float(row[6]),
                close=float(row[7]),
                volume=float(row[8]) if row[8] is not None else None,
                source_provider=row[9],
            )
            for row in rows
        ]

    def latest_quote(self, symbol: str) -> BenchmarkQuote | None:
        if not self._db_path.exists():
            return None
        connection = self._connect(read_only=True)
        try:
            row = connection.execute(
                """
                SELECT symbol, instrument_type, quoted_at, price, bid, ask, source_provider
                FROM benchmark_quotes
                WHERE symbol = ?
                ORDER BY quoted_at DESC
                LIMIT 1
                """,
                [symbol.upper()],
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return BenchmarkQuote(
            symbol=row[0],
            instrument_type=row[1],
            quoted_at=_to_utc(row[2]),
            price=float(row[3]),
            bid=float(row[4]) if row[4] is not None else None,
            ask=float(row[5]) if row[5] is not None else None,
            source_provider=row[6],
        )

    def save_audits(self, audits: list[BenchmarkAudit]) -> None:
        if not audits:
            return
        connection = self._connect()
        try:
            for audit in audits:
                connection.execute("DELETE FROM benchmark_audits WHERE audit_id = ?", [audit.audit_id])
                connection.execute(
                    """
                    INSERT INTO benchmark_audits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        audit.audit_id,
                        audit.profile_id,
                        audit.market_slug,
                        audit.run_id,
                        audit.session_id,
                        audit.symbol,
                        audit.instrument_type,
                        audit.interval_used,
                        audit.verdict,
                        audit.coverage_state,
                        audit.underlying_move_bps,
                        audit.session_edge_bps,
                        audit.edge_vs_benchmark_bps,
                        audit.stale,
                        audit.alignment_seconds,
                        audit.note,
                        _naive_utc(audit.observed_at),
                    ],
                )
        finally:
            connection.close()

    def audits_for_run(self, profile_id: str, run_id: str) -> list[BenchmarkAudit]:
        return self._fetch_audits(profile_id=profile_id, clause="run_id = ?", value=run_id)

    def audits_for_session(self, profile_id: str, session_id: str) -> list[BenchmarkAudit]:
        return self._fetch_audits(profile_id=profile_id, clause="session_id = ?", value=session_id)

    def recent_audits(self, profile_id: str, *, limit: int = 12) -> list[BenchmarkAudit]:
        if not self._db_path.exists():
            return []
        connection = self._connect(read_only=True)
        try:
            rows = connection.execute(
                """
                SELECT
                  audit_id,
                  profile_id,
                  market_slug,
                  run_id,
                  session_id,
                  symbol,
                  instrument_type,
                  interval_used,
                  verdict,
                  coverage_state,
                  underlying_move_bps,
                  session_edge_bps,
                  edge_vs_benchmark_bps,
                  stale,
                  alignment_seconds,
                  note,
                  observed_at
                FROM benchmark_audits
                WHERE profile_id = ?
                ORDER BY observed_at DESC
                LIMIT ?
                """,
                [profile_id, limit],
            ).fetchall()
        finally:
            connection.close()
        return [self._row_to_audit(row) for row in rows]

    def _fetch_audits(self, *, profile_id: str, clause: str, value: str) -> list[BenchmarkAudit]:
        if not self._db_path.exists():
            return []
        connection = self._connect(read_only=True)
        try:
            rows = connection.execute(
                f"""
                SELECT
                  audit_id,
                  profile_id,
                  market_slug,
                  run_id,
                  session_id,
                  symbol,
                  instrument_type,
                  interval_used,
                  verdict,
                  coverage_state,
                  underlying_move_bps,
                  session_edge_bps,
                  edge_vs_benchmark_bps,
                  stale,
                  alignment_seconds,
                  note,
                  observed_at
                FROM benchmark_audits
                WHERE profile_id = ? AND {clause}
                ORDER BY observed_at DESC
                """,
                [profile_id, value],
            ).fetchall()
        finally:
            connection.close()
        return [self._row_to_audit(row) for row in rows]

    @staticmethod
    def _row_to_audit(row: tuple[Any, ...]) -> BenchmarkAudit:
        return BenchmarkAudit(
            audit_id=row[0],
            profile_id=row[1],
            market_slug=row[2],
            run_id=row[3],
            session_id=row[4],
            symbol=row[5],
            instrument_type=row[6],
            interval_used=row[7],
            verdict=row[8],
            coverage_state=row[9],
            underlying_move_bps=int(row[10]),
            session_edge_bps=int(row[11]),
            edge_vs_benchmark_bps=int(row[12]),
            stale=bool(row[13]),
            alignment_seconds=int(row[14]) if row[14] is not None else None,
            note=row[15] or "",
            observed_at=_to_utc(row[16]),
        )

    def _connect(self, *, read_only: bool = False) -> duckdb.DuckDBPyConnection:
        if not read_only:
            bootstrap = DuckDBStorage(self._db_path)
            bootstrap.close()
        elif not self._db_path.exists():
            raise FileNotFoundError(self._db_path)
        return duckdb.connect(str(self._db_path), read_only=read_only)


class BenchmarkLinkService:
    def __init__(self, store: BenchmarkStore) -> None:
        self._store = store

    def save_manual_link(
        self,
        *,
        profile_id: str,
        market_slug: str,
        symbol: str,
        instrument_type: BenchmarkInstrumentType,
        interval_preference: BenchmarkInterval,
        notes: str = "",
        market_id: str | None = None,
    ) -> MarketBenchmarkLink:
        now = datetime.now(timezone.utc)
        existing = self._store.link_for_market(profile_id, market_slug, market_id)
        link = MarketBenchmarkLink(
            link_id=existing.link_id if existing is not None else str(uuid.uuid4()),
            profile_id=profile_id,
            market_slug=market_slug,
            market_id=market_id,
            symbol=symbol.upper(),
            instrument_type=instrument_type,
            interval_preference=interval_preference,
            mapping_confidence=100,
            notes=notes.strip(),
            created_at=existing.created_at if existing is not None else now,
            updated_at=now,
        )
        return self._store.save_link(link)

    def coverage_for_market(self, profile_id: str, market_slug: str) -> BenchmarkCoverage:
        link = self._store.link_for_market(profile_id, market_slug)
        if link is None:
            return BenchmarkCoverage(
                profile_id=profile_id,
                market_slug=market_slug,
                state="no_coverage",
                message="No benchmark link saved yet.",
            )
        return BenchmarkCoverage(
            profile_id=profile_id,
            market_slug=market_slug,
            state="covered",
            symbol=link.symbol,
            instrument_type=link.instrument_type,
            interval_used=link.interval_preference,
            mapping_confidence=link.mapping_confidence,
            message=f"{link.symbol} benchmark link is ready for Lab-only audit.",
        )


class BenchmarkAuditService:
    def __init__(self, store: BenchmarkStore) -> None:
        self._store = store

    def audit_session(self, profile_id: str, session: PaperBotSession, runs: list[PaperRunResult]) -> list[BenchmarkAudit]:
        audits: list[BenchmarkAudit] = []
        for run in runs:
            audits.extend(
                self._audit_run(
                    profile_id=profile_id,
                    run=run,
                    session_id=session.session_id,
                    started_at=session.started_at,
                    ended_at=session.ended_at or run.executed_at,
                )
            )
        self._store.save_audits(audits)
        return audits

    def audit_latest_run(self, profile_id: str, run: PaperRunResult) -> list[BenchmarkAudit]:
        audits = self._audit_run(
            profile_id=profile_id,
            run=run,
            session_id=None,
            started_at=None,
            ended_at=run.executed_at,
        )
        self._store.save_audits(audits)
        return audits

    def audits_for_session(self, profile_id: str, session_id: str) -> list[BenchmarkAudit]:
        return self._store.audits_for_session(profile_id, session_id)

    def recent_audits(self, profile_id: str, *, limit: int = 12) -> list[BenchmarkAudit]:
        return self._store.recent_audits(profile_id, limit=limit)

    def _audit_run(
        self,
        *,
        profile_id: str,
        run: PaperRunResult,
        session_id: str | None,
        started_at: datetime | None,
        ended_at: datetime,
    ) -> list[BenchmarkAudit]:
        if not run.positions:
            return [
                BenchmarkAudit(
                    audit_id=f"{run.run_id}:none",
                    profile_id=profile_id,
                    market_slug="unknown",
                    run_id=run.run_id,
                    session_id=session_id,
                    verdict="Not comparable",
                    coverage_state="not_applicable",
                    note="Run has no position-level market slug for benchmark comparison.",
                )
            ]
        audits: list[BenchmarkAudit] = []
        for position in run.positions:
            link = self._store.link_for_market(profile_id, position.market_slug)
            if link is None:
                audits.append(
                    BenchmarkAudit(
                        audit_id=f"{run.run_id}:{position.market_slug}:none",
                        profile_id=profile_id,
                        market_slug=position.market_slug,
                        run_id=run.run_id,
                        session_id=session_id,
                        verdict="Not comparable",
                        coverage_state="no_coverage",
                        session_edge_bps=run.realized_edge_bps or run.expected_edge_bps,
                        note="No benchmark link saved for this market slug.",
                    )
                )
                continue
            preferred = link.interval_preference
            effective_start = started_at or (
                run.executed_at - (timedelta(minutes=15) if preferred == "1m" else timedelta(days=1))
            )
            bars = self._load_window(link.symbol, preferred, effective_start, ended_at)
            fallback_used = False
            if len(bars) < 2 and preferred == "1m":
                bars = self._load_window(link.symbol, "1d", effective_start, ended_at)
                fallback_used = bool(bars)
            if len(bars) < 2:
                audits.append(
                    BenchmarkAudit(
                        audit_id=f"{run.run_id}:{position.market_slug}:{link.symbol}",
                        profile_id=profile_id,
                        market_slug=position.market_slug,
                        run_id=run.run_id,
                        session_id=session_id,
                        symbol=link.symbol,
                        instrument_type=link.instrument_type,
                        interval_used="1d" if fallback_used else preferred,
                        verdict="Not comparable",
                        coverage_state="no_coverage",
                        session_edge_bps=run.realized_edge_bps or run.expected_edge_bps,
                        note="No usable benchmark bars found for the audit window.",
                    )
                )
                continue
            start_bar = self._nearest_bar(bars, effective_start)
            end_bar = self._nearest_bar(bars, ended_at)
            alignment_seconds = abs(int((end_bar.recorded_at - ended_at).total_seconds()))
            underlying_move_bps = 0
            if start_bar.open:
                underlying_move_bps = int(round(((end_bar.close - start_bar.open) / start_bar.open) * 10_000))
            session_edge_bps = run.realized_edge_bps or run.expected_edge_bps
            stale = alignment_seconds > 600 if (fallback_used or preferred == "1m") else False
            verdict = "Aligned"
            if stale:
                verdict = "Stale benchmark"
            elif fallback_used or alignment_seconds > 180:
                verdict = "Weak coverage"
            audits.append(
                BenchmarkAudit(
                    audit_id=f"{run.run_id}:{position.market_slug}:{link.symbol}",
                    profile_id=profile_id,
                    market_slug=position.market_slug,
                    run_id=run.run_id,
                    session_id=session_id,
                    symbol=link.symbol,
                    instrument_type=link.instrument_type,
                    interval_used="1d" if fallback_used else preferred,
                    verdict=cast(Any, verdict),
                    coverage_state="covered",
                    underlying_move_bps=underlying_move_bps,
                    session_edge_bps=session_edge_bps,
                    edge_vs_benchmark_bps=session_edge_bps - abs(underlying_move_bps),
                    stale=stale,
                    alignment_seconds=alignment_seconds,
                    note=(
                        "1m bars aligned to the session window."
                        if verdict == "Aligned"
                        else "Fallback or loose timestamp alignment reduced audit confidence."
                    ),
                )
            )
        return audits

    def _load_window(
        self,
        symbol: str,
        interval: BenchmarkInterval,
        start_at: datetime,
        end_at: datetime,
    ) -> list[BenchmarkBar]:
        pad = timedelta(hours=1) if interval == "1m" else timedelta(days=5)
        return self._store.bars_for_symbol(
            symbol,
            interval=interval,
            start_at=start_at - pad,
            end_at=end_at + timedelta(minutes=1),
        )

    @staticmethod
    def _nearest_bar(bars: list[BenchmarkBar], target: datetime) -> BenchmarkBar:
        before = [bar for bar in bars if bar.recorded_at <= target]
        if before:
            return before[-1]
        return min(bars, key=lambda item: abs(item.recorded_at - target))


class BenchmarkSyncService:
    def __init__(self, provider: BenchmarkProvider, store: BenchmarkStore) -> None:
        self._provider = provider
        self._store = store

    def sync_symbol(
        self,
        *,
        symbol: str,
        instrument_type: BenchmarkInstrumentType,
        interval: BenchmarkInterval,
        start_at: datetime,
        end_at: datetime,
        api_key: str,
    ) -> dict[str, Any]:
        instruments = self._provider.search_symbol(symbol, api_key=api_key)
        bars = self._provider.fetch_bars(
            symbol,
            instrument_type=instrument_type,
            start_at=start_at,
            end_at=end_at,
            interval=interval,
            api_key=api_key,
        )
        quote = self._provider.fetch_latest_quote(symbol, instrument_type=instrument_type, api_key=api_key)
        if instruments:
            exact = [item for item in instruments if item.symbol == symbol.upper()]
            self._store.upsert_instruments(exact or instruments[:1])
        if bars:
            self._store.upsert_bars(bars)
        if quote is not None:
            self._store.upsert_quote(quote)
        return {
            "provider": self._provider.provider_label,
            "symbol": symbol.upper(),
            "interval": interval,
            "bars_synced": len(bars),
            "quote_synced": quote is not None,
            "instrument_matches": len(instruments),
        }
