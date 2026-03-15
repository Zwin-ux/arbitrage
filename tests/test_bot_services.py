from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from market_data_recorder.models import (
    BestBidAskEvent,
    DiscoveredMarket,
    PolymarketEvent,
    PolymarketMarket,
)
from market_data_recorder.storage import DuckDBStorage
from market_data_recorder_desktop.app_types import (
    AppProfile,
    EngineStatus,
    LiveUnlockChecklist,
    OpportunityCandidate,
    PaperRunResult,
    ScoreSnapshot,
)
from market_data_recorder_desktop.bot_services import (
    CapabilityService,
    ConnectorLoadoutService,
    ContractMatcher,
    ExperimentalLiveService,
    LiveExecutionEngine,
    OpportunityEngine,
    PaperExecutionEngine,
    PaperRunStore,
    PolymarketVenueAdapter,
    ScoreService,
    UnlockService,
)
from market_data_recorder_desktop.credentials import CredentialVault
from market_data_recorder_desktop.score_attack import (
    BotConfigService,
    PaperSimulationEngine,
    PortfolioEngine,
    SessionEventStore,
    UnlockTrackService,
)


def test_opportunity_engine_surfaces_internal_binary_candidate(app_paths: Any, fake_keyring: Any) -> None:
    profile = AppProfile(
        id="profile-1",
        display_name="Scanner",
        data_dir=app_paths.data_dir / "profile-1",
        enabled_venues=["Polymarket"],
    )
    db_path = profile.data_dir / "market_data.duckdb"
    storage = DuckDBStorage(db_path)
    try:
        market = PolymarketMarket.model_validate(
            {
                "id": "market-1",
                "conditionId": "condition-1",
                "question": "Will it rain?",
                "slug": "will-it-rain",
                "active": True,
                "enableOrderBook": True,
                "outcomes": '["Yes", "No"]',
                "clobTokenIds": '["yes-1", "no-1"]',
            }
        )
        event = PolymarketEvent.model_validate({"id": "event-1", "title": "Weather", "active": True})
        storage.store_discovery_snapshot([DiscoveredMarket(event=event, market=market)])
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="yes-1",
                market="market-1",
                best_bid="0.46",
                best_ask="0.47",
                spread="0.01",
                timestamp="1",
            )
        )
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="no-1",
                market="market-1",
                best_bid="0.47",
                best_ask="0.48",
                spread="0.01",
                timestamp="2",
            )
        )
    finally:
        storage.close()

    engine = OpportunityEngine([PolymarketVenueAdapter()], ContractMatcher())
    candidates = engine.scan(profile)

    assert candidates
    assert candidates[0].strategy_id == "internal-binary"
    assert candidates[0].net_edge_bps > 0
    assert "Will it rain?" in candidates[0].summary


def test_unlock_service_requires_paper_run_and_acknowledgements(app_paths: Any, fake_keyring: Any) -> None:
    profile = AppProfile(
        id="profile-2",
        display_name="Unlock",
        data_dir=app_paths.data_dir / "profile-2",
        enabled_venues=["Polymarket"],
        live_rules_accepted=True,
        risk_limits_acknowledged=True,
    )
    vault = CredentialVault(backend=fake_keyring)
    vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "key",
            "api_secret": "secret",
            "api_passphrase": "pass",
        },
    )
    paper_store = PaperRunStore()
    paper_store.append_run(
        profile,
        PaperRunResult(
            run_id="run-1",
            profile_id=profile.id,
            executed_at=datetime.now(timezone.utc),
            strategy_ids=["internal-binary"],
            candidate_ids=["cand-1"],
            status="completed",
            deployed_capital_cents=1000,
            expected_edge_bps=120,
            realized_pnl_cents=12,
            notes="ok",
        ),
    )

    checklist = UnlockService(paper_store).checklist(
        profile,
        venue_connections=[PolymarketVenueAdapter().connection(profile, vault)],
        engine_status=EngineStatus(),
        credential_statuses=vault.statuses_for_profile(profile.id),
    )

    assert checklist.live_ready is True
    assert all(check.passed for check in checklist.checks)


def test_paper_score_snapshot_uses_duckdb_ledger(app_paths: Any, fake_keyring: Any) -> None:
    del fake_keyring
    profile = AppProfile(
        id="profile-3",
        display_name="Score",
        data_dir=app_paths.data_dir / "profile-3",
        enabled_venues=["Polymarket"],
        equipped_connectors=["polymarket"],
    )
    paper_store = PaperRunStore()
    paper_store.append_run(
        profile,
        PaperRunResult(
            run_id="run-score-1",
            profile_id=profile.id,
            executed_at=datetime.now(timezone.utc),
            strategy_ids=["internal-binary"],
            candidate_ids=["cand-score-1"],
            status="completed",
            deployed_capital_cents=2000,
            expected_edge_bps=140,
            realized_pnl_cents=28,
            realized_edge_bps=120,
            opportunity_quality_score=74,
            notes="score test",
        ),
    )

    snapshot = ScoreService(paper_store).snapshot(profile)
    ledger = ScoreService(paper_store).ledger(profile)

    assert snapshot.paper_realized_pnl_cents == 28
    assert snapshot.completed_runs == 1
    assert snapshot.hit_rate == 100.0
    assert len(ledger) == 2


def test_loadout_and_capability_services_surface_equipped_states(app_paths: Any, fake_keyring: Any) -> None:
    profile = AppProfile(
        id="profile-4",
        display_name="Loadout",
        data_dir=app_paths.data_dir / "profile-4",
        enabled_venues=["Polymarket"],
        equipped_connectors=["polymarket", "coach"],
        equipped_modules=["internal-binary"],
        ai_coach_enabled=True,
    )
    vault = CredentialVault(backend=fake_keyring)
    vault.save(profile.id, "coach", {"api_key": "coach-key"})
    connections = [PolymarketVenueAdapter().connection(profile, vault)]
    credential_statuses = vault.statuses_for_profile(profile.id)

    loadout = ConnectorLoadoutService().build_loadout(profile)
    connector_states = ConnectorLoadoutService().connector_states(profile, connections, credential_statuses)
    capability_states = CapabilityService().states(
        profile=profile,
        engine_status=EngineStatus(),
        connections=connections,
        score_snapshot=ScoreService(PaperRunStore()).snapshot(profile),
        checklist=UnlockService(PaperRunStore()).checklist(
            profile,
            venue_connections=connections,
            engine_status=EngineStatus(),
            credential_statuses=credential_statuses,
        ),
    )

    assert "polymarket" in loadout.equipped_connectors
    assert any(item.capability_id == "coach" and item.equipped for item in connector_states)
    assert any(item.capability_id == "recorder" and item.ready for item in capability_states)


def test_experimental_live_service_promotes_from_shadow_to_micro(app_paths: Any, fake_keyring: Any) -> None:
    profile = AppProfile(
        id="profile-5",
        display_name="Experimental Live",
        data_dir=app_paths.data_dir / "profile-5",
        enabled_venues=["Polymarket"],
        live_rules_accepted=True,
        risk_limits_acknowledged=True,
        live_allowed_strategy_ids=["internal-binary"],
    )
    vault = CredentialVault(backend=fake_keyring)
    vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "key",
            "api_secret": "secret",
            "api_passphrase": "pass",
        },
    )
    paper_store = PaperRunStore()
    paper_store.append_run(
        profile,
        PaperRunResult(
            run_id="run-live-1",
            profile_id=profile.id,
            executed_at=datetime.now(timezone.utc),
            strategy_ids=["internal-binary"],
            candidate_ids=["cand-live-1"],
            status="completed",
            deployed_capital_cents=1000,
            expected_edge_bps=120,
            realized_pnl_cents=18,
            realized_edge_bps=92,
            notes="paper pass",
        ),
    )
    connections = [PolymarketVenueAdapter().connection(profile, vault)]
    credential_statuses = vault.statuses_for_profile(profile.id)
    checklist = UnlockService(paper_store).checklist(
        profile,
        venue_connections=connections,
        engine_status=EngineStatus(),
        credential_statuses=credential_statuses,
    )
    live_service = ExperimentalLiveService()
    live_status = live_service.status(
        profile,
        score_snapshot=ScoreService(paper_store).snapshot(profile),
        engine_status=EngineStatus(),
        venue_connections=connections,
        credential_statuses=credential_statuses,
        checklist=checklist,
    )

    assert "shadow" in live_status.available_modes
    assert "micro" in live_status.available_modes
    promoted = live_service.promote(profile, status=live_status, target_mode="micro")
    assert promoted.live_mode == "micro"
    assert promoted.live_unlocked is True
    assert promoted.experimental_live_enabled is True


def test_live_execution_preview_respects_shadow_and_micro_rules(app_paths: Any, fake_keyring: Any) -> None:
    profile = AppProfile(
        id="profile-6",
        display_name="Preview",
        data_dir=app_paths.data_dir / "profile-6",
        enabled_venues=["Polymarket"],
        live_mode="shadow",
        experimental_live_enabled=True,
        live_allowed_strategy_ids=["internal-binary"],
    )
    candidate = OpportunityCandidate(
        id="cand-6",
        strategy_id="internal-binary",
        strategy_label="Internal Binary",
        market_slug="preview-market",
        summary="Preview candidate",
        venues=["Polymarket"],
        gross_edge_bps=120,
        net_edge_bps=80,
        recommended_stake_cents=1000,
        explanation={"summary": "ok"},
    )
    live_status = ExperimentalLiveService().status(
        profile,
        score_snapshot=ScoreSnapshot(completed_runs=1, total_runs=1, average_realized_edge_bps=60),
        engine_status=EngineStatus(),
        venue_connections=[],
        credential_statuses=[],
        checklist=LiveUnlockChecklist(),
    )
    shadow_preview = LiveExecutionEngine().preview(profile, candidate, live_status)
    assert "Shadow mode" in shadow_preview
    assert "Would send live orders: no" in shadow_preview

    micro_profile = profile.model_copy(update={"live_mode": "micro"})
    micro_status = live_status.model_copy(update={"current_mode": "micro"})
    micro_preview = LiveExecutionEngine().preview(micro_profile, candidate, micro_status)
    assert "Mode: micro" in micro_preview


def test_paper_simulation_engine_runs_multi_bot_session(app_paths: Any, fake_keyring: Any) -> None:
    del fake_keyring
    profile = AppProfile(
        id="profile-7",
        display_name="Score Attack",
        data_dir=app_paths.data_dir / "profile-7",
        enabled_venues=["Polymarket"],
        equipped_connectors=["polymarket"],
        equipped_modules=["internal-binary", "cross-venue-complement"],
    )
    db_path = profile.data_dir / "market_data.duckdb"
    storage = DuckDBStorage(db_path)
    try:
        market = PolymarketMarket.model_validate(
            {
                "id": "market-7",
                "conditionId": "condition-7",
                "question": "Will session score climb?",
                "slug": "session-score-climb",
                "active": True,
                "enableOrderBook": True,
                "outcomes": '["Yes", "No"]',
                "clobTokenIds": '["yes-7", "no-7"]',
            }
        )
        event = PolymarketEvent.model_validate({"id": "event-7", "title": "Session", "active": True})
        storage.store_discovery_snapshot([DiscoveredMarket(event=event, market=market)])
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="yes-7",
                market="market-7",
                best_bid="0.44",
                best_ask="0.46",
                spread="0.02",
                timestamp="1",
            )
        )
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="no-7",
                market="market-7",
                best_bid="0.45",
                best_ask="0.47",
                spread="0.02",
                timestamp="2",
            )
        )
    finally:
        storage.close()

    paper_store = PaperRunStore()
    opportunity_engine = OpportunityEngine([PolymarketVenueAdapter()], ContractMatcher())
    candidates = opportunity_engine.scan(profile)
    score_snapshot = ScoreService(paper_store).snapshot(profile)
    simulation_engine = PaperSimulationEngine(
        paper_store=paper_store,
        paper_execution_engine=PaperExecutionEngine(paper_store),
        bot_config_service=BotConfigService(),
        session_store=SessionEventStore(paper_store),
    )
    session = simulation_engine.run_session(profile, candidates, score_snapshot=score_snapshot)
    sessions = paper_store.list_sessions(profile)

    assert session.state == "complete"
    assert session.score_delta > 0
    assert len(session.bot_slots) >= 1
    assert any(slot.state == "banked" for slot in session.bot_slots)
    assert sessions[-1].session_id == session.session_id


def test_portfolio_engine_surfaces_unlock_track(app_paths: Any, fake_keyring: Any) -> None:
    del fake_keyring
    profile = AppProfile(
        id="profile-8",
        display_name="Portfolio",
        data_dir=app_paths.data_dir / "profile-8",
        enabled_venues=["Polymarket"],
        equipped_connectors=["polymarket"],
    )
    paper_store = PaperRunStore()
    now = datetime.now(timezone.utc)
    for index in range(3):
        paper_store.append_run(
            profile,
            PaperRunResult(
                run_id=f"run-score-{index}",
                profile_id=profile.id,
                executed_at=now,
                strategy_ids=["internal-binary"],
                candidate_ids=[f"cand-{index}"],
                status="completed",
                deployed_capital_cents=2_000,
                expected_edge_bps=100,
                realized_pnl_cents=20 + index,
                realized_edge_bps=80,
                opportunity_quality_score=70,
                notes="portfolio test",
            ),
        )
    portfolio_snapshot = PortfolioEngine(
        paper_store,
        BotConfigService(),
        UnlockTrackService(),
    ).snapshot(profile)

    assert portfolio_snapshot.portfolio_score > 0
    assert portfolio_snapshot.available_bot_slots >= 2
    assert any(unlock.id == "slot-2" and unlock.unlocked for unlock in portfolio_snapshot.unlocks)
