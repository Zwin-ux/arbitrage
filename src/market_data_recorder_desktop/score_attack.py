from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .app_types import (
    AppProfile,
    BotBlueprint,
    BotConfig,
    BotRecipe,
    BotRegistryEntry,
    BotSlot,
    DecisionTraceLine,
    OpportunityCandidate,
    PaperBotDecision,
    PaperBotEvent,
    PaperBotSession,
    PaperRunResult,
    PortfolioCurvePoint,
    PortfolioSnapshot,
    ScoreSnapshot,
    SessionGrade,
    UnlockRequirement,
    UnlockState,
)
from .bot_services import PaperExecutionEngine, PaperRunStore
from .bot_recipes import BotRecipeStore


def _score_delta_for_run(run: PaperRunResult) -> int:
    if run.status != "completed":
        return 0
    quality_bonus = int(round(run.opportunity_quality_score / 2))
    edge_bonus = max(run.realized_edge_bps, 0)
    pnl_bonus = max(run.realized_pnl_cents, 0)
    discipline_bonus = 12 if run.execution.fill_ratio >= 0.8 else 0
    return pnl_bonus + quality_bonus + edge_bonus + discipline_bonus


def _family_label(strategy_family: str) -> str:
    return {
        "internal-binary": "Internal Binary",
        "cross-venue-complement": "Cross-Venue",
        "negative-risk-basket": "Neg Risk Lab",
        "maker-rebate-lab": "Maker Lab",
    }.get(strategy_family, strategy_family.replace("-", " ").title())


def _route_preference_label(route_preference: str) -> str:
    return {
        "highest_edge": "Highest edge",
        "best_quality": "Best quality",
        "balanced": "Balanced",
    }.get(route_preference, route_preference.replace("-", " ").title())


class BotConfigService:
    def __init__(self, recipe_store: BotRecipeStore | None = None) -> None:
        self._recipe_store = recipe_store or BotRecipeStore()

    def blueprints(self, profile: AppProfile) -> list[BotBlueprint]:
        blueprints: list[BotBlueprint] = []
        if "internal-binary" in profile.equipped_modules:
            blueprints.extend(
                [
                    BotBlueprint(
                        id="scout-bot",
                        label="Scout Bot",
                        description="Fast internal-binary scout that arms on modest positive edge and banks the first clean route.",
                        strategy_family="internal-binary",
                        min_net_edge_bps=20,
                        target_stake_cents=1_200,
                        route_preference="highest_edge",
                    ),
                    BotBlueprint(
                        id="discipline-bot",
                        label="Discipline Bot",
                        description="Higher threshold bot that favors quality and rewards cleaner fills over raw volume.",
                        strategy_family="internal-binary",
                        min_net_edge_bps=45,
                        target_stake_cents=1_800,
                        route_preference="best_quality",
                    ),
                ]
            )
        if "cross-venue-complement" in profile.equipped_modules:
            blueprints.append(
                BotBlueprint(
                    id="bridge-bot",
                    label="Bridge Bot",
                    description="Cross-venue complement bot that only arms when an exact match survives the net-edge gate.",
                    strategy_family="cross-venue-complement",
                    min_net_edge_bps=35,
                    target_stake_cents=1_600,
                    route_preference="balanced",
                )
            )
        if profile.lab_enabled and "negative-risk-basket" in profile.equipped_modules:
            blueprints.append(
                BotBlueprint(
                    id="lab-sentry",
                    label="Lab Sentry",
                    description="Paper-only lab bot that watches experimental neg-risk surfaces without touching live controls.",
                    strategy_family="negative-risk-basket",
                    min_net_edge_bps=30,
                    target_stake_cents=1_000,
                    route_preference="balanced",
                    lab_only=True,
                )
            )
        return blueprints

    def recipes(self, profile: AppProfile) -> list[BotRecipe]:
        starter_recipes = [
            self._recipe_store.recipe_from_blueprint(profile, blueprint) for blueprint in self.blueprints(profile)
        ]
        local_recipes = self._recipe_store.list_local_recipes(profile)
        return [*local_recipes, *starter_recipes]

    def recipe_by_id(self, profile: AppProfile, recipe_id: str) -> BotRecipe | None:
        for recipe in self.recipes(profile):
            if recipe.recipe_id == recipe_id:
                return recipe
        return None

    def fork_recipe(self, profile: AppProfile, recipe_id: str, *, new_label: str | None = None) -> BotRecipe:
        recipe = self.recipe_by_id(profile, recipe_id)
        if recipe is None:
            raise KeyError(f"Unknown bot recipe: {recipe_id}")
        return self._recipe_store.fork_recipe(profile, recipe, new_label=new_label)

    def _armable_recipes(self, profile: AppProfile) -> list[BotRecipe]:
        armable: list[BotRecipe] = []
        for recipe in self.recipes(profile):
            if not recipe.enabled:
                continue
            if recipe.strategy_family not in profile.equipped_modules:
                continue
            if recipe.lab_only and not profile.lab_enabled:
                continue
            armable.append(recipe)
        return armable

    def configs(self, profile: AppProfile, score_snapshot: ScoreSnapshot) -> list[BotConfig]:
        unlocked_slots = max(1, min(score_snapshot.available_bot_slots, 3))
        recipes = self._armable_recipes(profile)
        configs: list[BotConfig] = []
        for index, recipe in enumerate(recipes[:unlocked_slots], start=1):
            source_blueprint_id = recipe.source_blueprint_id or recipe.recipe_id
            configs.append(
                BotConfig(
                    blueprint_id=source_blueprint_id,
                    recipe_id=recipe.recipe_id,
                    slot_id=f"slot-{index}",
                    label=recipe.label,
                    strategy_family=recipe.strategy_family,
                    min_net_edge_bps=recipe.min_net_edge_bps,
                    max_position_cents=min(profile.live_position_cap_cents * 10, recipe.target_stake_cents),
                    max_assignments=recipe.max_assignments,
                    route_preference=recipe.route_preference,
                    enabled=recipe.enabled,
                    source_kind=recipe.source_kind,
                    source_blueprint_id=source_blueprint_id,
                )
            )
        return configs

    def slot_preview(self, profile: AppProfile, score_snapshot: ScoreSnapshot) -> list[BotSlot]:
        configs = self.configs(profile, score_snapshot)
        by_slot = {config.slot_id: config for config in configs}
        slots: list[BotSlot] = []
        for index in range(1, 4):
            slot_id = f"slot-{index}"
            config = by_slot.get(slot_id)
            if config is None:
                slots.append(
                    BotSlot(
                        slot_id=slot_id,
                        label=f"Slot {index}",
                        state="locked" if index > score_snapshot.available_bot_slots else "empty",
                        bot_label="Locked" if index > score_snapshot.available_bot_slots else "Open",
                        detail=(
                            "Complete more paper runs to unlock this bot slot."
                            if index > score_snapshot.available_bot_slots
                            else "This slot is open. Equip more modules to arm a bot here."
                        ),
                    )
                )
                continue
            slots.append(
                BotSlot(
                    slot_id=slot_id,
                    label=f"Slot {index}",
                    state="armed",
                    bot_id=config.recipe_id or config.blueprint_id,
                    bot_label=config.label,
                    detail=(
                        f"Armed for {config.strategy_family} at {config.min_net_edge_bps}+ bps."
                        if config.source_kind == "starter"
                        else f"Forked recipe armed at {config.min_net_edge_bps}+ bps."
                    ),
                )
            )
        return slots


class BotRegistryService:
    def __init__(self, bot_config_service: BotConfigService) -> None:
        self._bot_config_service = bot_config_service

    def entries(
        self,
        profile: AppProfile,
        score_snapshot: ScoreSnapshot,
        unlocks: list[UnlockState],
    ) -> list[BotRegistryEntry]:
        configs = {
            (config.recipe_id or config.blueprint_id): config
            for config in self._bot_config_service.configs(profile, score_snapshot)
        }
        next_unlock = next((unlock for unlock in unlocks if not unlock.unlocked), None)
        entries: list[BotRegistryEntry] = []
        armable_ids = {
            recipe.recipe_id
            for recipe in self._bot_config_service.recipes(profile)
            if recipe.enabled
            and recipe.strategy_family in profile.equipped_modules
            and (not recipe.lab_only or profile.lab_enabled)
        }
        for index, recipe in enumerate(self._bot_config_service.recipes(profile), start=1):
            config = configs.get(recipe.recipe_id)
            if config is not None:
                status = "armed"
                slot_label = config.slot_id.replace("-", " ").title()
                unlock_label = f"Armed in {slot_label}."
                tone = "active"
            elif recipe.lab_only and not profile.lab_enabled:
                status = "offline"
                slot_label = "Lab only"
                unlock_label = "Enable Lab to surface this starter bot."
                tone = "locked"
            elif not recipe.enabled:
                status = "offline"
                slot_label = "Disabled"
                unlock_label = "Recipe is saved locally but disabled."
                tone = "locked"
            elif recipe.strategy_family not in profile.equipped_modules:
                status = "offline"
                slot_label = "Module missing"
                unlock_label = "Equip this strategy module before the recipe can arm."
                tone = "warning"
            elif recipe.recipe_id in armable_ids and index <= score_snapshot.available_bot_slots:
                status = "available"
                slot_label = f"Slot {index}"
                unlock_label = "Current bot bay has room to arm this recipe."
                tone = "warning"
            else:
                status = "locked"
                slot_label = f"Slot {index}"
                unlock_label = next_unlock.detail if next_unlock is not None else score_snapshot.next_unlock_label
                tone = "locked"
            entries.append(
                BotRegistryEntry(
                    blueprint_id=recipe.source_blueprint_id or recipe.recipe_id,
                    recipe_id=recipe.recipe_id,
                    label=recipe.label,
                    strategy_family=recipe.strategy_family,
                    family_label=_family_label(recipe.strategy_family),
                    description=recipe.description,
                    min_net_edge_bps=recipe.min_net_edge_bps,
                    target_stake_cents=recipe.target_stake_cents,
                    route_preference=recipe.route_preference,
                    lab_only=recipe.lab_only,
                    status=status,
                    unlock_label=unlock_label,
                    slot_label=slot_label,
                    tone=tone,
                    source_kind=recipe.source_kind,
                    source_blueprint_id=recipe.source_blueprint_id,
                )
            )
        return entries


class SessionEventStore:
    def __init__(self, paper_store: PaperRunStore) -> None:
        self._paper_store = paper_store

    def append(self, profile: AppProfile, session: PaperBotSession) -> PaperBotSession:
        return self._paper_store.append_session(profile, session)

    def list_sessions(self, profile: AppProfile, *, limit: int = 12) -> list[PaperBotSession]:
        return self._paper_store.list_sessions(profile, limit=limit)

    def recent_events(self, profile: AppProfile, *, limit: int = 32) -> list[PaperBotEvent]:
        sessions = self.list_sessions(profile, limit=12)
        events: list[PaperBotEvent] = []
        for session in reversed(sessions):
            events.extend(session.events)
        return events[-limit:]


class UnlockTrackService:
    def unlocks(self, profile: AppProfile, score_snapshot: ScoreSnapshot) -> list[UnlockState]:
        completed_runs = score_snapshot.completed_runs
        hit_rate = score_snapshot.hit_rate
        realized_edge = score_snapshot.average_realized_edge_bps
        unlocks = [
            UnlockState(
                id="slot-2",
                label="Bot Slot 2",
                unlocked=completed_runs >= 2,
                detail=(
                    "A second bot slot opens after two completed paper runs."
                    if completed_runs < 2
                    else "Second slot is live for dual-bot paper sessions."
                ),
                requirements=[
                    UnlockRequirement(
                        id="completed-runs-2",
                        label="Completed paper runs",
                        target="2 runs",
                        met=completed_runs >= 2,
                    )
                ],
            ),
            UnlockState(
                id="slot-3",
                label="Bot Slot 3",
                unlocked=completed_runs >= 5 and hit_rate >= 50.0,
                detail=(
                    "Slot 3 unlocks at 5 completed runs with at least 50% hit rate."
                    if not (completed_runs >= 5 and hit_rate >= 50.0)
                    else "Third slot is live for full score-attack sessions."
                ),
                requirements=[
                    UnlockRequirement(
                        id="completed-runs-5",
                        label="Completed paper runs",
                        target="5 runs",
                        met=completed_runs >= 5,
                    ),
                    UnlockRequirement(
                        id="hit-rate-50",
                        label="Hit rate",
                        target="50%",
                        met=hit_rate >= 50.0,
                    ),
                ],
            ),
            UnlockState(
                id="analytics",
                label="Deep Analytics",
                unlocked=completed_runs >= 3,
                detail=(
                    "Deep analytics appear after three completed runs."
                    if completed_runs < 3
                    else "Deep analytics are unlocked for richer score review."
                ),
                requirements=[
                    UnlockRequirement(
                        id="completed-runs-3",
                        label="Completed paper runs",
                        target="3 runs",
                        met=completed_runs >= 3,
                    ),
                ],
            ),
            UnlockState(
                id="route-filters",
                label="Advanced Route Filters",
                unlocked=completed_runs >= 4 and realized_edge >= 30,
                detail=(
                    "Advanced route filters unlock when realized edge stays above 30 bps over four runs."
                    if not (completed_runs >= 4 and realized_edge >= 30)
                    else "Advanced route filters are available in the bot bay."
                ),
                requirements=[
                    UnlockRequirement(
                        id="completed-runs-4",
                        label="Completed paper runs",
                        target="4 runs",
                        met=completed_runs >= 4,
                    ),
                    UnlockRequirement(
                        id="realized-edge-30",
                        label="Average realized edge",
                        target="30 bps",
                        met=realized_edge >= 30,
                    ),
                ],
            ),
            UnlockState(
                id="lab-preview",
                label="Lab Preview",
                unlocked=profile.lab_enabled or (completed_runs >= 6 and hit_rate >= 60.0),
                detail=(
                    "Lab preview stays locked until the profile enables Lab or earns six disciplined runs."
                    if not (profile.lab_enabled or (completed_runs >= 6 and hit_rate >= 60.0))
                    else "Lab preview is unlocked for paper-only experimentation."
                ),
                requirements=[
                    UnlockRequirement(
                        id="lab-enabled",
                        label="Lab enabled",
                        target="profile toggle",
                        met=profile.lab_enabled,
                    ),
                    UnlockRequirement(
                        id="completed-runs-6",
                        label="Completed paper runs",
                        target="6 runs",
                        met=completed_runs >= 6,
                    ),
                    UnlockRequirement(
                        id="hit-rate-60",
                        label="Hit rate",
                        target="60%",
                        met=hit_rate >= 60.0,
                    ),
                ],
            ),
            UnlockState(
                id="shadow-preview",
                label="Shadow Live Preview",
                unlocked=completed_runs >= 3 and score_snapshot.paper_realized_pnl_cents >= 0,
                detail=(
                    "Shadow-live preview unlocks after three paper runs without a negative paper score."
                    if not (completed_runs >= 3 and score_snapshot.paper_realized_pnl_cents >= 0)
                    else "Shadow-live preview is visible, but public live execution stays locked."
                ),
                requirements=[
                    UnlockRequirement(
                        id="completed-runs-3b",
                        label="Completed paper runs",
                        target="3 runs",
                        met=completed_runs >= 3,
                    ),
                    UnlockRequirement(
                        id="non-negative-paper-score",
                        label="Paper score floor",
                        target=">= 0",
                        met=score_snapshot.paper_realized_pnl_cents >= 0,
                    ),
                ],
            ),
        ]
        return unlocks


class ProgressionService:
    def next_unlock_text(self, unlocks: list[UnlockState]) -> str:
        for unlock in unlocks:
            if not unlock.unlocked:
                unmet = [requirement.target for requirement in unlock.requirements if not requirement.met]
                detail = f" Need {', '.join(unmet)}." if unmet else ""
                return f"Next unlock: {unlock.label}.{detail}"
        return "All current paper-first unlocks are online."


class DecisionTraceFormatter:
    def render(self, session: PaperBotSession | None) -> str:
        if session is None:
            return (
                "TACTICAL TRACE\n\n"
                "No decision trace yet.\n"
                "Start a paper session to see what each bot saw, why it acted, and how score moved."
            )
        lines = [
            "TACTICAL TRACE",
            "",
            f"Session grade: {session.grade.grade}",
            f"Score delta: {session.score_delta}",
            "",
        ]
        for decision in session.decisions:
            lines.append(f"{decision.slot_id.upper()} :: {decision.decision.upper()} :: {decision.route_label or 'No route'}")
            lines.append(f"Reason: {decision.reason}")
            for item in decision.trace_lines:
                lines.append(f"  {item.label.upper():<12} {item.value}")
            lines.append("")
        return "\n".join(lines).rstrip()


class PortfolioEngine:
    def __init__(
        self,
        paper_store: PaperRunStore,
        bot_config_service: BotConfigService,
        unlock_track_service: UnlockTrackService,
    ) -> None:
        self._paper_store = paper_store
        self._bot_config_service = bot_config_service
        self._unlock_track_service = unlock_track_service

    def snapshot(self, profile: AppProfile | None) -> PortfolioSnapshot:
        if profile is None:
            return PortfolioSnapshot()
        runs = self._paper_store.list_runs(profile)
        sessions = self._paper_store.list_sessions(profile)
        score_snapshot = self._paper_store.score_snapshot(profile)
        unlocks = self._unlock_track_service.unlocks(profile, score_snapshot)
        cumulative_pnl = 0
        cumulative_score = 0
        curve_points: list[PortfolioCurvePoint] = []
        for run in runs:
            if run.status != "completed":
                continue
            cumulative_pnl += run.realized_pnl_cents
            cumulative_score += _score_delta_for_run(run)
            curve_points.append(
                PortfolioCurvePoint(
                    recorded_at=run.executed_at,
                    label=run.strategy_ids[0] if run.strategy_ids else "paper-run",
                    run_id=run.run_id,
                    cumulative_pnl_cents=cumulative_pnl,
                    cumulative_score=cumulative_score,
                )
            )
        active_slots = sum(1 for slot in self._bot_config_service.slot_preview(profile, score_snapshot) if slot.state == "armed")
        return PortfolioSnapshot(
            profile_id=profile.id,
            total_realized_pnl_cents=score_snapshot.paper_realized_pnl_cents,
            portfolio_score=score_snapshot.portfolio_score,
            mastery_score=score_snapshot.mastery_score,
            available_bot_slots=score_snapshot.available_bot_slots,
            active_bot_slots=active_slots,
            sessions_completed=len([session for session in sessions if session.state == "complete"]),
            current_streak=score_snapshot.current_streak,
            last_session_grade=sessions[-1].grade.grade if sessions else "D",
            curve_points=curve_points,
            unlocks=unlocks,
        )


class PaperSimulationEngine:
    def __init__(
        self,
        *,
        paper_store: PaperRunStore,
        paper_execution_engine: PaperExecutionEngine,
        bot_config_service: BotConfigService,
        session_store: SessionEventStore,
    ) -> None:
        self._paper_store = paper_store
        self._paper_execution_engine = paper_execution_engine
        self._bot_config_service = bot_config_service
        self._session_store = session_store

    def run_session(
        self,
        profile: AppProfile,
        candidates: list[OpportunityCandidate],
        *,
        score_snapshot: ScoreSnapshot | None = None,
    ) -> PaperBotSession:
        snapshot = score_snapshot or self._paper_store.score_snapshot(profile)
        configs = self._bot_config_service.configs(profile, snapshot)
        now = datetime.now(timezone.utc)
        session_id = str(uuid.uuid4())
        events: list[PaperBotEvent] = [
            PaperBotEvent(
                event_id=str(uuid.uuid4()),
                session_id=session_id,
                occurred_at=now,
                slot_id="session",
                bot_id="session",
                event_type="session_start",
                title="Session start",
                detail="Superior armed the current bot bay and is staging routes from local scanner output.",
                tone="active",
            )
        ]
        slots: list[BotSlot] = []
        decisions: list[PaperBotDecision] = []
        run_ids: list[str] = []
        curve_points: list[PortfolioCurvePoint] = []
        used_candidate_ids: set[str] = set()
        cumulative_pnl = 0
        cumulative_score = 0
        completed_runs: list[PaperRunResult] = []

        for config in configs:
            bot_id = config.recipe_id or config.blueprint_id
            slot = BotSlot(
                slot_id=config.slot_id,
                label=config.slot_id.replace("-", " ").title(),
                state="armed",
                bot_id=bot_id,
                bot_label=config.label,
                detail=f"Armed at {config.min_net_edge_bps}+ bps.",
            )
            slots.append(slot)
            events.append(
                PaperBotEvent(
                    event_id=str(uuid.uuid4()),
                    session_id=session_id,
                    occurred_at=datetime.now(timezone.utc),
                    slot_id=config.slot_id,
                    bot_id=bot_id,
                    event_type="bot_armed",
                    title=f"{config.label} armed",
                    detail=f"Watching {config.strategy_family} routes with a {config.min_net_edge_bps} bps gate.",
                    tone="active",
                )
            )
            candidate = self._select_candidate(config, candidates, used_candidate_ids)
            if candidate is None:
                slot.state = "blocked"
                slot.bot_label = config.label
                slot.detail = "No staged route cleared this bot gate."
                decisions.append(
                    PaperBotDecision(
                        bot_id=bot_id,
                        slot_id=config.slot_id,
                        decision="blocked",
                        reason="No current candidate matched the bot gate.",
                        route_label="No staged route",
                        stake_cents=0,
                        quality_score=0,
                        trace_lines=[
                            DecisionTraceLine(label="family", value=_family_label(config.strategy_family)),
                            DecisionTraceLine(label="gate", value=f"{config.min_net_edge_bps}+ bps", tone="warning"),
                            DecisionTraceLine(label="route", value="No matching local route", tone="locked"),
                            DecisionTraceLine(label="result", value="Bot stayed blocked", tone="locked"),
                        ],
                    )
                )
                events.append(
                    PaperBotEvent(
                        event_id=str(uuid.uuid4()),
                        session_id=session_id,
                        occurred_at=datetime.now(timezone.utc),
                        slot_id=config.slot_id,
                        bot_id=bot_id,
                        event_type="blocked",
                        title=f"{config.label} blocked",
                        detail="No local route matched the configured strategy family and edge threshold.",
                        tone="warning",
                    )
                )
                continue

            used_candidate_ids.add(candidate.id)
            slot.state = "staged"
            slot.current_candidate_id = candidate.id
            slot.detail = f"Staged {candidate.strategy_label} at {candidate.net_edge_bps} bps."
            decisions.append(
                PaperBotDecision(
                    bot_id=bot_id,
                    slot_id=config.slot_id,
                    decision="stage",
                    reason=f"Candidate cleared the {config.min_net_edge_bps} bps bot gate.",
                    candidate_id=candidate.id,
                    route_label=candidate.strategy_label,
                    expected_edge_bps=candidate.net_edge_bps,
                    stake_cents=min(candidate.recommended_stake_cents, config.max_position_cents),
                    quality_score=candidate.opportunity_quality_score,
                    trace_lines=[
                        DecisionTraceLine(label="family", value=_family_label(config.strategy_family)),
                        DecisionTraceLine(label="preference", value=_route_preference_label(config.route_preference)),
                        DecisionTraceLine(label="route", value=candidate.summary),
                        DecisionTraceLine(label="gross edge", value=f"{candidate.gross_edge_bps} bps", tone="warning"),
                        DecisionTraceLine(label="net edge", value=f"{candidate.net_edge_bps} bps", tone="active"),
                        DecisionTraceLine(label="quality", value=str(candidate.opportunity_quality_score), tone="active"),
                        DecisionTraceLine(
                            label="stake",
                            value=f"${min(candidate.recommended_stake_cents, config.max_position_cents) / 100:.2f}",
                        ),
                        DecisionTraceLine(label="result", value="Route staged", tone="warning"),
                    ],
                )
            )
            events.append(
                PaperBotEvent(
                    event_id=str(uuid.uuid4()),
                    session_id=session_id,
                    occurred_at=datetime.now(timezone.utc),
                    slot_id=config.slot_id,
                    bot_id=bot_id,
                    event_type="route_staged",
                    title=f"{config.label} staged route",
                    detail=f"{candidate.strategy_label} cleared the bot gate at {candidate.net_edge_bps} bps.",
                    tone="warning",
                    metadata={"candidate_id": candidate.id, "strategy": candidate.strategy_id},
                )
            )
            run = self._paper_execution_engine.paper_trade(profile, candidate)
            run_ids.append(run.run_id)
            score_delta = _score_delta_for_run(run)
            cumulative_pnl += run.realized_pnl_cents
            cumulative_score += score_delta
            completed_runs.append(run)
            slot.state = "banked" if run.status == "completed" else "blocked"
            slot.realized_pnl_cents = run.realized_pnl_cents
            slot.score_delta = score_delta
            slot.detail = (
                f"Banked ${run.realized_pnl_cents / 100:.2f} and {score_delta} score."
                if run.status == "completed"
                else "Route stayed out of the paper ledger."
            )
            decisions.append(
                PaperBotDecision(
                    bot_id=bot_id,
                    slot_id=config.slot_id,
                    decision="bank" if run.status == "completed" else "blocked",
                    reason=run.notes,
                    candidate_id=candidate.id,
                    route_label=candidate.strategy_label,
                    expected_edge_bps=run.expected_edge_bps,
                    realized_edge_bps=run.realized_edge_bps,
                    realized_pnl_cents=run.realized_pnl_cents,
                    stake_cents=run.deployed_capital_cents,
                    quality_score=run.opportunity_quality_score,
                    score_delta=score_delta,
                    trace_lines=[
                        DecisionTraceLine(label="family", value=_family_label(config.strategy_family)),
                        DecisionTraceLine(label="route", value=candidate.summary),
                        DecisionTraceLine(label="gate", value=f"{config.min_net_edge_bps}+ bps", tone="warning"),
                        DecisionTraceLine(label="expected", value=f"{run.expected_edge_bps} bps", tone="warning"),
                        DecisionTraceLine(
                            label="realized",
                            value=f"{run.realized_edge_bps} bps",
                            tone="success" if run.status == "completed" else "locked",
                        ),
                        DecisionTraceLine(label="quality", value=str(run.opportunity_quality_score), tone="active"),
                        DecisionTraceLine(label="stake", value=f"${run.deployed_capital_cents / 100:.2f}"),
                        DecisionTraceLine(
                            label="paper pnl",
                            value=f"${run.realized_pnl_cents / 100:.2f}",
                            tone="success" if run.realized_pnl_cents >= 0 else "error",
                        ),
                        DecisionTraceLine(
                            label="score",
                            value=str(score_delta),
                            tone="success" if score_delta > 0 else "locked",
                        ),
                        DecisionTraceLine(
                            label="result",
                            value="Score banked" if run.status == "completed" else "Route blocked",
                            tone="success" if run.status == "completed" else "locked",
                        ),
                    ],
                )
            )
            events.append(
                PaperBotEvent(
                    event_id=str(uuid.uuid4()),
                    session_id=session_id,
                    occurred_at=run.executed_at,
                    slot_id=config.slot_id,
                    bot_id=bot_id,
                    event_type="paper_banked" if run.status == "completed" else "blocked",
                    title=f"{config.label} {'banked score' if run.status == 'completed' else 'blocked'}",
                    detail=(
                        f"Paper PnL {run.realized_pnl_cents / 100:.2f} with realized edge {run.realized_edge_bps} bps."
                        if run.status == "completed"
                        else "The route did not clear the deterministic paper fill rules."
                    ),
                    tone="success" if run.status == "completed" else "error",
                    amount_cents=run.realized_pnl_cents,
                    metadata={"run_id": run.run_id, "candidate_id": candidate.id},
                )
            )
            curve_points.append(
                PortfolioCurvePoint(
                    recorded_at=run.executed_at,
                    label=config.label,
                    run_id=run.run_id,
                    cumulative_pnl_cents=cumulative_pnl,
                    cumulative_score=cumulative_score,
                )
            )

        combo_count = 0
        for run in completed_runs:
            if run.realized_pnl_cents > 0:
                combo_count += 1
            else:
                combo_count = 0
                break
        consistency_bonus = 15 if completed_runs and all(run.realized_pnl_cents >= 0 for run in completed_runs) else 0
        session_score = cumulative_score + consistency_bonus
        grade = self._grade_session(session_score)
        ended_at = datetime.now(timezone.utc)
        final_state = "complete" if completed_runs else "blocked"
        events.append(
            PaperBotEvent(
                event_id=str(uuid.uuid4()),
                session_id=session_id,
                occurred_at=ended_at,
                slot_id="session",
                bot_id="session",
                event_type="session_complete",
                title="Session complete",
                detail=f"Banked ${cumulative_pnl / 100:.2f} with session grade {grade.grade}.",
                tone="success" if completed_runs else "warning",
                amount_cents=cumulative_pnl,
            )
        )
        session = PaperBotSession(
            session_id=session_id,
            profile_id=profile.id,
            started_at=now,
            ended_at=ended_at,
            state=final_state,
            bot_slots=slots or self._bot_config_service.slot_preview(profile, snapshot),
            decisions=decisions,
            events=events,
            run_ids=run_ids,
            realized_pnl_cents=cumulative_pnl,
            score_delta=session_score,
            curve_points=curve_points,
            grade=grade,
        )
        return self._session_store.append(profile, session)

    @staticmethod
    def _grade_session(session_score: int) -> SessionGrade:
        if session_score >= 260:
            grade = "S"
        elif session_score >= 180:
            grade = "A"
        elif session_score >= 120:
            grade = "B"
        elif session_score >= 60:
            grade = "C"
        else:
            grade = "D"
        combo_count = 3 if session_score >= 180 else 2 if session_score >= 120 else 1 if session_score >= 60 else 0
        consistency_bonus = 15 if session_score >= 120 else 0
        note = {
            "S": "High-discipline session. Multiple routes banked cleanly.",
            "A": "Strong session with consistent score pressure.",
            "B": "Solid paper session with room for cleaner fills.",
            "C": "Starter session complete. Keep feeding the machine.",
            "D": "No clean score banked yet. Tighten the bot bay and try again.",
        }[grade]
        return SessionGrade(
            grade=grade,
            score_delta=session_score,
            combo_count=combo_count,
            consistency_bonus=consistency_bonus,
            note=note,
        )

    @staticmethod
    def _select_candidate(
        config: BotConfig,
        candidates: list[OpportunityCandidate],
        used_candidate_ids: set[str],
    ) -> OpportunityCandidate | None:
        matching = [
            candidate
            for candidate in candidates
            if candidate.id not in used_candidate_ids
            and candidate.strategy_id == config.strategy_family
            and candidate.net_edge_bps >= config.min_net_edge_bps
        ]
        if not matching:
            return None
        if config.route_preference == "best_quality":
            return max(matching, key=lambda candidate: (candidate.opportunity_quality_score, candidate.net_edge_bps))
        if config.route_preference == "balanced":
            return max(
                matching,
                key=lambda candidate: (candidate.net_edge_bps + candidate.opportunity_quality_score, candidate.gross_edge_bps),
            )
        return max(matching, key=lambda candidate: (candidate.net_edge_bps, candidate.opportunity_quality_score))
