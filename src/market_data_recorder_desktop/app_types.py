from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field


TemplateName = Literal["Recorder", "Research", "Custom", "Guided"]
PresetMode = Literal["record", "replay", "verify"]
EngineState = Literal["idle", "running", "completed", "failed"]
CredentialState = Literal["missing", "saved", "validated", "invalid"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
StrategyTier = Literal["core", "lab"]
OpportunityStatus = Literal["candidate", "rejected", "monitor"]
PaperRunStatus = Literal["completed", "skipped"]
ScoreboardMode = Literal["paper", "live"]
LiveMode = Literal["locked", "shadow", "micro", "experimental"]
ConnectorId = Literal["polymarket", "kalshi", "coach"]
ModuleId = Literal[
    "internal-binary",
    "cross-venue-complement",
    "negative-risk-basket",
    "maker-rebate-lab",
]
LedgerType = Literal["paper_stake", "paper_pnl", "live_pnl"]


class RunPreset(BaseModel):
    id: str
    label: str
    description: str
    mode: PresetMode
    runtime_seconds: float | None = None
    persist_discovery_metadata: bool = False
    max_pages: int | None = None
    asset_ids: list[str] = Field(default_factory=list)


class AppProfile(BaseModel):
    id: str
    display_name: str
    template: TemplateName = "Guided"
    data_dir: Path
    enabled_venues: list[str] = Field(default_factory=lambda: ["Polymarket"])
    market_filters: list[str] = Field(default_factory=list)
    auto_start: bool = False
    start_minimized: bool = False
    default_preset: str = "continuous-record"
    notes: str | None = None
    experience_level: ExperienceLevel = "beginner"
    guided_mode: bool = True
    lab_enabled: bool = False
    live_unlocked: bool = False
    ai_coach_enabled: bool = False
    default_strategy_tier: StrategyTier = "core"
    risk_policy_id: str = "starter"
    primary_goal: str = "learn_and_scan"
    live_rules_accepted: bool = False
    risk_limits_acknowledged: bool = False
    brand_name: str = "Superior"
    equipped_connectors: list[ConnectorId] = Field(
        default_factory=lambda: cast(list[ConnectorId], ["polymarket"])
    )
    equipped_modules: list[ModuleId] = Field(
        default_factory=lambda: cast(list[ModuleId], ["internal-binary", "cross-venue-complement"])
    )
    scoreboard_mode: ScoreboardMode = "paper"
    first_run_completed: bool = False
    primary_mission: str = "Equip Polymarket and record your first book."
    experimental_live_enabled: bool = False
    live_mode: LiveMode = "locked"
    live_target_venue: str = "Polymarket"
    live_position_cap_cents: int = 100
    live_daily_cap_cents: int = 500
    live_allowed_strategy_ids: list[str] = Field(default_factory=lambda: ["internal-binary"])
    paper_gate_passed: bool = False
    paper_gate_passed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CredentialField(BaseModel):
    key: str
    label: str
    help_text: str
    secret: bool = False
    multiline: bool = False
    required: bool = False
    placeholder: str | None = None


class CredentialValidationResult(BaseModel):
    ok: bool
    status: CredentialState
    message: str


class CredentialStatus(BaseModel):
    provider_id: str
    provider_label: str
    status: CredentialState
    message: str


class DashboardSummary(BaseModel):
    db_path: Path
    raw_messages: int = 0
    book_snapshots: int = 0
    health_events: int = 0
    last_recorded_at: datetime | None = None
    latest_warning: str | None = None


class EngineStatus(BaseModel):
    state: EngineState = "idle"
    active_profile_id: str | None = None
    active_preset_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_message: str = "Ready."
    last_error: str | None = None
    summary: DashboardSummary | None = None


class VenueConnection(BaseModel):
    venue_id: str
    venue_label: str
    enabled: bool
    configured: bool
    mode: Literal["disabled", "paper", "configured", "live_ready"]
    message: str


class ConnectorLoadout(BaseModel):
    profile_id: str
    equipped_connectors: list[ConnectorId] = Field(default_factory=list)
    equipped_modules: list[ModuleId] = Field(default_factory=list)


class CapabilityState(BaseModel):
    capability_id: str
    label: str
    equipped: bool = False
    ready: bool = False
    tier: StrategyTier = "core"
    message: str


class RiskPolicy(BaseModel):
    id: str
    label: str
    description: str
    max_position_cents: int
    max_daily_loss_cents: int
    max_open_positions: int
    lab_only: bool = False


class LiveUnlockCheck(BaseModel):
    id: str
    label: str
    passed: bool
    message: str


class LiveUnlockChecklist(BaseModel):
    checks: list[LiveUnlockCheck] = Field(default_factory=list)
    live_ready: bool = False

    @property
    def outstanding(self) -> list[LiveUnlockCheck]:
        return [check for check in self.checks if not check.passed]


class ExperimentalLiveStatus(BaseModel):
    current_mode: LiveMode = "locked"
    recommended_mode: LiveMode = "locked"
    paper_gate_passed: bool = False
    available_modes: list[LiveMode] = Field(default_factory=lambda: cast(list[LiveMode], ["locked"]))
    venue_scope: list[str] = Field(default_factory=list)
    strategy_scope: list[str] = Field(default_factory=list)
    position_cap_cents: int = 0
    daily_cap_cents: int = 0
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ExperimentalLivePlan(BaseModel):
    mode: LiveMode = "locked"
    send_orders: bool = False
    venue_label: str = "Polymarket"
    strategy_id: str = ""
    order_style: Literal["shadow", "post_only", "post_only_or_taker"] = "shadow"
    min_net_edge_bps: int = 0
    max_position_cents: int = 0
    max_daily_cap_cents: int = 0
    message: str = ""
    blockers: list[str] = Field(default_factory=list)


class CanonicalContract(BaseModel):
    venue_id: str
    contract_id: str
    question: str
    slug: str
    outcome: str
    orientation: str


class ContractMatch(BaseModel):
    status: Literal["exact_match", "probable_match", "reject"]
    reason: str


class OpportunityEvidence(BaseModel):
    raw_edge_bps: int = 0
    net_edge_bps: int = 0
    cost_adjustments_bps: dict[str, int] = Field(default_factory=dict)
    matched_markets: list[str] = Field(default_factory=list)
    rationale: str = ""


class OpportunityExplanation(BaseModel):
    summary: str
    matched_contracts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    cost_adjustments_bps: dict[str, int] = Field(default_factory=dict)


class OpportunityCandidate(BaseModel):
    id: str
    strategy_id: str
    strategy_label: str
    tier: StrategyTier = "core"
    status: OpportunityStatus = "candidate"
    market_slug: str
    summary: str
    venues: list[str] = Field(default_factory=list)
    gross_edge_bps: int = 0
    net_edge_bps: int = 0
    recommended_stake_cents: int = 0
    lab_only: bool = False
    explanation: OpportunityExplanation
    evidence: OpportunityEvidence = Field(default_factory=OpportunityEvidence)
    opportunity_quality_score: int = 0


class PaperPosition(BaseModel):
    market_slug: str
    strategy_id: str
    venue_labels: list[str] = Field(default_factory=list)
    deployed_capital_cents: int = 0
    expected_edge_bps: int = 0
    realized_pnl_cents: int = 0


class PaperExecutionSummary(BaseModel):
    fill_ratio: float = 0.0
    realized_edge_bps: int = 0
    slippage_bps: int = 0
    notes: str = ""


class PaperRunConfig(BaseModel):
    profile_id: str
    candidate_ids: list[str] = Field(default_factory=list)
    bankroll_cents: int = 10_000
    max_positions: int = 1
    slippage_bps: int = 10


class PaperRunResult(BaseModel):
    run_id: str
    profile_id: str
    executed_at: datetime
    strategy_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[str] = Field(default_factory=list)
    status: PaperRunStatus = "completed"
    deployed_capital_cents: int = 0
    expected_edge_bps: int = 0
    realized_pnl_cents: int = 0
    realized_edge_bps: int = 0
    opportunity_quality_score: int = 0
    notes: str = ""
    positions: list[PaperPosition] = Field(default_factory=list)
    execution: PaperExecutionSummary = Field(default_factory=PaperExecutionSummary)


class StrategyModule(BaseModel):
    id: ModuleId
    label: str
    description: str
    tier: StrategyTier = "core"
    guided_visible: bool = True
    paper_only: bool = True


class AssistantMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AssistantSession(BaseModel):
    session_id: str
    profile_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list[AssistantMessage] = Field(default_factory=list)
    remote_configured: bool = False
    sources: list[str] = Field(default_factory=list)


class VenueMarketQuote(BaseModel):
    venue_id: str
    contract_id: str
    market_id: str
    question: str
    slug: str
    outcome: str
    best_bid: float | None = None
    best_ask: float | None = None
    fees_enabled: bool = False
    neg_risk: bool = False
    recorded_at: datetime | None = None


class ScoreLedgerEntry(BaseModel):
    entry_id: str
    profile_id: str
    run_id: str | None = None
    recorded_at: datetime
    ledger_type: LedgerType
    amount_cents: int = 0
    label: str
    metadata: dict[str, str] = Field(default_factory=dict)


class ScoreSnapshot(BaseModel):
    profile_id: str | None = None
    scoreboard_mode: ScoreboardMode = "paper"
    paper_realized_pnl_cents: int = 0
    live_realized_pnl_cents: int = 0
    completed_runs: int = 0
    total_runs: int = 0
    hit_rate: float = 0.0
    average_expected_edge_bps: int = 0
    average_realized_edge_bps: int = 0
    current_streak: int = 0
    opportunity_quality_score: int = 0
    last_updated_at: datetime | None = None


class PortfolioSummary(BaseModel):
    total_runs: int = 0
    completed_runs: int = 0
    total_deployed_cents: int = 0
    total_realized_pnl_cents: int = 0


def default_run_presets() -> list[RunPreset]:
    return [
        RunPreset(
            id="continuous-record",
            label="Continuous recorder",
            description="Capture Polymarket market data until you stop the app.",
            mode="record",
            persist_discovery_metadata=True,
        ),
        RunPreset(
            id="fast-smoke-run",
            label="Quick calibration",
            description="Record a short sample to confirm recorder health.",
            mode="record",
            runtime_seconds=30.0,
            max_pages=1,
        ),
        RunPreset(
            id="replay-latest",
            label="Replay latest DB",
            description="Summarize the current profile database.",
            mode="replay",
        ),
        RunPreset(
            id="verify-latest",
            label="Verify latest DB",
            description="Verify hashes and stream consistency for the current profile database.",
            mode="verify",
        ),
    ]


def default_risk_policies() -> list[RiskPolicy]:
    return [
        RiskPolicy(
            id="starter",
            label="Starter",
            description="Small paper allocations and a conservative daily loss cap.",
            max_position_cents=2_500,
            max_daily_loss_cents=1_500,
            max_open_positions=1,
        ),
        RiskPolicy(
            id="balanced",
            label="Balanced",
            description="Moderate paper sizing for users who already understand fill risk.",
            max_position_cents=7_500,
            max_daily_loss_cents=5_000,
            max_open_positions=2,
        ),
        RiskPolicy(
            id="lab",
            label="Lab",
            description="Experimental paper sizing for high-risk strategy work inside the Lab.",
            max_position_cents=15_000,
            max_daily_loss_cents=10_000,
            max_open_positions=3,
            lab_only=True,
        ),
    ]


def default_strategy_modules() -> list[StrategyModule]:
    return [
        StrategyModule(
            id="internal-binary",
            label="Internal Binary",
            description="Scan binary Polymarket books for yes/no baskets priced below full payout after costs.",
            tier="core",
            guided_visible=True,
        ),
        StrategyModule(
            id="cross-venue-complement",
            label="Cross-Venue Complement",
            description="Match equivalent contracts across venues and reject anything that is not an exact economic match.",
            tier="core",
            guided_visible=True,
        ),
        StrategyModule(
            id="negative-risk-basket",
            label="Neg Risk Lab",
            description="Track neg-risk surfaces and experimental basket opportunities in paper mode only.",
            tier="lab",
            guided_visible=False,
        ),
        StrategyModule(
            id="maker-rebate-lab",
            label="Maker Lab",
            description="Inspect maker and rebate experiments behind an explicit Lab gate.",
            tier="lab",
            guided_visible=False,
        ),
    ]
