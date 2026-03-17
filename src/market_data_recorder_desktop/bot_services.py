from __future__ import annotations

import json
import re
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import duckdb

from market_data_recorder.arbitrage import ArbitrageAnalyzer
from market_data_recorder.models import ArbitrageOpportunity
from market_data_recorder.storage import DuckDBStorage

from .app_types import (
    AppProfile,
    AssistantMessage,
    AssistantSession,
    BotSlot,
    CapabilityState,
    CanonicalContract,
    ConnectorLoadout,
    ContractMatch,
    CredentialStatus,
    EngineStatus,
    ExperimentalLivePlan,
    ExperimentalLiveStatus,
    LiveUnlockCheck,
    LiveUnlockChecklist,
    OpportunityCandidate,
    OpportunityEvidence,
    OpportunityExplanation,
    PaperBotDecision,
    PaperBotEvent,
    PaperBotSession,
    PaperExecutionSummary,
    PaperPosition,
    PaperRunResult,
    PortfolioCurvePoint,
    PortfolioSnapshot,
    PortfolioSummary,
    RiskPolicy,
    ScoreLedgerEntry,
    SessionGrade,
    ScoreSnapshot,
    StrategyModule,
    UnlockState,
    VenueConnection,
    VenueMarketQuote,
    default_risk_policies,
    default_strategy_modules,
)
from .credentials import CredentialVault


CONNECTOR_LABELS = {
    "polymarket": "Polymarket Connector",
    "kalshi": "Kalshi Connector",
    "coach": "Coach Link",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _parse_price(value: float | str | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        return value
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def _to_utc_datetime(value: datetime) -> datetime:
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _naive_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return _to_utc_datetime(value).replace(tzinfo=None)


class VenueAdapter(ABC):
    venue_id: str
    venue_label: str

    @abstractmethod
    def connection(self, profile: AppProfile, vault: CredentialVault) -> VenueConnection:
        raise NotImplementedError

    @abstractmethod
    def load_quotes(self, profile: AppProfile) -> list[VenueMarketQuote]:
        raise NotImplementedError


class PolymarketVenueAdapter(VenueAdapter):
    venue_id = "polymarket"
    venue_label = "Polymarket"

    def connection(self, profile: AppProfile, vault: CredentialVault) -> VenueConnection:
        enabled = "Polymarket" in profile.enabled_venues and "polymarket" in profile.equipped_connectors
        if not enabled:
            return VenueConnection(
                venue_id=self.venue_id,
                venue_label=self.venue_label,
                enabled=False,
                configured=False,
                mode="disabled",
                message="Equip the Polymarket connector to unlock recorder and scanner flow.",
            )
        credential_status = vault.status(profile.id, self.venue_id)
        db_path = profile.data_dir / "market_data.duckdb"
        if credential_status.status in {"validated", "saved"}:
            return VenueConnection(
                venue_id=self.venue_id,
                venue_label=self.venue_label,
                enabled=True,
                configured=True,
                mode="live_ready",
                message="Connector equipped. Credentials are stored locally for future live gating.",
            )
        if db_path.exists():
            return VenueConnection(
                venue_id=self.venue_id,
                venue_label=self.venue_label,
                enabled=True,
                configured=False,
                mode="paper",
                message="Connector equipped. Local recorder data is available for scanner and paper mode.",
            )
        return VenueConnection(
            venue_id=self.venue_id,
            venue_label=self.venue_label,
            enabled=True,
            configured=False,
            mode="paper",
            message="Ready to record public Polymarket books. No credentials required for the first run.",
        )

    def load_quotes(self, profile: AppProfile) -> list[VenueMarketQuote]:
        if "polymarket" not in profile.equipped_connectors:
            return []
        db_path = profile.data_dir / "market_data.duckdb"
        if not db_path.exists():
            return []
        storage = DuckDBStorage(db_path, read_only=True)
        try:
            rows = storage.fetch_latest_market_quotes()
        finally:
            storage.close()
        quotes: list[VenueMarketQuote] = []
        for row in rows:
            quotes.append(
                VenueMarketQuote(
                    venue_id=self.venue_id,
                    contract_id=str(row[0]),
                    market_id=str(row[1]),
                    question=str(row[2]),
                    slug=str(row[3]),
                    outcome=str(row[4]),
                    neg_risk=bool(row[5]),
                    fees_enabled=bool(row[6]),
                    best_bid=_parse_price(row[7]),
                    best_ask=_parse_price(row[8]),
                    recorded_at=_to_utc_datetime(row[9]) if row[9] is not None else None,
                )
            )
        return quotes


class KalshiVenueAdapter(VenueAdapter):
    venue_id = "kalshi"
    venue_label = "Kalshi"

    def connection(self, profile: AppProfile, vault: CredentialVault) -> VenueConnection:
        enabled = "Kalshi" in profile.enabled_venues and "kalshi" in profile.equipped_connectors
        if not enabled:
            return VenueConnection(
                venue_id=self.venue_id,
                venue_label=self.venue_label,
                enabled=False,
                configured=False,
                mode="disabled",
                message="Equip the Kalshi connector only when you want cross-venue comparisons.",
            )
        credential_status = vault.status(profile.id, self.venue_id)
        if credential_status.status in {"validated", "saved"}:
            return VenueConnection(
                venue_id=self.venue_id,
                venue_label=self.venue_label,
                enabled=True,
                configured=True,
                mode="configured",
                message="Connector equipped. Cross-venue scanning will stay exact-match-first.",
            )
        return VenueConnection(
            venue_id=self.venue_id,
            venue_label=self.venue_label,
            enabled=True,
            configured=False,
            mode="paper",
            message="Optional in v1. Add credentials later if you want live-ready cross-venue work.",
        )

    def load_quotes(self, profile: AppProfile) -> list[VenueMarketQuote]:
        del profile
        return []


class ContractMatcher:
    def normalize(self, quote: VenueMarketQuote) -> CanonicalContract:
        outcome = _normalize_text(quote.outcome)
        orientation = "unknown"
        if outcome in {"yes", "higher", "above"}:
            orientation = "affirmative"
        elif outcome in {"no", "lower", "below"}:
            orientation = "negative"
        return CanonicalContract(
            venue_id=quote.venue_id,
            contract_id=quote.contract_id,
            question=_normalize_text(quote.question),
            slug=_normalize_text(quote.slug),
            outcome=outcome,
            orientation=orientation,
        )

    def match(self, left: VenueMarketQuote, right: VenueMarketQuote) -> ContractMatch:
        normalized_left = self.normalize(left)
        normalized_right = self.normalize(right)
        if normalized_left.venue_id == normalized_right.venue_id:
            return ContractMatch(status="reject", reason="Cross-venue matches require two different venues.")
        if normalized_left.slug == normalized_right.slug and normalized_left.outcome != normalized_right.outcome:
            return ContractMatch(
                status="exact_match",
                reason="Slug and question align across venues with complementary outcomes.",
            )
        if normalized_left.question == normalized_right.question:
            return ContractMatch(
                status="probable_match",
                reason="Question text overlaps, but the market identity is still not exact enough.",
            )
        return ContractMatch(status="reject", reason="Contracts do not describe the same market in an exact way.")


class ConnectorLoadoutService:
    def build_loadout(self, profile: AppProfile) -> ConnectorLoadout:
        return ConnectorLoadout(
            profile_id=profile.id,
            equipped_connectors=list(profile.equipped_connectors),
            equipped_modules=list(profile.equipped_modules),
        )

    def connector_states(
        self,
        profile: AppProfile,
        connections: list[VenueConnection],
        credential_statuses: list[CredentialStatus],
    ) -> list[CapabilityState]:
        states: list[CapabilityState] = []
        connection_map = {item.venue_id: item for item in connections}
        credential_map = {item.provider_id: item for item in credential_statuses}
        for connector_id in ("polymarket", "kalshi", "coach"):
            if connector_id == "coach":
                equipped = connector_id in profile.equipped_connectors
                status = credential_map.get("coach")
                ready = bool(status and status.status == "validated")
                message = (
                    "Coach equipped and ready to explain scanner output."
                    if ready
                    else "Equip the Coach link if you want BYO-model guidance later."
                )
            else:
                connection = connection_map.get(connector_id)
                equipped = connector_id in profile.equipped_connectors
                ready = bool(connection and connection.enabled)
                message = connection.message if connection is not None else "No connector state yet."
            states.append(
                CapabilityState(
                    capability_id=connector_id,
                    label=CONNECTOR_LABELS[connector_id],
                    equipped=equipped,
                    ready=ready,
                    message=message,
                )
            )
        return states

    def module_states(self, profile: AppProfile, modules: list[StrategyModule]) -> list[CapabilityState]:
        states: list[CapabilityState] = []
        for module in modules:
            equipped = module.id in profile.equipped_modules
            ready = equipped and (module.tier == "core" or profile.lab_enabled)
            if module.tier == "lab" and not profile.lab_enabled:
                message = "Enable Lab before this module can be equipped."
            elif equipped:
                message = "Module equipped and ready for scanner or lab surfaces."
            else:
                message = "Available in loadout. Equip it when you want this strategy visible."
            states.append(
                CapabilityState(
                    capability_id=module.id,
                    label=module.label,
                    equipped=equipped,
                    ready=ready,
                    tier=module.tier,
                    message=message,
                )
            )
        return states


class CapabilityService:
    def states(
        self,
        *,
        profile: AppProfile,
        engine_status: EngineStatus,
        connections: list[VenueConnection],
        score_snapshot: ScoreSnapshot,
        checklist: LiveUnlockChecklist,
    ) -> list[CapabilityState]:
        recorder_ready = any(item.venue_id == "polymarket" and item.enabled for item in connections)
        market_db_exists = (profile.data_dir / "market_data.duckdb").exists()
        scanner_ready = market_db_exists or (
            engine_status.summary is not None and engine_status.summary.book_snapshots > 0
        )
        paper_ready = score_snapshot.total_runs > 0 or scanner_ready
        return [
            CapabilityState(
                capability_id="recorder",
                label="Recorder",
                equipped=True,
                ready=recorder_ready,
                message=(
                    "Ready to capture local Polymarket books for the first paper loop."
                    if recorder_ready
                    else "Equip Polymarket first."
                ),
            ),
            CapabilityState(
                capability_id="scanner",
                label="Scanner",
                equipped=True,
                ready=scanner_ready,
                message=(
                    "Local books are ready. Refresh scan to inspect the next route."
                    if scanner_ready
                    else "Run the recorder once so scanner explanations have local data."
                ),
            ),
            CapabilityState(
                capability_id="paper-score",
                label="Paper Score",
                equipped=True,
                ready=paper_ready,
                message=(
                    "Paper score will light up after the first paper route."
                    if not score_snapshot.total_runs
                    else "Paper score is live and reading from the local ledger."
                ),
            ),
            CapabilityState(
                capability_id="live-gate",
                label="Live Gate",
                equipped=True,
                ready=checklist.live_ready,
                message=(
                    "Micro-live gate is clear, but consumer live still stays experimental."
                    if checklist.live_ready
                    else "Live stays locked until every local rule passes."
                ),
            ),
        ]


class OpportunityEngine:
    def __init__(
        self,
        venue_adapters: Iterable[VenueAdapter],
        matcher: ContractMatcher,
        *,
        risk_policies: list[RiskPolicy] | None = None,
        strategy_modules: list[StrategyModule] | None = None,
    ) -> None:
        self._venue_adapters = {adapter.venue_id: adapter for adapter in venue_adapters}
        self._matcher = matcher
        self._risk_policies = {policy.id: policy for policy in (risk_policies or default_risk_policies())}
        self._strategy_modules = strategy_modules or default_strategy_modules()

    def strategy_modules(self) -> list[StrategyModule]:
        return list(self._strategy_modules)

    def scan(self, profile: AppProfile) -> list[OpportunityCandidate]:
        candidates: list[OpportunityCandidate] = []
        quotes_by_venue = {
            venue_id: adapter.load_quotes(profile) for venue_id, adapter in self._venue_adapters.items()
        }
        if "internal-binary" in profile.equipped_modules:
            candidates.extend(self._scan_internal_binary(profile, quotes_by_venue.get("polymarket", [])))
        if (
            "cross-venue-complement" in profile.equipped_modules
            and "kalshi" in profile.equipped_connectors
        ):
            candidates.extend(
                self._scan_cross_venue(
                    profile,
                    quotes_by_venue.get("polymarket", []),
                    quotes_by_venue.get("kalshi", []),
                )
            )
        if profile.lab_enabled and "negative-risk-basket" in profile.equipped_modules:
            candidates.extend(self._scan_lab_monitors(quotes_by_venue.get("polymarket", [])))
        return sorted(
            candidates,
            key=lambda item: (item.net_edge_bps, item.opportunity_quality_score, item.gross_edge_bps),
            reverse=True,
        )

    def _scan_internal_binary(
        self,
        profile: AppProfile,
        quotes: list[VenueMarketQuote],
    ) -> list[OpportunityCandidate]:
        grouped: dict[str, list[VenueMarketQuote]] = defaultdict(list)
        for quote in quotes:
            grouped[quote.market_id].append(quote)
        risk_policy = self._risk_policies.get(profile.risk_policy_id, default_risk_policies()[0])
        candidates: list[OpportunityCandidate] = []
        for market_quotes in grouped.values():
            if len(market_quotes) != 2:
                continue
            asks = [_parse_price(quote.best_ask) for quote in market_quotes]
            if any(price is None for price in asks):
                continue
            assert asks[0] is not None
            assert asks[1] is not None
            gross_edge = 1.0 - asks[0] - asks[1]
            gross_edge_bps = int(round(gross_edge * 10_000))
            cost_adjustments = {
                "slippage_bps": 10,
                "stale_book_bps": 5,
                "fees_bps": 8 if any(quote.fees_enabled for quote in market_quotes) else 0,
                "reject_risk_bps": 4,
            }
            net_edge_bps = gross_edge_bps - sum(cost_adjustments.values())
            question = market_quotes[0].question
            candidates.append(
                OpportunityCandidate(
                    id=str(uuid.uuid4()),
                    strategy_id="internal-binary",
                    strategy_label="Internal Binary",
                    tier="core",
                    status="candidate" if net_edge_bps > 0 else "rejected",
                    market_slug=market_quotes[0].slug,
                    summary=f"Price both sides of {question} as a full basket and keep only the net-positive setup.",
                    venues=["Polymarket"],
                    gross_edge_bps=gross_edge_bps,
                    net_edge_bps=net_edge_bps,
                    recommended_stake_cents=min(risk_policy.max_position_cents, 2_500),
                    explanation=OpportunityExplanation(
                        summary="The scanner prices the two mutually exclusive outcomes, then subtracts explicit execution drag.",
                        matched_contracts=[f"{quote.outcome}: ask {quote.best_ask}" for quote in market_quotes],
                        assumptions=[
                            "The market resolves to exactly one displayed outcome.",
                            "Top-of-book quotes are recent enough for a deterministic paper fill.",
                        ],
                        cost_adjustments_bps=cost_adjustments,
                    ),
                    evidence=OpportunityEvidence(
                        raw_edge_bps=gross_edge_bps,
                        net_edge_bps=net_edge_bps,
                        cost_adjustments_bps=cost_adjustments,
                        matched_markets=[f"{quote.market_id}:{quote.outcome}" for quote in market_quotes],
                        rationale="Internal binary dislocation only passes when the basket still clears cost deductions.",
                    ),
                    opportunity_quality_score=max(0, min(100, 55 + int(net_edge_bps / 6))),
                )
            )
        return candidates

    def _scan_cross_venue(
        self,
        profile: AppProfile,
        polymarket_quotes: list[VenueMarketQuote],
        kalshi_quotes: list[VenueMarketQuote],
    ) -> list[OpportunityCandidate]:
        risk_policy = self._risk_policies.get(profile.risk_policy_id, default_risk_policies()[0])
        if not polymarket_quotes or not kalshi_quotes:
            return []
        candidates: list[OpportunityCandidate] = []
        for left in polymarket_quotes:
            for right in kalshi_quotes:
                match = self._matcher.match(left, right)
                if match.status != "exact_match":
                    continue
                left_ask = _parse_price(left.best_ask)
                right_ask = _parse_price(right.best_ask)
                if left_ask is None or right_ask is None:
                    continue
                gross_edge_bps = int(round((1.0 - left_ask - right_ask) * 10_000))
                cost_adjustments = {
                    "slippage_bps": 16,
                    "mismatch_penalty_bps": 12,
                    "reject_risk_bps": 6,
                }
                net_edge_bps = gross_edge_bps - sum(cost_adjustments.values())
                candidates.append(
                    OpportunityCandidate(
                        id=str(uuid.uuid4()),
                        strategy_id="cross-venue-complement",
                        strategy_label="Cross-Venue Complement",
                        tier="core",
                        status="candidate" if net_edge_bps > 0 else "rejected",
                        market_slug=left.slug,
                        summary="Hold an exact-match complement pair across venues only if the net basket still clears costs.",
                        venues=[left.venue_id.title(), right.venue_id.title()],
                        gross_edge_bps=gross_edge_bps,
                        net_edge_bps=net_edge_bps,
                        recommended_stake_cents=min(risk_policy.max_position_cents, 2_000),
                        explanation=OpportunityExplanation(
                            summary=match.reason,
                            matched_contracts=[
                                f"{left.venue_id.title()}: {left.question} / {left.outcome}",
                                f"{right.venue_id.title()}: {right.question} / {right.outcome}",
                            ],
                            assumptions=["Cross-venue candidates stay exact-match-first in v1."],
                            cost_adjustments_bps=cost_adjustments,
                        ),
                        evidence=OpportunityEvidence(
                            raw_edge_bps=gross_edge_bps,
                            net_edge_bps=net_edge_bps,
                            cost_adjustments_bps=cost_adjustments,
                            matched_markets=[left.slug, right.slug],
                            rationale="Cross-venue opportunities are rejected unless equivalence is exact and net-positive.",
                        ),
                        opportunity_quality_score=max(0, min(100, 48 + int(net_edge_bps / 7))),
                    )
                )
        return candidates

    def _scan_lab_monitors(self, quotes: list[VenueMarketQuote]) -> list[OpportunityCandidate]:
        monitors: list[OpportunityCandidate] = []
        seen_market_ids: set[str] = set()
        for quote in quotes:
            if not quote.neg_risk or quote.market_id in seen_market_ids:
                continue
            seen_market_ids.add(quote.market_id)
            monitors.append(
                OpportunityCandidate(
                    id=str(uuid.uuid4()),
                    strategy_id="negative-risk-basket",
                    strategy_label="Neg Risk Lab",
                    tier="lab",
                    status="monitor",
                    market_slug=quote.slug,
                    summary=f"Neg-risk market detected for {quote.question}. Keep it in Lab and paper-only.",
                    venues=["Polymarket"],
                    gross_edge_bps=0,
                    net_edge_bps=0,
                    recommended_stake_cents=0,
                    lab_only=True,
                    explanation=OpportunityExplanation(
                        summary="The recorder found neg-risk metadata. v1 exposes this as a monitor, not a live strategy.",
                        matched_contracts=[f"{quote.outcome}: {quote.market_id}"],
                        assumptions=["Negative-risk conversion logic needs explicit graph validation before execution."],
                        cost_adjustments_bps={},
                    ),
                    evidence=OpportunityEvidence(
                        matched_markets=[quote.market_id],
                        rationale="Lab monitor only.",
                    ),
                    opportunity_quality_score=0,
                )
            )
        return monitors


class PaperRunStore:
    def __init__(self, *, state_db_path: Path | None = None) -> None:
        self._state_db_path = state_db_path

    def list_runs(self, profile: AppProfile) -> list[PaperRunResult]:
        return self.list_runs_for_profile_id(profile.id, state_db_path=self._state_path_for_profile(profile))

    def list_runs_for_profile_id(
        self,
        profile_id: str,
        *,
        state_db_path: Path | None = None,
    ) -> list[PaperRunResult]:
        connection = self._connect_for_path(state_db_path or self._state_db_path)
        try:
            rows = connection.execute(
                """
                SELECT
                  run_id,
                  profile_id,
                  executed_at,
                  strategy_ids_json,
                  candidate_ids_json,
                  status,
                  deployed_capital_cents,
                  expected_edge_bps,
                  realized_pnl_cents,
                  realized_edge_bps,
                  opportunity_quality_score,
                  notes,
                  positions_json,
                  execution_json
                FROM paper_runs
                WHERE profile_id = ?
                ORDER BY executed_at
                """,
                [profile_id],
            ).fetchall()
        finally:
            connection.close()
        runs: list[PaperRunResult] = []
        for row in rows:
            runs.append(
                PaperRunResult(
                    run_id=row[0],
                    profile_id=row[1],
                    executed_at=_to_utc_datetime(row[2]),
                    strategy_ids=list(json.loads(row[3])),
                    candidate_ids=list(json.loads(row[4])),
                    status=row[5],
                    deployed_capital_cents=int(row[6]),
                    expected_edge_bps=int(row[7]),
                    realized_pnl_cents=int(row[8]),
                    realized_edge_bps=int(row[9]),
                    opportunity_quality_score=int(row[10]),
                    notes=row[11],
                    positions=[PaperPosition.model_validate(item) for item in json.loads(row[12])],
                    execution=PaperExecutionSummary.model_validate(json.loads(row[13])),
                )
            )
        return runs

    def append_run(self, profile: AppProfile, run: PaperRunResult) -> PaperRunResult:
        connection = self._connect(profile)
        try:
            connection.execute(
                """
                INSERT INTO paper_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    run.run_id,
                    profile.id,
                    _naive_utc_datetime(run.executed_at),
                    json.dumps(run.strategy_ids),
                    json.dumps(run.candidate_ids),
                    run.status,
                    run.deployed_capital_cents,
                    run.expected_edge_bps,
                    run.realized_pnl_cents,
                    run.realized_edge_bps,
                    run.opportunity_quality_score,
                    run.notes,
                    json.dumps([item.model_dump(mode="json") for item in run.positions]),
                    json.dumps(run.execution.model_dump(mode="json")),
                ],
            )
            if run.deployed_capital_cents:
                self._append_ledger_entry(
                    connection,
                    ScoreLedgerEntry(
                        entry_id=str(uuid.uuid4()),
                        profile_id=profile.id,
                        run_id=run.run_id,
                        recorded_at=run.executed_at,
                        ledger_type="paper_stake",
                        amount_cents=-run.deployed_capital_cents,
                        label="paper_stake",
                        metadata={"status": run.status},
                    ),
                )
            self._append_ledger_entry(
                connection,
                ScoreLedgerEntry(
                    entry_id=str(uuid.uuid4()),
                    profile_id=profile.id,
                    run_id=run.run_id,
                    recorded_at=run.executed_at,
                    ledger_type="paper_pnl",
                    amount_cents=run.realized_pnl_cents,
                    label="paper_pnl",
                    metadata={"strategy": run.strategy_ids[0] if run.strategy_ids else "unknown"},
                ),
            )
        finally:
            connection.close()
        return run

    def list_sessions(self, profile: AppProfile, *, limit: int | None = None) -> list[PaperBotSession]:
        connection = self._connect(profile)
        try:
            query = """
                SELECT
                  session_id,
                  profile_id,
                  started_at,
                  ended_at,
                  state,
                  bot_slots_json,
                  decisions_json,
                  events_json,
                  run_ids_json,
                  realized_pnl_cents,
                  score_delta,
                  curve_json,
                  grade_json
                FROM bot_sessions
                WHERE profile_id = ?
                ORDER BY started_at
            """
            params: list[object] = [profile.id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            rows = connection.execute(query, params).fetchall()
        finally:
            connection.close()
        sessions: list[PaperBotSession] = []
        for row in rows:
            sessions.append(
                PaperBotSession(
                    session_id=row[0],
                    profile_id=row[1],
                    started_at=_to_utc_datetime(row[2]),
                    ended_at=_to_utc_datetime(row[3]) if row[3] is not None else None,
                    state=row[4],
                    bot_slots=[BotSlot.model_validate(item) for item in json.loads(row[5])],
                    decisions=[PaperBotDecision.model_validate(item) for item in json.loads(row[6])],
                    events=[PaperBotEvent.model_validate(item) for item in json.loads(row[7])],
                    run_ids=list(json.loads(row[8])),
                    realized_pnl_cents=int(row[9]),
                    score_delta=int(row[10]),
                    curve_points=[PortfolioCurvePoint.model_validate(item) for item in json.loads(row[11])],
                    grade=SessionGrade.model_validate(json.loads(row[12])),
                )
            )
        return sessions

    def append_session(self, profile: AppProfile, session: PaperBotSession) -> PaperBotSession:
        connection = self._connect(profile)
        try:
            connection.execute(
                """
                INSERT INTO bot_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    session.session_id,
                    profile.id,
                    _naive_utc_datetime(session.started_at),
                    _naive_utc_datetime(session.ended_at),
                    session.state,
                    json.dumps([item.model_dump(mode="json") for item in session.bot_slots]),
                    json.dumps([item.model_dump(mode="json") for item in session.decisions]),
                    json.dumps([item.model_dump(mode="json") for item in session.events]),
                    json.dumps(session.run_ids),
                    session.realized_pnl_cents,
                    session.score_delta,
                    json.dumps([item.model_dump(mode="json") for item in session.curve_points]),
                    json.dumps(session.grade.model_dump(mode="json")),
                ],
            )
        finally:
            connection.close()
        return session

    def recent_ledger(self, profile: AppProfile, *, limit: int = 12) -> list[ScoreLedgerEntry]:
        connection = self._connect(profile)
        try:
            rows = connection.execute(
                """
                SELECT entry_id, profile_id, run_id, recorded_at, ledger_type, amount_cents, label, metadata_json
                FROM score_ledger
                WHERE profile_id = ?
                ORDER BY recorded_at DESC
                LIMIT ?
                """,
                [profile.id, limit],
            ).fetchall()
        finally:
            connection.close()
        return [
            ScoreLedgerEntry(
                entry_id=row[0],
                profile_id=row[1],
                run_id=row[2],
                recorded_at=_to_utc_datetime(row[3]),
                ledger_type=row[4],
                amount_cents=int(row[5]),
                label=row[6],
                metadata=dict(json.loads(row[7])),
            )
            for row in rows
        ]

    def summary(self, profile: AppProfile) -> PortfolioSummary:
        runs = self.list_runs(profile)
        sessions = self.list_sessions(profile)
        snapshot = self.score_snapshot(profile)
        return PortfolioSummary(
            total_runs=len(runs),
            completed_runs=sum(1 for run in runs if run.status == "completed"),
            total_deployed_cents=sum(run.deployed_capital_cents for run in runs),
            total_realized_pnl_cents=sum(run.realized_pnl_cents for run in runs),
            sessions_completed=len([session for session in sessions if session.state == "complete"]),
            portfolio_score=snapshot.portfolio_score,
            available_bot_slots=snapshot.available_bot_slots,
            mastery_score=snapshot.mastery_score,
            last_session_grade=sessions[-1].grade.grade if sessions else "D",
        )

    def score_snapshot(self, profile: AppProfile) -> ScoreSnapshot:
        runs = self.list_runs(profile)
        sessions = self.list_sessions(profile)
        if not runs:
            return ScoreSnapshot(profile_id=profile.id, scoreboard_mode=profile.scoreboard_mode)
        completed = [run for run in runs if run.status == "completed"]
        paper_pnl = sum(run.realized_pnl_cents for run in completed)
        hit_rate = (
            round((sum(1 for run in completed if run.realized_pnl_cents > 0) / len(completed)) * 100, 1)
            if completed
            else 0.0
        )
        average_expected = int(round(sum(run.expected_edge_bps for run in completed) / len(completed))) if completed else 0
        average_realized = int(round(sum(run.realized_edge_bps for run in completed) / len(completed))) if completed else 0
        quality = int(round(sum(run.opportunity_quality_score for run in runs) / len(runs)))
        streak = 0
        for run in reversed(completed):
            if run.realized_pnl_cents > 0:
                streak += 1
            else:
                break
        portfolio_score = sum(self._score_delta_for_run(run) for run in completed)
        mastery_score = max(0, min(999, int(round(hit_rate * 4 + average_realized + quality))))
        available_bot_slots = 1
        if len(completed) >= 2:
            available_bot_slots += 1
        if len(completed) >= 5 and hit_rate >= 50.0:
            available_bot_slots += 1
        if available_bot_slots >= 3:
            next_unlock_label = "All v1 bot slots are unlocked."
        elif available_bot_slots == 2:
            next_unlock_label = "Reach 5 completed runs with at least 50% hit rate to unlock slot 3."
        else:
            next_unlock_label = "Complete two paper runs to unlock bot slot 2."
        return ScoreSnapshot(
            profile_id=profile.id,
            scoreboard_mode=profile.scoreboard_mode,
            paper_realized_pnl_cents=paper_pnl,
            live_realized_pnl_cents=0,
            completed_runs=len(completed),
            total_runs=len(runs),
            hit_rate=hit_rate,
            average_expected_edge_bps=average_expected,
            average_realized_edge_bps=average_realized,
            current_streak=streak,
            opportunity_quality_score=quality,
            portfolio_score=portfolio_score,
            mastery_score=mastery_score,
            available_bot_slots=available_bot_slots,
            next_unlock_label=next_unlock_label,
            last_updated_at=runs[-1].executed_at,
        )

    def _connect(self, profile: AppProfile) -> duckdb.DuckDBPyConnection:
        return self._connect_for_path(self._state_path_for_profile(profile))

    @staticmethod
    def _state_path_for_profile(profile: AppProfile) -> Path:
        return profile.data_dir / "superior_state.duckdb"

    def _connect_for_path(self, path: Path | None) -> duckdb.DuckDBPyConnection:
        if path is None:
            raise ValueError("State DB path is required.")
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(path))
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_runs (
              run_id TEXT,
              profile_id TEXT,
              executed_at TIMESTAMP,
              strategy_ids_json TEXT,
              candidate_ids_json TEXT,
              status TEXT,
              deployed_capital_cents BIGINT,
              expected_edge_bps INTEGER,
              realized_pnl_cents BIGINT,
              realized_edge_bps INTEGER,
              opportunity_quality_score INTEGER,
              notes TEXT,
              positions_json TEXT,
              execution_json TEXT
            );

            CREATE TABLE IF NOT EXISTS score_ledger (
              entry_id TEXT,
              profile_id TEXT,
              run_id TEXT,
              recorded_at TIMESTAMP,
              ledger_type TEXT,
              amount_cents BIGINT,
              label TEXT,
              metadata_json TEXT
            );

            CREATE TABLE IF NOT EXISTS bot_sessions (
              session_id TEXT,
              profile_id TEXT,
              started_at TIMESTAMP,
              ended_at TIMESTAMP,
              state TEXT,
              bot_slots_json TEXT,
              decisions_json TEXT,
              events_json TEXT,
              run_ids_json TEXT,
              realized_pnl_cents BIGINT,
              score_delta BIGINT,
              curve_json TEXT,
              grade_json TEXT
            );
            """
        )
        return connection

    @staticmethod
    def _append_ledger_entry(connection: duckdb.DuckDBPyConnection, entry: ScoreLedgerEntry) -> None:
        connection.execute(
            """
            INSERT INTO score_ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                entry.entry_id,
                entry.profile_id,
                entry.run_id,
                _naive_utc_datetime(entry.recorded_at),
                entry.ledger_type,
                entry.amount_cents,
                entry.label,
                json.dumps(entry.metadata),
            ],
        )

    @staticmethod
    def _score_delta_for_run(run: PaperRunResult) -> int:
        if run.status != "completed":
            return 0
        quality_bonus = int(round(run.opportunity_quality_score / 2))
        edge_bonus = max(run.realized_edge_bps, 0)
        pnl_bonus = max(run.realized_pnl_cents, 0)
        discipline_bonus = 12 if run.execution.fill_ratio >= 0.8 else 0
        return pnl_bonus + quality_bonus + edge_bonus + discipline_bonus


class ScoreService:
    def __init__(self, paper_store: PaperRunStore) -> None:
        self._paper_store = paper_store

    def snapshot(self, profile: AppProfile | None) -> ScoreSnapshot:
        if profile is None:
            return ScoreSnapshot()
        return self._paper_store.score_snapshot(profile)

    def ledger(self, profile: AppProfile | None, *, limit: int = 12) -> list[ScoreLedgerEntry]:
        if profile is None:
            return []
        return self._paper_store.recent_ledger(profile, limit=limit)


class PaperExecutionEngine:
    def __init__(self, paper_store: PaperRunStore, *, risk_policies: list[RiskPolicy] | None = None) -> None:
        self._paper_store = paper_store
        self._risk_policies = {policy.id: policy for policy in (risk_policies or default_risk_policies())}

    def paper_trade(self, profile: AppProfile, candidate: OpportunityCandidate) -> PaperRunResult:
        risk_policy = self._risk_policies.get(profile.risk_policy_id, default_risk_policies()[0])
        if candidate.net_edge_bps <= 0:
            run = PaperRunResult(
                run_id=str(uuid.uuid4()),
                profile_id=profile.id,
                executed_at=datetime.now(timezone.utc),
                strategy_ids=[candidate.strategy_id],
                candidate_ids=[candidate.id],
                status="skipped",
                deployed_capital_cents=0,
                expected_edge_bps=candidate.net_edge_bps,
                realized_pnl_cents=0,
                realized_edge_bps=0,
                opportunity_quality_score=candidate.opportunity_quality_score,
                notes="Candidate failed the net-edge gate and stayed out of the paper ledger.",
                execution=PaperExecutionSummary(
                    fill_ratio=0.0,
                    realized_edge_bps=0,
                    slippage_bps=0,
                    notes="Skipped because the candidate did not clear the paper gate.",
                ),
            )
            return self._paper_store.append_run(profile, run)

        deployed_capital = min(candidate.recommended_stake_cents or 1_500, risk_policy.max_position_cents)
        base_drag = sum(candidate.explanation.cost_adjustments_bps.values())
        queue_penalty = 6 if candidate.strategy_id == "internal-binary" else 10
        realized_edge_bps = max(candidate.gross_edge_bps - base_drag - queue_penalty, 0)
        fill_ratio = 1.0 if candidate.net_edge_bps >= 75 else 0.82 if candidate.net_edge_bps >= 40 else 0.65
        slippage_bps = max(candidate.gross_edge_bps - realized_edge_bps, 0)
        realized_pnl = int(round(deployed_capital * fill_ratio * realized_edge_bps / 10_000))
        run = PaperRunResult(
            run_id=str(uuid.uuid4()),
            profile_id=profile.id,
            executed_at=datetime.now(timezone.utc),
            strategy_ids=[candidate.strategy_id],
            candidate_ids=[candidate.id],
            status="completed",
            deployed_capital_cents=deployed_capital,
            expected_edge_bps=candidate.net_edge_bps,
            realized_pnl_cents=realized_pnl,
            realized_edge_bps=realized_edge_bps,
            opportunity_quality_score=candidate.opportunity_quality_score,
            notes="Deterministic paper fill using gross edge, explicit cost deductions, and a simple fill-ratio rule.",
            positions=[
                PaperPosition(
                    market_slug=candidate.market_slug,
                    strategy_id=candidate.strategy_id,
                    venue_labels=candidate.venues,
                    deployed_capital_cents=deployed_capital,
                    expected_edge_bps=candidate.net_edge_bps,
                    realized_pnl_cents=realized_pnl,
                )
            ],
            execution=PaperExecutionSummary(
                fill_ratio=fill_ratio,
                realized_edge_bps=realized_edge_bps,
                slippage_bps=slippage_bps,
                notes="Deterministic paper execution. Live order routing is not exposed in v1.",
            ),
        )
        return self._paper_store.append_run(profile, run)


class LiveExecutionEngine:
    def plan(
        self,
        profile: AppProfile,
        candidate: OpportunityCandidate,
        live_status: ExperimentalLiveStatus,
    ) -> ExperimentalLivePlan:
        if profile.live_mode == "locked":
            return ExperimentalLivePlan(
                mode="locked",
                send_orders=False,
                venue_label=profile.live_target_venue,
                strategy_id=candidate.strategy_id,
                order_style="shadow",
                max_position_cents=0,
                max_daily_cap_cents=profile.live_daily_cap_cents,
                message="Experimental live is locked. Finish the paper-first graduation steps first.",
                blockers=["Current profile is still locked."],
            )
        if candidate.strategy_id not in profile.live_allowed_strategy_ids:
            return ExperimentalLivePlan(
                mode=profile.live_mode,
                send_orders=False,
                venue_label=profile.live_target_venue,
                strategy_id=candidate.strategy_id,
                order_style="shadow" if profile.live_mode == "shadow" else "post_only",
                min_net_edge_bps=0,
                max_position_cents=profile.live_position_cap_cents,
                max_daily_cap_cents=profile.live_daily_cap_cents,
                message="This strategy is outside the current experimental live scope for the profile.",
                blockers=["Strategy is not on the live allowlist."],
            )
        if profile.live_mode == "shadow":
            return ExperimentalLivePlan(
                mode="shadow",
                send_orders=False,
                venue_label=profile.live_target_venue,
                strategy_id=candidate.strategy_id,
                order_style="shadow",
                min_net_edge_bps=max(candidate.net_edge_bps, 40),
                max_position_cents=profile.live_position_cap_cents,
                max_daily_cap_cents=profile.live_daily_cap_cents,
                message="Shadow mode records the would-be order plan locally and sends nothing.",
            )
        order_style = "post_only" if candidate.net_edge_bps < 150 else "post_only_or_taker"
        min_edge = 75 if profile.live_mode == "micro" else 60
        blockers: list[str] = []
        if candidate.net_edge_bps < min_edge:
            blockers.append(f"Net edge {candidate.net_edge_bps} bps is below the {min_edge} bps gate for {profile.live_mode}.")
        return ExperimentalLivePlan(
            mode=profile.live_mode,
            send_orders=not blockers,
            venue_label=profile.live_target_venue,
            strategy_id=candidate.strategy_id,
            order_style=order_style,
            min_net_edge_bps=min_edge,
            max_position_cents=profile.live_position_cap_cents,
            max_daily_cap_cents=profile.live_daily_cap_cents,
            message=(
                "Experimental live stays deterministic: post-only first, tiny caps, and strict kill switches."
                if not blockers
                else "Candidate blocked by the current experimental-live rule set."
            ),
            blockers=blockers,
        )

    def preview(
        self,
        profile: AppProfile,
        candidate: OpportunityCandidate,
        live_status: ExperimentalLiveStatus,
    ) -> str:
        plan = self.plan(profile, candidate, live_status)
        lines = [
            f"Mode: {plan.mode}",
            f"Venue: {plan.venue_label}",
            f"Strategy: {plan.strategy_id}",
            f"Order style: {plan.order_style}",
            f"Min net edge gate: {plan.min_net_edge_bps} bps",
            f"Position cap: ${plan.max_position_cents / 100:.2f}",
            f"Daily cap: ${plan.max_daily_cap_cents / 100:.2f}",
            f"Would send live orders: {'yes' if plan.send_orders else 'no'}",
            "",
            plan.message,
        ]
        if plan.blockers:
            lines.extend(["", "Blockers:"])
            lines.extend(f"- {blocker}" for blocker in plan.blockers)
        return "\n".join(lines)


class UnlockService:
    def __init__(self, paper_store: PaperRunStore, *, risk_policies: list[RiskPolicy] | None = None) -> None:
        self._paper_store = paper_store
        self._risk_policies = {policy.id: policy for policy in (risk_policies or default_risk_policies())}

    def checklist(
        self,
        profile: AppProfile,
        *,
        venue_connections: list[VenueConnection],
        engine_status: EngineStatus,
        credential_statuses: list[CredentialStatus],
    ) -> LiveUnlockChecklist:
        completed_runs = self._paper_store.summary(profile).completed_runs
        has_valid_credentials = any(
            item.provider_id in {"polymarket", "kalshi"} and item.status == "validated"
            for item in credential_statuses
        )
        risk_policy_ready = profile.risk_policy_id in self._risk_policies
        checks = [
            LiveUnlockCheck(
                id="credentials",
                label="Connector credentials",
                passed=has_valid_credentials,
                message="Store at least one validated venue credential set before any live path appears.",
            ),
            LiveUnlockCheck(
                id="rules",
                label="Live rules accepted",
                passed=profile.live_rules_accepted,
                message="Acknowledge the non-guarantee warning and venue rules.",
            ),
            LiveUnlockCheck(
                id="risk",
                label="Risk policy acknowledged",
                passed=risk_policy_ready and profile.risk_limits_acknowledged,
                message="Choose a risk preset and confirm that you understand the daily loss cap.",
            ),
            LiveUnlockCheck(
                id="paper",
                label="Paper score earned",
                passed=completed_runs > 0,
                message="Complete at least one paper run before live gate can ever clear.",
            ),
            LiveUnlockCheck(
                id="diagnostics",
                label="Diagnostics clear",
                passed=engine_status.summary is None or engine_status.summary.latest_warning is None,
                message="Resolve stale-book or verification warnings first.",
            ),
            LiveUnlockCheck(
                id="venue",
                label="Connector ready",
                passed=any(connection.mode in {"configured", "live_ready"} for connection in venue_connections),
                message="At least one equipped venue connector must be configured beyond paper-only mode.",
            ),
        ]
        return LiveUnlockChecklist(checks=checks, live_ready=all(check.passed for check in checks))


class ExperimentalLiveService:
    _mode_order = ["locked", "shadow", "micro", "experimental"]

    def status(
        self,
        profile: AppProfile,
        *,
        score_snapshot: ScoreSnapshot,
        engine_status: EngineStatus,
        venue_connections: list[VenueConnection],
        credential_statuses: list[CredentialStatus],
        checklist: LiveUnlockChecklist,
    ) -> ExperimentalLiveStatus:
        diagnostics_clear = engine_status.summary is None or engine_status.summary.latest_warning is None
        paper_gate_passed = (
            score_snapshot.completed_runs >= 1
            and score_snapshot.total_runs >= 1
            and score_snapshot.average_realized_edge_bps >= 0
            and diagnostics_clear
        )
        validated_polymarket = any(
            status.provider_id == "polymarket" and status.status == "validated"
            for status in credential_statuses
        )
        polymarket_ready = any(
            connection.venue_id == "polymarket" and connection.mode in {"configured", "live_ready"}
            for connection in venue_connections
        )
        shadow_ready = paper_gate_passed and profile.live_rules_accepted and profile.risk_limits_acknowledged
        micro_ready = shadow_ready and validated_polymarket and polymarket_ready and checklist.live_ready
        experimental_ready = micro_ready and score_snapshot.completed_runs >= 3 and diagnostics_clear

        available_modes = ["locked"]
        if shadow_ready:
            available_modes.append("shadow")
        if micro_ready:
            available_modes.append("micro")
        if experimental_ready:
            available_modes.append("experimental")

        recommended_mode = "locked"
        if experimental_ready:
            recommended_mode = "experimental"
        elif micro_ready:
            recommended_mode = "micro"
        elif shadow_ready:
            recommended_mode = "shadow"

        warnings: list[str] = []
        if not diagnostics_clear:
            warnings.append("Diagnostics must stay clear before any experimental live stage is armed.")
        if profile.live_target_venue != "Polymarket":
            warnings.append("Experimental live stays Polymarket-first in v1.")
        if any(strategy_id not in {"internal-binary", "cross-venue-complement"} for strategy_id in profile.live_allowed_strategy_ids):
            warnings.append("Only core strategies belong in experimental live v1.")

        notes = [
            "Shadow mode writes would-be live decisions locally and never sends an order.",
            "Micro-live is Polymarket-first with tiny caps and post-only preference.",
            "Experimental live remains deterministic and separate from paper score.",
        ]
        if "micro" not in available_modes:
            notes.append("Micro-live still requires validated Polymarket credentials and a clean live checklist.")
        if "experimental" not in available_modes:
            notes.append("Experimental live only appears after repeated paper runs, not after one lucky score.")

        return ExperimentalLiveStatus(
            current_mode=profile.live_mode,
            recommended_mode=recommended_mode,
            paper_gate_passed=paper_gate_passed,
            available_modes=available_modes,
            venue_scope=[profile.live_target_venue],
            strategy_scope=list(profile.live_allowed_strategy_ids),
            position_cap_cents=profile.live_position_cap_cents,
            daily_cap_cents=profile.live_daily_cap_cents,
            warnings=warnings,
            notes=notes,
        )

    def can_promote(self, status: ExperimentalLiveStatus, target_mode: str) -> bool:
        return target_mode in status.available_modes

    def promote(self, profile: AppProfile, *, status: ExperimentalLiveStatus, target_mode: str) -> AppProfile:
        if target_mode not in self._mode_order:
            raise ValueError(f"Unsupported live mode: {target_mode}")
        if target_mode != "locked" and target_mode not in status.available_modes:
            raise ValueError(f"{target_mode} is still blocked for this profile.")
        paper_gate_passed_at = profile.paper_gate_passed_at
        if status.paper_gate_passed and paper_gate_passed_at is None:
            paper_gate_passed_at = datetime.now(timezone.utc)
        return profile.model_copy(
            update={
                "experimental_live_enabled": target_mode != "locked",
                "live_mode": target_mode,
                "live_unlocked": target_mode in {"micro", "experimental"},
                "paper_gate_passed": status.paper_gate_passed,
                "paper_gate_passed_at": paper_gate_passed_at,
            }
        )


class AssistantService:
    def __init__(self, docs_paths: Iterable[Path] | None = None) -> None:
        self._docs_paths = [path for path in (docs_paths or []) if path.exists()]

    def answer(
        self,
        *,
        question: str,
        profile: AppProfile | None,
        candidates: list[OpportunityCandidate],
        checklist: LiveUnlockChecklist | None,
        portfolio_summary: PortfolioSummary | None,
        remote_configured: bool,
    ) -> AssistantSession:
        lowered = question.lower()
        sources = self._collect_sources(lowered)
        response = self._build_response(
            lowered=lowered,
            profile=profile,
            candidates=candidates,
            checklist=checklist,
            portfolio_summary=portfolio_summary,
            remote_configured=remote_configured,
            sources=sources,
        )
        now = datetime.now(timezone.utc)
        return AssistantSession(
            session_id=str(uuid.uuid4()),
            profile_id=profile.id if profile is not None else None,
            created_at=now,
            last_updated_at=now,
            remote_configured=remote_configured,
            sources=sources,
            messages=[
                AssistantMessage(role="user", content=question.strip()),
                AssistantMessage(role="assistant", content=response),
            ],
        )

    def _build_response(
        self,
        *,
        lowered: str,
        profile: AppProfile | None,
        candidates: list[OpportunityCandidate],
        checklist: LiveUnlockChecklist | None,
        portfolio_summary: PortfolioSummary | None,
        remote_configured: bool,
        sources: list[str],
    ) -> str:
        preface = "Coach mode only. Superior keeps execution deterministic and outside the assistant."
        if "loadout" in lowered or "equip" in lowered or "connector" in lowered:
            if profile is None:
                return f"{preface}\n\nNo profile is active yet. Create one, then equip Polymarket first."
            connectors = ", ".join(profile.equipped_connectors) or "none"
            modules = ", ".join(profile.equipped_modules) or "none"
            return (
                f"{preface}\n\nCurrent loadout:\n"
                f"- Connectors: {connectors}\n"
                f"- Modules: {modules}\n"
                f"- Primary mission: {profile.primary_mission}"
            )
        if "unlock" in lowered or "live" in lowered:
            if checklist is None:
                return f"{preface}\n\nNo profile is active, so there is no live-gate checklist to review yet."
            if checklist.live_ready:
                return (
                    f"{preface}\n\nThis profile satisfies the current local live gate. "
                    "The next step is shadow or micro-live under the experimental rollout, not broad consumer live trading."
                )
            missing = "\n".join(f"- {item.label}: {item.message}" for item in checklist.outstanding)
            return f"{preface}\n\nLive gate is still closed. Finish these items first:\n{missing}"
        if "reject" in lowered or "opportunity" in lowered or "scanner" in lowered:
            if not candidates:
                return (
                    f"{preface}\n\nThe scanner has no current candidates. Record local books first, then refresh the scanner."
                )
            top = candidates[0]
            return (
                f"{preface}\n\nTop scanner result: {top.strategy_label}\n"
                f"- Summary: {top.summary}\n"
                f"- Raw edge: {top.evidence.raw_edge_bps} bps\n"
                f"- Net edge: {top.evidence.net_edge_bps} bps\n"
                f"- Why it qualifies: {top.explanation.summary}"
            )
        if "score" in lowered or "paper" in lowered or "portfolio" in lowered:
            if portfolio_summary is None:
                return f"{preface}\n\nNo paper-score history is loaded yet."
            return (
                f"{preface}\n\nPaper score summary:\n"
                f"- Total runs: {portfolio_summary.total_runs}\n"
                f"- Completed runs: {portfolio_summary.completed_runs}\n"
                f"- Realized paper PnL: ${portfolio_summary.total_realized_pnl_cents / 100:.2f}"
            )
        if "risk" in lowered:
            if profile is None:
                return f"{preface}\n\nChoose a profile first so the coach can explain the active risk preset."
            return (
                f"{preface}\n\nActive profile: {profile.display_name}\n"
                f"- Risk preset: {profile.risk_policy_id}\n"
                f"- Guided mode: {'on' if profile.guided_mode else 'off'}\n"
                f"- Lab enabled: {'yes' if profile.lab_enabled else 'no'}"
            )
        source_text = ", ".join(sources) if sources else "local profile state and bundled docs"
        remote_hint = (
            "A BYO model key is configured for richer coaching later."
            if remote_configured
            else "No BYO model key is configured, so this answer stays local-first."
        )
        return (
            f"{preface}\n\nSuperior is built to teach, record, scan, and paper before any live path is considered.\n"
            f"{remote_hint}\n"
            f"Answer source: {source_text}."
        )

    def _collect_sources(self, lowered: str) -> list[str]:
        sources: list[str] = []
        keywords = [word for word in lowered.split() if len(word) > 3]
        for path in self._docs_paths:
            text = path.read_text(encoding="utf-8").lower()
            if any(keyword in text for keyword in keywords):
                sources.append(path.name)
        return sources[:4]


class ArbitrageService:
    """Read-only service that surfaces guaranteed arbitrage opportunities from a recorded DuckDB file."""

    def find_opportunities(
        self,
        profile: AppProfile,
        *,
        min_edge: str = "0",
    ) -> list[ArbitrageOpportunity]:
        db_path = profile.data_dir / "market_data.duckdb"
        if not db_path.exists():
            return []
        storage = DuckDBStorage(db_path, read_only=True)
        try:
            return ArbitrageAnalyzer(storage).find_opportunities(min_edge=min_edge)
        finally:
            storage.close()

