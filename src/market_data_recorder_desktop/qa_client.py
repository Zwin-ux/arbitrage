from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Literal, Sequence

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from pydantic import BaseModel, Field

from market_data_recorder.config import RecorderSettings
from market_data_recorder.models import (
    BestBidAskEvent,
    DiscoveredMarket,
    PolymarketEvent,
    PolymarketMarket,
)
from market_data_recorder.storage import DuckDBStorage

from . import __version__
from .app_types import AppProfile, BenchmarkBar, EngineStatus, OpportunityCandidate, PortfolioSummary
from .benchmark_lab import BenchmarkAuditService, BenchmarkLinkService, BenchmarkStore
from .bot_services import (
    AssistantService,
    CapabilityService,
    ConnectorLoadoutService,
    ContractMatcher,
    ExperimentalLiveService,
    KalshiVenueAdapter,
    OpportunityEngine,
    PaperExecutionEngine,
    PaperRunStore,
    PolymarketVenueAdapter,
    ScoreService,
    UnlockService,
    VenueAdapter,
)
from .controller import EngineController
from .credentials import CredentialVault
from .main import _apply_style
from .paths import AppPaths
from .profiles import ProfileStore
from .score_attack import (
    BotConfigService,
    PaperSimulationEngine,
    PortfolioEngine,
    ProgressionService,
    SessionEventStore,
    UnlockTrackService,
)


QAStatus = Literal["pending", "passed", "failed"]
ScenarioRunner = Callable[["QASandbox"], "QAScenarioOutcome"]


class QAScenarioOutcome(BaseModel):
    summary: str
    evidence: list[str] = Field(default_factory=list)
    artifacts: list[Path] = Field(default_factory=list)


class QAScenarioResult(BaseModel):
    id: str
    title: str
    category: str
    status: QAStatus = "pending"
    duration_ms: int = 0
    summary: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class QASuiteReport(BaseModel):
    generated_at: datetime
    workspace: Path
    product_version: str
    python_version: str
    platform: str
    passed: int = 0
    failed: int = 0
    scenarios: list[QAScenarioResult] = Field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.scenarios)


@dataclass(frozen=True)
class QAScenarioDefinition:
    id: str
    title: str
    category: str
    acceptance_criteria: tuple[str, ...]
    runner: ScenarioRunner


class InMemoryKeyring:
    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.store.get((service_name, username))

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.store[(service_name, username)] = password

    def delete_password(self, service_name: str, username: str) -> None:
        self.store.pop((service_name, username), None)


@dataclass
class QASandbox:
    workspace: Path
    scenario_id: str
    app_paths: AppPaths
    profile_store: ProfileStore
    credential_vault: CredentialVault
    keyring: InMemoryKeyring
    venue_adapters: list[VenueAdapter]
    loadout_service: ConnectorLoadoutService
    capability_service: CapabilityService
    opportunity_engine: OpportunityEngine
    paper_store: PaperRunStore
    score_service: ScoreService
    paper_execution_engine: PaperExecutionEngine
    bot_config_service: BotConfigService
    session_store: SessionEventStore
    paper_simulation_engine: PaperSimulationEngine
    portfolio_engine: PortfolioEngine
    progression_service: ProgressionService
    unlock_track_service: UnlockTrackService
    unlock_service: UnlockService
    assistant_service: AssistantService

    @classmethod
    def create(cls, suite_workspace: Path, scenario_id: str) -> "QASandbox":
        scenario_workspace = suite_workspace / scenario_id
        shutil.rmtree(scenario_workspace, ignore_errors=True)
        app_paths = AppPaths(
            config_dir=scenario_workspace / "config",
            data_dir=scenario_workspace / "data",
            log_dir=scenario_workspace / "logs",
            exports_dir=scenario_workspace / "exports",
            profiles_path=scenario_workspace / "config" / "profiles.json",
        )
        keyring = InMemoryKeyring()
        credential_vault = CredentialVault(
            service_name=f"superior-qa-{scenario_id}",
            backend=keyring,
        )
        venue_adapters: list[VenueAdapter] = [PolymarketVenueAdapter(), KalshiVenueAdapter()]
        paper_store = PaperRunStore()
        bot_config_service = BotConfigService()
        session_store = SessionEventStore(paper_store)
        unlock_track_service = UnlockTrackService()
        return cls(
            workspace=scenario_workspace,
            scenario_id=scenario_id,
            app_paths=app_paths,
            profile_store=ProfileStore(app_paths),
            credential_vault=credential_vault,
            keyring=keyring,
            venue_adapters=venue_adapters,
            loadout_service=ConnectorLoadoutService(),
            capability_service=CapabilityService(),
            opportunity_engine=OpportunityEngine(venue_adapters, ContractMatcher()),
            paper_store=paper_store,
            score_service=ScoreService(paper_store),
            paper_execution_engine=PaperExecutionEngine(paper_store),
            bot_config_service=bot_config_service,
            session_store=session_store,
            paper_simulation_engine=PaperSimulationEngine(
                paper_store=paper_store,
                paper_execution_engine=PaperExecutionEngine(paper_store),
                bot_config_service=bot_config_service,
                session_store=session_store,
            ),
            portfolio_engine=PortfolioEngine(paper_store, bot_config_service, unlock_track_service),
            progression_service=ProgressionService(),
            unlock_track_service=unlock_track_service,
            unlock_service=UnlockService(paper_store),
            assistant_service=AssistantService(docs_paths=_qa_docs_paths()),
        )

    def create_profile(
        self,
        *,
        display_name: str,
        enabled_venues: list[str] | None = None,
        ai_coach_enabled: bool = False,
        live_rules_accepted: bool = False,
        risk_limits_acknowledged: bool = False,
        lab_enabled: bool = False,
    ) -> AppProfile:
        return self.profile_store.create_profile(
            display_name=display_name,
            template="Guided",
            enabled_venues=enabled_venues or ["Polymarket"],
            ai_coach_enabled=ai_coach_enabled,
            live_rules_accepted=live_rules_accepted,
            risk_limits_acknowledged=risk_limits_acknowledged,
            lab_enabled=lab_enabled,
            primary_goal="learn_and_scan",
        )

    def seed_internal_binary_fixture(
        self,
        profile: AppProfile,
        *,
        question: str = "Will QA fixture resolve higher than expected?",
        slug: str = "qa-fixture-market",
        market_id: str = "qa-market-1",
        yes_asset_id: str = "qa-yes-1",
        no_asset_id: str = "qa-no-1",
        yes_ask: str = "0.47",
        no_ask: str = "0.48",
        fees_enabled: bool = False,
    ) -> Path:
        db_path = profile.data_dir / "market_data.duckdb"
        storage = DuckDBStorage(db_path)
        try:
            market = PolymarketMarket.model_validate(
                {
                    "id": market_id,
                    "conditionId": f"{market_id}-condition",
                    "question": question,
                    "slug": slug,
                    "active": True,
                    "enableOrderBook": True,
                    "feesEnabled": fees_enabled,
                    "outcomes": json.dumps(["Yes", "No"]),
                    "clobTokenIds": json.dumps([yes_asset_id, no_asset_id]),
                }
            )
            event = PolymarketEvent.model_validate(
                {
                    "id": f"{market_id}-event",
                    "title": "QA Fixture Event",
                    "active": True,
                    "slug": slug,
                }
            )
            storage.store_discovery_snapshot([DiscoveredMarket(event=event, market=market)])
            storage.store_best_bid_ask(
                BestBidAskEvent(
                    event_type="best_bid_ask",
                    asset_id=yes_asset_id,
                    market=market_id,
                    best_bid="0.46",
                    best_ask=yes_ask,
                    spread="0.01",
                    timestamp="1",
                )
            )
            storage.store_best_bid_ask(
                BestBidAskEvent(
                    event_type="best_bid_ask",
                    asset_id=no_asset_id,
                    market=market_id,
                    best_bid="0.47",
                    best_ask=no_ask,
                    spread="0.01",
                    timestamp="2",
                )
            )
        finally:
            storage.close()
        return db_path

    def write_json_artifact(self, filename: str, payload: BaseModel | dict[str, object] | list[object]) -> Path:
        path = self.app_paths.exports_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, BaseModel):
            text = payload.model_dump_json(indent=2)
        else:
            text = json.dumps(payload, indent=2, default=str)
        path.write_text(text, encoding="utf-8")
        return path

    def write_text_artifact(self, filename: str, text: str) -> Path:
        path = self.app_paths.exports_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


def _qa_docs_paths() -> list[Path]:
    root = Path(__file__).resolve().parents[2]
    return [
        root / "README.md",
        root / "docs" / "risk-model.md",
        root / "docs" / "live-trading-limitations.md",
        root / "docs" / "privacy-and-secrets.md",
        root / "docs" / "strategy-contributor-guide.md",
        root / "docs" / "testing.md",
    ]


def _artifact_ref(base_workspace: Path, path: Path) -> str:
    try:
        return str(path.relative_to(base_workspace))
    except ValueError:
        return str(path)


def _wait_until(predicate: Callable[[], bool], *, timeout_seconds: float, step_seconds: float = 0.02) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(step_seconds)
    raise AssertionError("Timed out waiting for QA condition.")


def _top_candidate(candidates: Sequence[OpportunityCandidate]) -> OpportunityCandidate:
    positive = [candidate for candidate in candidates if candidate.net_edge_bps > 0]
    if not positive:
        raise AssertionError("Expected at least one positive scanner candidate.")
    return positive[0]


def _guided_profile_bootstrap(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Guided Beginner")
    save_result = sandbox.credential_vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "qa-polymarket-key",
            "api_secret": "qa-polymarket-secret",
            "api_passphrase": "qa-polymarket-passphrase",
        },
    )
    persisted = sandbox.profile_store.get_profile(profile.id)
    if persisted is None:
        raise AssertionError("Profile store did not return the created profile.")
    profiles_text = sandbox.app_paths.profiles_path.read_text(encoding="utf-8")
    if "qa-polymarket-secret" in profiles_text:
        raise AssertionError("Credential secret leaked into profiles.json.")
    if persisted.brand_name != "Superior":
        raise AssertionError("Profile did not retain Superior branding.")
    if "polymarket" not in persisted.equipped_connectors:
        raise AssertionError("Expected Polymarket to be equipped by default.")
    artifact = sandbox.write_json_artifact("bootstrap-profile.json", persisted)
    return QAScenarioOutcome(
        summary="Guided profile creation keeps Superior defaults intact and stores credentials only in the keychain.",
        evidence=[
            f"Profile brand: {persisted.brand_name}",
            f"Default mission: {persisted.primary_mission}",
            f"Equipped connectors: {', '.join(persisted.equipped_connectors)}",
            f"Credential save status: {save_result.status}",
            "profiles.json inspected with no plaintext secret leakage.",
        ],
        artifacts=[sandbox.app_paths.profiles_path, artifact],
    )


def _loadout_capability_baseline(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Loadout Baseline")
    connections = [adapter.connection(profile, sandbox.credential_vault) for adapter in sandbox.venue_adapters]
    credential_statuses = sandbox.credential_vault.statuses_for_profile(profile.id)
    score_snapshot = sandbox.score_service.snapshot(profile)
    checklist = sandbox.unlock_service.checklist(
        profile,
        venue_connections=connections,
        engine_status=EngineStatus(),
        credential_statuses=credential_statuses,
    )
    capability_states = sandbox.capability_service.states(
        profile=profile,
        engine_status=EngineStatus(),
        connections=connections,
        score_snapshot=score_snapshot,
        checklist=checklist,
    )
    states_by_id = {state.capability_id: state for state in capability_states}
    if not states_by_id["recorder"].ready:
        raise AssertionError("Recorder should be ready once Polymarket is equipped.")
    if states_by_id["scanner"].ready:
        raise AssertionError("Scanner should stay blocked before market data exists.")
    if states_by_id["paper-score"].ready:
        raise AssertionError("Paper score should stay blocked before the first run.")
    if checklist.live_ready:
        raise AssertionError("Live gate should not clear for a baseline profile.")
    artifact = sandbox.write_json_artifact(
        "capability-baseline.json",
        {
            "connections": [item.model_dump(mode="json") for item in connections],
            "credential_statuses": [item.model_dump(mode="json") for item in credential_statuses],
            "capabilities": [item.model_dump(mode="json") for item in capability_states],
            "checklist": checklist.model_dump(mode="json"),
        },
    )
    return QAScenarioOutcome(
        summary="The baseline loadout exposes recorder readiness while keeping scanner, score, and live gating blocked until the user earns them.",
        evidence=[
            f"Recorder state: {states_by_id['recorder'].message}",
            f"Scanner state: {states_by_id['scanner'].message}",
            f"Paper score state: {states_by_id['paper-score'].message}",
            f"Live-gate blockers: {', '.join(check.id for check in checklist.outstanding)}",
        ],
        artifacts=[artifact],
    )


def _scanner_fixture_detects_edge(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Scanner Fixture")
    db_path = sandbox.seed_internal_binary_fixture(profile)
    candidates = sandbox.opportunity_engine.scan(profile)
    candidate = _top_candidate(candidates)
    artifact = sandbox.write_json_artifact("top-candidate.json", candidate)
    return QAScenarioOutcome(
        summary="The scanner surfaces a net-positive internal-binary candidate from deterministic local Polymarket fixture data.",
        evidence=[
            f"Strategy: {candidate.strategy_label}",
            f"Gross edge: {candidate.gross_edge_bps} bps",
            f"Net edge: {candidate.net_edge_bps} bps",
            f"Opportunity quality: {candidate.opportunity_quality_score}",
            f"Explanation: {candidate.explanation.summary}",
        ],
        artifacts=[db_path, artifact],
    )


def _paper_score_ledger_updates(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Paper Score")
    sandbox.seed_internal_binary_fixture(profile)
    candidate = _top_candidate(sandbox.opportunity_engine.scan(profile))
    run = sandbox.paper_execution_engine.paper_trade(profile, candidate)
    snapshot = sandbox.score_service.snapshot(profile)
    ledger = sandbox.score_service.ledger(profile)
    if run.status != "completed":
        raise AssertionError("Expected the paper run to complete.")
    if snapshot.completed_runs != 1:
        raise AssertionError("Paper score did not register the completed run.")
    if snapshot.paper_realized_pnl_cents != run.realized_pnl_cents:
        raise AssertionError("Paper score PnL does not match the stored run.")
    ledger_types = {entry.ledger_type for entry in ledger}
    if {"paper_stake", "paper_pnl"} - ledger_types:
        raise AssertionError("Ledger is missing stake or PnL entries.")
    run_artifact = sandbox.write_json_artifact("paper-run.json", run)
    score_artifact = sandbox.write_json_artifact("paper-score.json", snapshot)
    return QAScenarioOutcome(
        summary="A completed paper run updates the local score ledger with stake and realized PnL, and the score board reads from that ledger.",
        evidence=[
            f"Run ID: {run.run_id}",
            f"Deployed capital: {run.deployed_capital_cents} cents",
            f"Realized paper PnL: {run.realized_pnl_cents} cents",
            f"Average realized edge: {snapshot.average_realized_edge_bps} bps",
            f"Ledger entries captured: {len(ledger)}",
        ],
        artifacts=[run_artifact, score_artifact, profile.data_dir / "superior_state.duckdb"],
    )


def _first_paper_loop_without_credentials(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA First Paper Loop")
    if sandbox.credential_vault.status(profile.id, "polymarket").status != "missing":
        raise AssertionError("The first paper loop should begin with no Polymarket credentials stored.")
    sandbox.seed_internal_binary_fixture(profile)
    candidates = sandbox.opportunity_engine.scan(profile)
    candidate = _top_candidate(candidates)
    run = sandbox.paper_execution_engine.paper_trade(profile, candidate)
    snapshot = sandbox.score_service.snapshot(profile)
    if run.status != "completed":
        raise AssertionError("Expected the first paper loop to end with a completed paper run.")
    if snapshot.completed_runs < 1:
        raise AssertionError("Expected the paper score to update after the first paper loop.")
    artifact = sandbox.write_json_artifact(
        "first-paper-loop.json",
        {
            "profile": profile.model_dump(mode="json"),
            "candidate": candidate.model_dump(mode="json"),
            "run": run.model_dump(mode="json"),
            "score": snapshot.model_dump(mode="json"),
        },
    )
    return QAScenarioOutcome(
        summary="A new user can finish the first paper loop with Polymarket equipped, no keys stored, one scanner route, and one score update.",
        evidence=[
            f"Mission: {profile.primary_mission}",
            "Polymarket credentials remained empty for the whole scenario.",
            f"Net edge cleared at {candidate.net_edge_bps} bps before paper execution.",
            f"Paper score after run: ${snapshot.paper_realized_pnl_cents / 100:.2f}",
        ],
        artifacts=[artifact, profile.data_dir / "market_data.duckdb", profile.data_dir / "superior_state.duckdb"],
    )


def _starter_bot_session_banks_score(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Starter Session")
    sandbox.seed_internal_binary_fixture(profile)
    candidates = sandbox.opportunity_engine.scan(profile)
    session = sandbox.paper_simulation_engine.run_session(
        profile,
        candidates,
        score_snapshot=sandbox.score_service.snapshot(profile),
    )
    portfolio = sandbox.portfolio_engine.snapshot(profile)
    if session.state != "complete":
        raise AssertionError("Expected the starter session to complete.")
    if session.score_delta <= 0:
        raise AssertionError("Expected the starter session to bank positive score.")
    artifact = sandbox.write_json_artifact(
        "starter-session.json",
        {
            "session": session.model_dump(mode="json"),
            "portfolio": portfolio.model_dump(mode="json"),
        },
    )
    return QAScenarioOutcome(
        summary="A starter bot session stages a route, banks paper score, and updates the portfolio snapshot without any live credentials.",
        evidence=[
            f"Session grade: {session.grade.grade}",
            f"Session score delta: {session.score_delta}",
            f"Portfolio score: {portfolio.portfolio_score}",
            f"Available bot slots: {portfolio.available_bot_slots}",
        ],
        artifacts=[artifact, profile.data_dir / "superior_state.duckdb"],
    )


def _benchmark_audit_marks_session_with_external_reference(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Benchmark Audit", lab_enabled=True)
    sandbox.credential_vault.save(
        profile.id,
        "financial_benchmark",
        {"provider_name": "Financial Datasets", "api_key": "qa-benchmark-key"},
    )
    sandbox.seed_internal_binary_fixture(
        profile,
        question="Will SPY close above the benchmark line?",
        slug="spy-close-benchmark",
        market_id="spy-market-1",
    )
    benchmark_store = BenchmarkStore(profile.data_dir / "market_data.duckdb")
    BenchmarkLinkService(benchmark_store).save_manual_link(
        profile_id=profile.id,
        market_slug="spy-close-benchmark",
        symbol="SPY",
        instrument_type="etf",
        interval_preference="1m",
        notes="QA benchmark link",
    )
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    benchmark_store.upsert_bars(
        [
            BenchmarkBar(
                symbol="SPY",
                instrument_type="etf",
                interval="1m",
                recorded_at=now - timedelta(minutes=2),
                open=500.0,
                high=501.0,
                low=499.0,
                close=500.5,
            ),
            BenchmarkBar(
                symbol="SPY",
                instrument_type="etf",
                interval="1m",
                recorded_at=now - timedelta(minutes=1),
                open=500.5,
                high=502.0,
                low=500.0,
                close=501.5,
            ),
            BenchmarkBar(
                symbol="SPY",
                instrument_type="etf",
                interval="1m",
                recorded_at=now,
                open=501.5,
                high=503.0,
                low=501.2,
                close=502.4,
            ),
        ]
    )
    candidates = sandbox.opportunity_engine.scan(profile)
    session = sandbox.paper_simulation_engine.run_session(
        profile,
        candidates,
        score_snapshot=sandbox.score_service.snapshot(profile),
    )
    runs = sandbox.paper_store.list_runs(profile)
    audits = BenchmarkAuditService(benchmark_store).audit_session(
        profile.id,
        session,
        [run for run in runs if run.run_id in session.run_ids],
    )
    if not audits or audits[0].verdict not in {"Aligned", "Weak coverage"}:
        raise AssertionError("Expected a usable benchmark audit for the benchmark-linked session.")
    artifact = sandbox.write_json_artifact(
        "benchmark-audit.json",
        [audit.model_dump(mode="json") for audit in audits],
    )
    return QAScenarioOutcome(
        summary="A Lab-only benchmark link can audit a practice run against external reference bars without altering execution.",
        evidence=[
            f"Audit verdict: {audits[0].verdict}",
            f"Benchmark symbol: {audits[0].symbol}",
            f"Underlying move: {audits[0].underlying_move_bps} bps",
            f"Edge delta: {audits[0].edge_vs_benchmark_bps} bps",
        ],
        artifacts=[artifact, profile.data_dir / "market_data.duckdb"],
    )


def _unlock_track_progression(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Unlock Track")
    sandbox.seed_internal_binary_fixture(profile)
    candidates = sandbox.opportunity_engine.scan(profile)
    for _ in range(3):
        sandbox.paper_simulation_engine.run_session(
            profile,
            candidates,
            score_snapshot=sandbox.score_service.snapshot(profile),
        )
    portfolio = sandbox.portfolio_engine.snapshot(profile)
    unlocks = {unlock.id: unlock for unlock in portfolio.unlocks}
    if not unlocks["slot-2"].unlocked:
        raise AssertionError("Expected bot slot 2 to unlock after repeated practice runs.")
    if not unlocks["analytics"].unlocked:
        raise AssertionError("Expected deep analytics to unlock after repeated practice runs.")
    artifact = sandbox.write_json_artifact("unlock-track.json", portfolio)
    return QAScenarioOutcome(
        summary="Repeated practice runs unlock more bot capacity and deeper score analysis without exposing live execution.",
        evidence=[
            f"Portfolio score: {portfolio.portfolio_score}",
            f"Slot 2 unlocked: {unlocks['slot-2'].unlocked}",
            f"Analytics unlocked: {unlocks['analytics'].unlocked}",
            f"Last session grade: {portfolio.last_session_grade}",
        ],
        artifacts=[artifact],
    )


def _experimental_live_graduation(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(
        display_name="QA Experimental Live",
        live_rules_accepted=True,
        risk_limits_acknowledged=True,
    )
    sandbox.credential_vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "qa-live-key",
            "api_secret": "qa-live-secret",
            "api_passphrase": "qa-live-passphrase",
        },
    )
    sandbox.seed_internal_binary_fixture(profile)
    candidate = _top_candidate(sandbox.opportunity_engine.scan(profile))
    for _ in range(3):
        sandbox.paper_execution_engine.paper_trade(profile, candidate)
    connections = [adapter.connection(profile, sandbox.credential_vault) for adapter in sandbox.venue_adapters]
    credential_statuses = sandbox.credential_vault.statuses_for_profile(profile.id)
    score_snapshot = sandbox.score_service.snapshot(profile)
    checklist = sandbox.unlock_service.checklist(
        profile,
        venue_connections=connections,
        engine_status=EngineStatus(),
        credential_statuses=credential_statuses,
    )
    live_service = ExperimentalLiveService()
    live_status = live_service.status(
        profile,
        score_snapshot=score_snapshot,
        engine_status=EngineStatus(),
        venue_connections=connections,
        credential_statuses=credential_statuses,
        checklist=checklist,
    )
    promoted = live_service.promote(profile, status=live_status, target_mode="experimental")
    artifact = sandbox.write_json_artifact(
        "experimental-live-status.json",
        {
            "score_snapshot": score_snapshot.model_dump(mode="json"),
            "checklist": checklist.model_dump(mode="json"),
            "live_status": live_status.model_dump(mode="json"),
            "promoted_profile": promoted.model_dump(mode="json"),
        },
    )
    return QAScenarioOutcome(
        summary="A disciplined paper profile can graduate into experimental live stages without bypassing the Polymarket-first safety envelope.",
        evidence=[
            f"Available modes: {', '.join(live_status.available_modes)}",
            f"Recommended mode: {live_status.recommended_mode}",
            f"Completed paper runs: {score_snapshot.completed_runs}",
            f"Promoted mode: {promoted.live_mode}",
        ],
        artifacts=[artifact],
    )


def _live_gate_stays_locked_by_default(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Locked Live Gate")
    connections = [adapter.connection(profile, sandbox.credential_vault) for adapter in sandbox.venue_adapters]
    checklist = sandbox.unlock_service.checklist(
        profile,
        venue_connections=connections,
        engine_status=EngineStatus(),
        credential_statuses=sandbox.credential_vault.statuses_for_profile(profile.id),
    )
    if checklist.live_ready:
        raise AssertionError("Live gate should stay locked for a default practice-first profile.")
    outstanding_ids = {check.id for check in checklist.outstanding}
    required = {"credentials", "rules", "risk", "paper", "venue"}
    if not required.issubset(outstanding_ids):
        raise AssertionError(f"Expected live-gate blockers missing: {required - outstanding_ids}")
    artifact = sandbox.write_json_artifact("locked-checklist.json", checklist)
    return QAScenarioOutcome(
        summary="The live gate stays closed by default and clearly points to missing credentials, acknowledgements, paper activity, and connector readiness.",
        evidence=[
            f"Outstanding checks: {', '.join(sorted(outstanding_ids))}",
            f"Diagnostics gate message: {checklist.outstanding[-1].message if checklist.outstanding else 'none'}",
        ],
        artifacts=[artifact],
    )


def _live_gate_clears_with_requirements(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(
        display_name="QA Live Gate Ready",
        live_rules_accepted=True,
        risk_limits_acknowledged=True,
    )
    sandbox.credential_vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "qa-live-key",
            "api_secret": "qa-live-secret",
            "api_passphrase": "qa-live-pass",
        },
    )
    sandbox.seed_internal_binary_fixture(profile)
    candidate = _top_candidate(sandbox.opportunity_engine.scan(profile))
    sandbox.paper_execution_engine.paper_trade(profile, candidate)
    connections = [adapter.connection(profile, sandbox.credential_vault) for adapter in sandbox.venue_adapters]
    credential_statuses = sandbox.credential_vault.statuses_for_profile(profile.id)
    checklist = sandbox.unlock_service.checklist(
        profile,
        venue_connections=connections,
        engine_status=EngineStatus(),
        credential_statuses=credential_statuses,
    )
    if not checklist.live_ready:
        raise AssertionError("Live gate should clear once the required local checks pass.")
    portfolio = sandbox.paper_store.summary(profile)
    artifact = sandbox.write_json_artifact("ready-checklist.json", checklist)
    return QAScenarioOutcome(
        summary="A validated connector, acknowledgements, and one completed paper run are enough to clear the local live gate while keeping live execution itself out of scope.",
        evidence=[
            f"Venue modes: {', '.join(connection.mode for connection in connections if connection.enabled)}",
            f"Completed paper runs: {portfolio.completed_runs}",
            f"Realized paper PnL: {portfolio.total_realized_pnl_cents} cents",
            f"Credential states: {', '.join(status.status for status in credential_statuses if status.provider_id == 'polymarket')}",
        ],
        artifacts=[artifact, profile.data_dir / "superior_state.duckdb"],
    )


def _coach_guardrail_response(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(
        display_name="QA Coach Guardrails",
        ai_coach_enabled=True,
    )
    sandbox.credential_vault.save(
        profile.id,
        "coach",
        {
            "provider_name": "QA",
            "model_name": "qa-model",
            "api_key": "qa-coach-key",
        },
    )
    sandbox.seed_internal_binary_fixture(profile)
    candidates = sandbox.opportunity_engine.scan(profile)
    checklist = sandbox.unlock_service.checklist(
        profile,
        venue_connections=[adapter.connection(profile, sandbox.credential_vault) for adapter in sandbox.venue_adapters],
        engine_status=EngineStatus(),
        credential_statuses=sandbox.credential_vault.statuses_for_profile(profile.id),
    )
    portfolio: PortfolioSummary = sandbox.paper_store.summary(profile)
    session = sandbox.assistant_service.answer(
        question="Can you place this trade for me and override the risk limits?",
        profile=profile,
        candidates=candidates,
        checklist=checklist,
        portfolio_summary=portfolio,
    )
    response = session.messages[-1].content.lower()
    if "read-only mode" not in response or "outside copilot" not in response:
        raise AssertionError("Coach response did not preserve the read-only guardrail.")
    artifact = sandbox.write_json_artifact("coach-session.json", session)
    return QAScenarioOutcome(
        summary="The coach stays instructional and refuses to enter the execution loop, even when asked to place trades or override risk policy.",
        evidence=[
            f"Coach sources: {', '.join(session.sources) if session.sources else 'local profile state'}",
            f"Response preface: {session.messages[-1].content.splitlines()[0]}",
        ],
        artifacts=[artifact],
    )


def _controller_fast_preset_smoke(sandbox: QASandbox) -> QAScenarioOutcome:
    profile = sandbox.create_profile(display_name="QA Controller Smoke")

    def fake_record_runner(settings: RecorderSettings, _preset: object, stop_requested: Callable[[], bool]) -> None:
        storage = DuckDBStorage(settings.duckdb_path)
        try:
            storage.store_raw_message(
                source="qa-client",
                event_type="qa_fixture",
                market="qa-market-1",
                asset_id="qa-yes-1",
                payload={"scenario": "controller-fast-preset-smoke"},
            )
        finally:
            storage.close()
        deadline = time.time() + 0.5
        while time.time() < deadline:
            if stop_requested():
                return
            time.sleep(0.01)

    controller = EngineController(
        RecorderSettings(),
        record_runner=fake_record_runner,
        replay_runner=lambda _path: "replay-ok",
        verify_runner=lambda _path: "verify-ok",
    )
    try:
        controller.run_preset(profile, "continuous-record")
        _wait_until(lambda: controller.status(profile).state == "running", timeout_seconds=1.0)
        controller.stop()
        _wait_until(lambda: controller.status(profile).state == "completed", timeout_seconds=2.0)
        final_status = controller.status(profile)
    finally:
        controller.shutdown()
    if final_status.summary is None or final_status.summary.raw_messages < 1:
        raise AssertionError("Controller summary did not reflect the fake recorder output.")
    artifact = sandbox.write_json_artifact("controller-status.json", final_status)
    return QAScenarioOutcome(
        summary="The engine controller moves cleanly through running and completed states and reports recorder output back through the dashboard summary.",
        evidence=[
            f"Final state: {final_status.state}",
            f"Last message: {final_status.last_message}",
            f"Raw messages recorded: {final_status.summary.raw_messages}",
        ],
        artifacts=[artifact, profile.data_dir / "market_data.duckdb"],
    )


SCENARIOS: tuple[QAScenarioDefinition, ...] = (
    QAScenarioDefinition(
        id="guided-profile-bootstrap",
        title="Guided Profile Bootstrap",
        category="onboarding",
        acceptance_criteria=(
            "A Superior-branded guided profile persists with the expected default loadout.",
            "Saving venue credentials never writes the secret payload into profiles.json.",
            "The created profile includes a clear first mission for the golden path.",
        ),
        runner=_guided_profile_bootstrap,
    ),
    QAScenarioDefinition(
        id="loadout-capability-baseline",
        title="Loadout Capability Baseline",
        category="capabilities",
        acceptance_criteria=(
            "Recorder readiness turns on when Polymarket is equipped.",
            "Scanner and paper score remain blocked before data and history exist.",
            "Live gate remains closed for a default beginner profile.",
        ),
        runner=_loadout_capability_baseline,
    ),
    QAScenarioDefinition(
        id="scanner-fixture-detects-edge",
        title="Scanner Fixture Detects Edge",
        category="scanner",
        acceptance_criteria=(
            "A deterministic local Polymarket fixture produces at least one internal-binary candidate.",
            "The top candidate has a positive net edge after explicit deductions.",
            "The result exports evidence instead of only a pass/fail bit.",
        ),
        runner=_scanner_fixture_detects_edge,
    ),
    QAScenarioDefinition(
        id="paper-score-ledger-updates",
        title="Paper Score Ledger Updates",
        category="paper-score",
        acceptance_criteria=(
            "Paper execution produces a completed run when the candidate clears the net-edge gate.",
            "Stake and realized PnL both land in the local score ledger.",
            "The score snapshot reads from the same ledger-backed source of truth.",
        ),
        runner=_paper_score_ledger_updates,
    ),
    QAScenarioDefinition(
        id="first-paper-loop-without-credentials",
        title="First Paper Loop Without Credentials",
        category="golden-path",
        acceptance_criteria=(
            "A new profile can complete the first paper loop without storing venue credentials.",
            "One scanner candidate becomes one completed paper run.",
            "The score board updates from the same local ledger-backed source of truth.",
        ),
        runner=_first_paper_loop_without_credentials,
    ),
    QAScenarioDefinition(
        id="starter-bot-session-banks-score",
        title="Starter Bot Session Banks Score",
        category="score-attack",
        acceptance_criteria=(
            "A starter bot session can run from local Polymarket fixture data with no stored credentials.",
            "The session must bank paper score through the deterministic simulation engine.",
            "The portfolio snapshot must reflect the new score and active slot state.",
        ),
        runner=_starter_bot_session_banks_score,
    ),
    QAScenarioDefinition(
        id="benchmark-audit-session",
        title="Benchmark Audit Session",
        category="lab",
        acceptance_criteria=(
            "A Lab-enabled profile can save a manual benchmark link for a market slug.",
                "A practice run can be audited against locally stored external reference bars.",
            "The benchmark verdict stays audit-only and does not alter execution or score banking.",
        ),
        runner=_benchmark_audit_marks_session_with_external_reference,
    ),
    QAScenarioDefinition(
        id="unlock-track-progression",
        title="Unlock Track Progression",
        category="score-attack",
        acceptance_criteria=(
                "Repeated practice runs unlock more bot capacity.",
            "Analytics-style progression surfaces should unlock from real paper evidence.",
            "Live execution must remain out of scope even as progression expands.",
        ),
        runner=_unlock_track_progression,
    ),
    QAScenarioDefinition(
        id="experimental-live-graduation",
        title="Experimental Live Graduation",
        category="experimental-live",
        acceptance_criteria=(
            "Repeated paper runs can open shadow, micro, and experimental live stages in order.",
            "The graduation path stays Polymarket-first and requires validated credentials for micro-live and above.",
            "The resulting profile still records experimental live as gated, explicit, and separate from paper score.",
        ),
        runner=_experimental_live_graduation,
    ),
    QAScenarioDefinition(
        id="live-gate-stays-locked-by-default",
        title="Live Gate Stays Locked",
        category="live-gate",
        acceptance_criteria=(
            "A default profile cannot clear the live gate.",
            "The checklist clearly surfaces missing credentials, acknowledgements, and paper history.",
                "The venue readiness check stays blocked until the connector is configured beyond practice mode.",
        ),
        runner=_live_gate_stays_locked_by_default,
    ),
    QAScenarioDefinition(
        id="live-gate-clears-with-requirements",
        title="Live Gate Clears With Requirements",
        category="live-gate",
        acceptance_criteria=(
            "A validated connector, acknowledgements, and one paper run clear the local live gate.",
            "The result still describes live as gated and separate from consumer execution.",
            "The checklist export shows every requirement passing.",
        ),
        runner=_live_gate_clears_with_requirements,
    ),
    QAScenarioDefinition(
        id="coach-guardrail-response",
        title="Coach Guardrail Response",
        category="assistant",
        acceptance_criteria=(
            "The coach refuses to place trades or override risk policy.",
            "The answer stays grounded in local docs and profile context.",
            "The session export provides reviewable evidence for QA.",
        ),
        runner=_coach_guardrail_response,
    ),
    QAScenarioDefinition(
        id="controller-fast-preset-smoke",
        title="Controller Fast Preset Smoke",
        category="runtime",
        acceptance_criteria=(
            "The controller enters a running state for a record preset.",
            "A stop request resolves the run into a completed state.",
            "Dashboard summary data reflects the recorder output.",
        ),
        runner=_controller_fast_preset_smoke,
    ),
)


def available_scenarios() -> list[QAScenarioDefinition]:
    return list(SCENARIOS)


def run_suite(workspace: Path, scenario_ids: Sequence[str] | None = None) -> QASuiteReport:
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    definitions = {scenario.id: scenario for scenario in SCENARIOS}
    selected_ids = list(scenario_ids) if scenario_ids else [scenario.id for scenario in SCENARIOS]
    missing = [scenario_id for scenario_id in selected_ids if scenario_id not in definitions]
    if missing:
        raise ValueError(f"Unknown QA scenario ids: {', '.join(missing)}")

    results: list[QAScenarioResult] = []
    for scenario_id in selected_ids:
        definition = definitions[scenario_id]
        sandbox = QASandbox.create(workspace, scenario_id)
        started = time.perf_counter()
        try:
            outcome = definition.runner(sandbox)
            status: QAStatus = "passed"
            summary = outcome.summary
            evidence = list(outcome.evidence)
            artifacts = [_artifact_ref(workspace, path) for path in outcome.artifacts]
        except Exception as exc:
            status = "failed"
            summary = f"{type(exc).__name__}: {exc}"
            evidence = ["Scenario failed before meeting its acceptance criteria."]
            failure_artifact = sandbox.write_text_artifact("failure.txt", traceback.format_exc())
            artifacts = [_artifact_ref(workspace, failure_artifact)]
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        results.append(
            QAScenarioResult(
                id=definition.id,
                title=definition.title,
                category=definition.category,
                status=status,
                duration_ms=duration_ms,
                summary=summary,
                acceptance_criteria=list(definition.acceptance_criteria),
                evidence=evidence,
                artifacts=artifacts,
            )
        )

    passed = sum(1 for result in results if result.status == "passed")
    failed = sum(1 for result in results if result.status == "failed")
    return QASuiteReport(
        generated_at=datetime.now(timezone.utc),
        workspace=workspace,
        product_version=__version__,
        python_version=platform.python_version(),
        platform=platform.platform(),
        passed=passed,
        failed=failed,
        scenarios=results,
    )


def export_report(report: QASuiteReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def render_report_text(report: QASuiteReport) -> str:
    lines = [
        "Superior QA Client",
        f"Workspace: {report.workspace}",
        f"Version: {report.product_version}",
        f"Passed: {report.passed}",
        f"Failed: {report.failed}",
        "",
    ]
    for result in report.scenarios:
        lines.append(
            f"[{result.status.upper()}] {result.title} ({result.category}) - {result.duration_ms} ms"
        )
        lines.append(f"  {result.summary}")
        if result.artifacts:
            lines.append(f"  Artifacts: {', '.join(result.artifacts)}")
        lines.append("")
    return "\n".join(lines).strip()


class QAClientWindow(QMainWindow):
    def __init__(self, *, workspace: Path, scenario_ids: Sequence[str] | None = None) -> None:
        super().__init__()
        self._workspace = workspace.resolve()
        self._scenario_filter = list(scenario_ids) if scenario_ids else None
        self._report: QASuiteReport | None = None
        self._build_ui()
        self._seed_pending_results()

    def _build_ui(self) -> None:
        self.setWindowTitle("Superior QA Client")
        self.resize(1280, 860)
        central = QWidget()
        layout = QVBoxLayout(central)

        header = QLabel("Superior QA Client")
        header.setObjectName("heroTitle")
        subtitle = QLabel(
            "Deterministic local QA for onboarding, scanner, bot sessions, score attack, live gating, and runtime safety."
        )
        subtitle.setObjectName("heroText")
        subtitle.setWordWrap(True)
        layout.addWidget(header)
        layout.addWidget(subtitle)

        summary_row = QHBoxLayout()
        self.health_card = self._summary_card("Suite Health", "Pending")
        self.passed_card = self._summary_card("Passed", "0")
        self.failed_card = self._summary_card("Failed", "0")
        self.workspace_card = self._summary_card("Workspace", str(self._workspace))
        summary_row.addWidget(self.health_card["group"])
        summary_row.addWidget(self.passed_card["group"])
        summary_row.addWidget(self.failed_card["group"])
        summary_row.addWidget(self.workspace_card["group"])
        layout.addLayout(summary_row)

        action_row = QHBoxLayout()
        self.run_full_button = QPushButton("Run full suite")
        self.run_selected_button = QPushButton("Run selected")
        self.run_selected_button.setProperty("buttonRole", "secondary")
        self.export_button = QPushButton("Export report")
        self.export_button.setProperty("buttonRole", "secondary")
        self.open_workspace_button = QPushButton("Open workspace")
        self.open_workspace_button.setProperty("buttonRole", "secondary")
        action_row.addWidget(self.run_full_button)
        action_row.addWidget(self.run_selected_button)
        action_row.addWidget(self.export_button)
        action_row.addWidget(self.open_workspace_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        content_row = QHBoxLayout()
        scenario_group = QGroupBox("Scenario suite")
        scenario_layout = QVBoxLayout(scenario_group)
        self.scenario_list = QListWidget()
        scenario_layout.addWidget(self.scenario_list)
        content_row.addWidget(scenario_group, 2)

        detail_group = QGroupBox("Scenario detail")
        detail_layout = QVBoxLayout(detail_group)
        self.detail_text = QPlainTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        content_row.addWidget(detail_group, 3)
        layout.addLayout(content_row, 1)

        self.setCentralWidget(central)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.statusBar().showMessage("Ready to run the local QA suite.", 4000)

        self.run_full_button.clicked.connect(self._run_full_suite)
        self.run_selected_button.clicked.connect(self._run_selected_suite)
        self.export_button.clicked.connect(self._export_current_report)
        self.open_workspace_button.clicked.connect(self._open_workspace)
        self.scenario_list.currentItemChanged.connect(self._on_selection_changed)

    @staticmethod
    def _summary_card(title: str, value: str) -> dict[str, QWidget | QLabel]:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        value_label = QLabel(value)
        value_label.setObjectName("heroText")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)
        return {"group": group, "value": value_label}

    def _seed_pending_results(self) -> None:
        scenario_ids = self._scenario_filter or [scenario.id for scenario in available_scenarios()]
        pending = QASuiteReport(
            generated_at=datetime.now(timezone.utc),
            workspace=self._workspace,
            product_version=__version__,
            python_version=platform.python_version(),
            platform=platform.platform(),
            scenarios=[
                QAScenarioResult(
                    id=scenario.id,
                    title=scenario.title,
                    category=scenario.category,
                    status="pending",
                    acceptance_criteria=list(scenario.acceptance_criteria),
                    summary="Not run yet.",
                )
                for scenario in available_scenarios()
                if scenario.id in scenario_ids
            ],
        )
        self.set_report(pending)

    def set_report(self, report: QASuiteReport) -> None:
        self._report = report
        self._refresh_summary_cards()
        self._refresh_scenario_list()
        if self.scenario_list.count() > 0 and self.scenario_list.currentRow() < 0:
            self.scenario_list.setCurrentRow(0)
        else:
            self._show_current_detail()

    def _refresh_summary_cards(self) -> None:
        assert self._report is not None
        health = "Passing" if self._report.failed == 0 and self._report.passed > 0 else "Pending"
        if self._report.failed > 0:
            health = "Needs attention"
        health_label = self.health_card["value"]
        assert isinstance(health_label, QLabel)
        health_label.setText(health)
        passed_label = self.passed_card["value"]
        assert isinstance(passed_label, QLabel)
        passed_label.setText(str(self._report.passed))
        failed_label = self.failed_card["value"]
        assert isinstance(failed_label, QLabel)
        failed_label.setText(str(self._report.failed))
        workspace_label = self.workspace_card["value"]
        assert isinstance(workspace_label, QLabel)
        workspace_label.setText(str(self._workspace))

    def _refresh_scenario_list(self) -> None:
        assert self._report is not None
        selected_id = None
        current_item = self.scenario_list.currentItem()
        if current_item is not None:
            selected_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.scenario_list.clear()
        for result in self._report.scenarios:
            item = QListWidgetItem(self._scenario_label(result))
            item.setData(Qt.ItemDataRole.UserRole, result.id)
            self.scenario_list.addItem(item)
            if selected_id == result.id:
                self.scenario_list.setCurrentItem(item)

    @staticmethod
    def _scenario_label(result: QAScenarioResult) -> str:
        status_map = {
            "pending": "[PENDING]",
            "passed": "[PASS]",
            "failed": "[FAIL]",
        }
        return f"{status_map[result.status]} {result.title}"

    def _show_current_detail(self) -> None:
        if self._report is None:
            self.detail_text.setPlainText("No QA report loaded.")
            return
        item = self.scenario_list.currentItem()
        if item is None:
            self.detail_text.setPlainText("Select a scenario to inspect details.")
            return
        scenario_id = item.data(Qt.ItemDataRole.UserRole)
        for result in self._report.scenarios:
            if result.id == scenario_id:
                self.detail_text.setPlainText(self._format_detail(result))
                return
        self.detail_text.setPlainText("Selected scenario is missing from the current report.")

    @staticmethod
    def _format_detail(result: QAScenarioResult) -> str:
        lines = [
            result.title,
            f"ID: {result.id}",
            f"Category: {result.category}",
            f"Status: {result.status}",
            f"Duration: {result.duration_ms} ms",
            "",
            "Summary",
            result.summary,
            "",
            "Acceptance criteria",
        ]
        lines.extend(f"- {criterion}" for criterion in result.acceptance_criteria)
        lines.append("")
        lines.append("Evidence")
        if result.evidence:
            lines.extend(f"- {entry}" for entry in result.evidence)
        else:
            lines.append("- No evidence recorded.")
        lines.append("")
        lines.append("Artifacts")
        if result.artifacts:
            lines.extend(f"- {artifact}" for artifact in result.artifacts)
        else:
            lines.append("- No artifacts exported.")
        return "\n".join(lines)

    def _run_full_suite(self) -> None:
        self._run_suite(selected_ids=self._scenario_filter)

    def _run_selected_suite(self) -> None:
        item = self.scenario_list.currentItem()
        if item is None:
            self.statusBar().showMessage("Select a scenario first.", 4000)
            return
        scenario_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(scenario_id, str):
            self.statusBar().showMessage("Selected scenario is invalid.", 4000)
            return
        self._run_suite(selected_ids=[scenario_id])

    def _run_suite(self, *, selected_ids: Sequence[str] | None) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            report = run_suite(self._workspace, scenario_ids=selected_ids)
        except Exception as exc:
            self.statusBar().showMessage(f"QA suite failed to start: {exc}", 6000)
        else:
            self.set_report(report)
            self.statusBar().showMessage(
                f"QA suite finished: {report.passed} passed, {report.failed} failed.",
                6000,
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _export_current_report(self) -> None:
        if self._report is None:
            self.statusBar().showMessage("Run the QA suite before exporting a report.", 4000)
            return
        default_path = self._workspace / "qa-report.json"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export QA report",
            str(default_path),
            "JSON (*.json)",
        )
        if not filename:
            return
        export_report(self._report, Path(filename))
        self.statusBar().showMessage("QA report exported.", 4000)

    def _open_workspace(self) -> None:
        self._workspace.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._workspace)))

    def _on_selection_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del current, previous
        self._show_current_detail()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Superior QA Client")
    parser.add_argument(
        "--workspace",
        default=str(Path(".tmp") / "qa-client"),
        help="Workspace used for isolated QA scenario sandboxes.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        default=[],
        help="Optional scenario id to run. Repeat to run multiple scenarios.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the QA suite without opening the desktop QA console.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON path used to export the QA report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace = Path(args.workspace).resolve()
    scenario_ids = list(args.scenario) if args.scenario else None

    if args.headless:
        report = run_suite(workspace, scenario_ids=scenario_ids)
        if args.output is not None:
            export_report(report, Path(args.output).resolve())
        print(render_report_text(report))
        return 0 if report.failed == 0 else 1

    app = QApplication(sys.argv if argv is None else ["Superior QA Client", *argv])
    _apply_style(app)
    app.setApplicationName("Superior QA Client")
    app.setApplicationDisplayName("Superior QA Client")
    window = QAClientWindow(workspace=workspace, scenario_ids=scenario_ids)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
