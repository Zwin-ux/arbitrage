from __future__ import annotations

import time
from typing import Any, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit

from market_data_recorder.config import RecorderSettings
from market_data_recorder.models import BestBidAskEvent, DiscoveredMarket, PolymarketEvent, PolymarketMarket
from market_data_recorder.storage import DuckDBStorage
from market_data_recorder_desktop.bot_services import (
    AssistantService,
    CapabilityService,
    ConnectorLoadoutService,
    ContractMatcher,
    ExperimentalLiveService,
    KalshiVenueAdapter,
    LiveExecutionEngine,
    OpportunityEngine,
    PaperExecutionEngine,
    PaperRunStore,
    PolymarketVenueAdapter,
    ScoreService,
    UnlockService,
)
from market_data_recorder_desktop.controller import EngineController
from market_data_recorder_desktop.credentials import CredentialVault
from market_data_recorder_desktop.diagnostics import DiagnosticsService
from market_data_recorder_desktop.main import _smoke_report, main
from market_data_recorder_desktop.paths import AppPaths
from market_data_recorder_desktop.profiles import ProfileStore
from market_data_recorder_desktop.startup import UnsupportedStartupManager
from market_data_recorder_desktop.window import DesktopMainWindow
from market_data_recorder_desktop.wizard import SetupWizard


def _desktop_window(
    *,
    app_paths: AppPaths,
    store: ProfileStore,
    fake_keyring: Any,
    controller: EngineController,
    allow_setup_wizard_on_empty_profiles: bool = False,
) -> DesktopMainWindow:
    venue_adapters = [PolymarketVenueAdapter(), KalshiVenueAdapter()]
    paper_store = PaperRunStore()
    return DesktopMainWindow(
        paths=app_paths,
        profile_store=store,
        credential_vault=CredentialVault(backend=fake_keyring),
        controller=controller,
        diagnostics=DiagnosticsService(app_paths),
        startup_manager=UnsupportedStartupManager(),
        venue_adapters=venue_adapters,
        loadout_service=ConnectorLoadoutService(),
        capability_service=CapabilityService(),
        opportunity_engine=OpportunityEngine(venue_adapters, ContractMatcher()),
        paper_store=paper_store,
        score_service=ScoreService(paper_store),
        paper_execution_engine=PaperExecutionEngine(paper_store),
        experimental_live_service=ExperimentalLiveService(),
        live_execution_engine=LiveExecutionEngine(),
        unlock_service=UnlockService(paper_store),
        assistant_service=AssistantService(),
        allow_setup_wizard_on_empty_profiles=allow_setup_wizard_on_empty_profiles,
    )


def test_setup_wizard_creates_profile_and_keeps_secrets_out_of_json(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    vault = CredentialVault(backend=fake_keyring)
    wizard = SetupWizard(
        profile_store=store,
        credential_vault=vault,
        startup_manager=UnsupportedStartupManager(),
        preset_labels=[("continuous-record", "Continuous recorder")],
    )
    qtbot.addWidget(wizard)

    wizard.profile_page.name_edit.setText("Wizard Profile")
    wizard.profile_page.data_dir_edit.setText(str(app_paths.data_dir / "wizard"))
    wizard.venue_page.polymarket_checkbox.setChecked(True)
    wizard.credentials_page.set_enabled_providers(["polymarket"])
    box = wizard.credentials_page._field_widgets["polymarket"]  # noqa: SLF001
    cast(QLineEdit, box["api_key"]).setText("api-key")
    cast(QLineEdit, box["api_secret"]).setText("secret-value")
    cast(QLineEdit, box["api_passphrase"]).setText("passphrase-value")
    wizard.risk_page.market_filters_edit.setText("sports, elections")
    wizard.accept()

    created = store.get_profile(wizard.created_profile_id or "")
    assert created is not None
    assert created.display_name == "Wizard Profile"
    assert created.primary_goal == "learn_and_scan"
    assert created.risk_policy_id == "starter"
    assert created.brand_name == "Superior"
    assert "Connector credentials entered now: Polymarket" in wizard.finish_page.summary_label.text()
    profiles_json = store.profiles_path.read_text(encoding="utf-8")
    assert "secret-value" not in profiles_json
    assert fake_keyring.store


def test_setup_wizard_allows_first_run_without_credentials(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    vault = CredentialVault(backend=fake_keyring)
    wizard = SetupWizard(
        profile_store=store,
        credential_vault=vault,
        startup_manager=UnsupportedStartupManager(),
        preset_labels=[("continuous-record", "Continuous recorder")],
    )
    qtbot.addWidget(wizard)

    wizard.profile_page.name_edit.setText("No Keys Yet")
    wizard.profile_page.data_dir_edit.setText(str(app_paths.data_dir / "no-keys"))
    wizard.venue_page.polymarket_checkbox.setChecked(True)
    wizard.venue_page.kalshi_checkbox.setChecked(False)
    wizard.credentials_page.set_enabled_providers(["polymarket"])
    wizard.accept()

    created = store.get_profile(wizard.created_profile_id or "")
    assert created is not None
    assert created.enabled_venues == ["Polymarket"]
    assert "Run one paper route and use Score as the main progression surface." in wizard.finish_page.summary_label.text()
    assert fake_keyring.store == {}


def test_setup_wizard_surfaces_recommended_plan(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    wizard = SetupWizard(
        profile_store=store,
        credential_vault=CredentialVault(backend=fake_keyring),
        startup_manager=UnsupportedStartupManager(),
        preset_labels=[
            ("continuous-record", "Continuous recorder"),
            ("fast-smoke-run", "Fast smoke run"),
        ],
    )
    qtbot.addWidget(wizard)

    wizard.intent_page.goal_combo.setCurrentIndex(wizard.intent_page.goal_combo.findData("live_prepare"))
    wizard.intent_page.experience_combo.setCurrentIndex(wizard.intent_page.experience_combo.findData("advanced"))

    assert "Recommended template: Research" in wizard.intent_page.plan_label.text()
    assert "Recommended risk policy: Balanced" in wizard.intent_page.plan_label.text()
    assert "Current preset: Continuous recorder" in wizard.risk_page.recommendation_label.text()


def test_main_window_runs_default_preset(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Window Profile",
        template="Recorder",
        enabled_venues=["Polymarket"],
        default_preset="continuous-record",
    )

    def fake_record_runner(settings: RecorderSettings, preset: Any, stop_requested: Any) -> None:
        settings.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        settings.duckdb_path.touch()
        deadline = time.time() + 0.3
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
    window = _desktop_window(
        app_paths=app_paths,
        store=store,
        fake_keyring=fake_keyring,
        controller=controller,
    )
    qtbot.addWidget(window)
    window.show()

    selector_index = window.profile_selector.findData(profile.id)
    window.profile_selector.setCurrentIndex(selector_index)
    window._start_default_preset()  # noqa: SLF001
    qtbot.waitUntil(
        lambda: controller.status(profile).state in {"running", "completed"},
        timeout=1500,
    )
    if controller.status(profile).state == "running":
        controller.stop()
    qtbot.waitUntil(lambda: controller.status(profile).state == "completed", timeout=3000)
    window._refresh_status_only()  # noqa: SLF001
    assert "Completed" in window.home_tab.engine_label.text()
    assert window.home_tab.secondary_actions_widget.isVisible() is True
    assert window.home_tab.replay_button.isEnabled() is True
    assert window.home_tab.scan_button.isEnabled() is True
    controller.shutdown()


def test_main_window_empty_state_surfaces_guided_setup(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    controller = EngineController(RecorderSettings())
    window = _desktop_window(
        app_paths=app_paths,
        store=store,
        fake_keyring=fake_keyring,
        controller=controller,
        allow_setup_wizard_on_empty_profiles=False,
    )
    qtbot.addWidget(window)
    window.show()

    assert window.home_tab.setup_progress_label.text() == "Setup checklist"
    assert "[>] Create first profile." in window.home_tab.setup_steps_label.text()
    assert window.home_tab.open_setup_button.text() == "Create first profile"
    assert window.home_tab.start_button.isEnabled() is False
    assert window.home_tab.secondary_actions_widget.isVisible() is False
    assert window.home_tab.view_docs_button.isEnabled() is True
    label_text = " ".join(label.text() for label in window.findChildren(QLabel))
    assert "CONTROL  Hangar | Loadout" not in label_text
    assert "OPERATIONS  Scanner | Paper" not in label_text
    controller.shutdown()


def test_main_window_switches_primary_action_to_start_session(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Session Ready",
        template="Recorder",
        enabled_venues=["Polymarket"],
        equipped_connectors=["polymarket"],
        equipped_modules=["internal-binary"],
    )
    db_path = profile.data_dir / "market_data.duckdb"
    storage = DuckDBStorage(db_path)
    try:
        market = PolymarketMarket.model_validate(
            {
                "id": "market-session",
                "conditionId": "condition-session",
                "question": "Will the session start?",
                "slug": "will-the-session-start",
                "active": True,
                "enableOrderBook": True,
                "outcomes": '["Yes", "No"]',
                "clobTokenIds": '["yes-session", "no-session"]',
            }
        )
        event = PolymarketEvent.model_validate({"id": "event-session", "title": "Session", "active": True})
        storage.store_discovery_snapshot([DiscoveredMarket(event=event, market=market)])
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="yes-session",
                market="market-session",
                best_bid="0.45",
                best_ask="0.47",
                spread="0.02",
                timestamp="1",
            )
        )
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="no-session",
                market="market-session",
                best_bid="0.46",
                best_ask="0.48",
                spread="0.02",
                timestamp="2",
            )
        )
    finally:
        storage.close()

    controller = EngineController(RecorderSettings())
    window = _desktop_window(
        app_paths=app_paths,
        store=store,
        fake_keyring=fake_keyring,
        controller=controller,
    )
    qtbot.addWidget(window)
    window.show()

    selector_index = window.profile_selector.findData(profile.id)
    window.profile_selector.setCurrentIndex(selector_index)
    window._refresh_scanner()  # noqa: SLF001
    window._refresh_status_only()  # noqa: SLF001

    assert window.home_tab.start_button.text() == "Start session"
    assert "Start a paper session" in window.home_tab.primary_action_hint.text()
    controller.shutdown()


def test_smoke_report_captures_window_state(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    store.create_profile(
        display_name="Smoke Report",
        template="Recorder",
        enabled_venues=["Polymarket"],
    )
    controller = EngineController(RecorderSettings())
    window = _desktop_window(
        app_paths=app_paths,
        store=store,
        fake_keyring=fake_keyring,
        controller=controller,
    )
    qtbot.addWidget(window)
    window.show()

    app = QApplication.instance()
    assert app is not None
    report = _smoke_report(cast(QApplication, app), window)

    assert report["app_name"] == "pytest-qt-qapp"
    assert report["window_title"] == "Superior"
    assert report["window_visible"] is True
    assert isinstance(report["window_icon_present"], bool)
    controller.shutdown()


def test_parser_requires_smoke_output_with_smoke_test() -> None:
    try:
        main(["--smoke-test"])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover - defensive
        raise AssertionError("expected parser to reject --smoke-test without --smoke-output")


def test_arbitrage_tab_shows_no_data_placeholder(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    from market_data_recorder_desktop.window import ArbitrageTab

    tab = ArbitrageTab()
    qtbot.addWidget(tab)
    tab.show()

    assert tab.opportunity_list.count() == 0
    assert "No data yet" in tab.details_text.toPlainText()


def test_arbitrage_tab_update_opportunities_populates_list(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    from market_data_recorder.models import ArbitrageLeg, ArbitrageOpportunity
    from market_data_recorder_desktop.window import ArbitrageTab

    tab = ArbitrageTab()
    qtbot.addWidget(tab)
    tab.show()

    opportunities = [
        ArbitrageOpportunity(
            market="test-market",
            strategy="buy_all_outcomes",
            timestamp="1000",
            total_price="0.95",
            guaranteed_profit="0.05",
            outcome_count=2,
            legs=[
                ArbitrageLeg(asset_id="yes-token", outcome="Yes", best_bid="0.44", best_ask="0.45"),
                ArbitrageLeg(asset_id="no-token", outcome="No", best_bid="0.49", best_ask="0.50"),
            ],
        )
    ]
    tab.update_opportunities(opportunities)

    assert tab.opportunity_list.count() == 1
    assert "[BUY]" in tab.opportunity_list.item(0).text()
    assert "+5.00%" in tab.opportunity_list.item(0).text()


def test_arbitrage_tab_set_detail_shows_legs(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    from market_data_recorder.models import ArbitrageLeg, ArbitrageOpportunity
    from market_data_recorder_desktop.window import ArbitrageTab

    tab = ArbitrageTab()
    qtbot.addWidget(tab)
    tab.show()

    opp = ArbitrageOpportunity(
        market="sell-market",
        strategy="sell_all_outcomes",
        timestamp="2000",
        total_price="1.05",
        guaranteed_profit="0.05",
        outcome_count=2,
        legs=[
            ArbitrageLeg(asset_id="yes-token", outcome="Yes", best_bid="0.56", best_ask="0.57"),
            ArbitrageLeg(asset_id="no-token", outcome="No", best_bid="0.49", best_ask="0.50"),
        ],
    )
    tab.set_detail(opp)

    detail_text = tab.details_text.toPlainText()
    assert "sell-market" in detail_text
    assert "Sell all outcomes" in detail_text
    assert "yes-token" in detail_text
    assert "no-token" in detail_text
    assert "+5.0000%" in detail_text


def test_desktop_window_has_arbitrage_tab(
    qtbot: Any,
    app_paths: AppPaths,
    fake_keyring: Any,
) -> None:
    store = ProfileStore(app_paths)
    controller = EngineController(RecorderSettings())
    window = _desktop_window(
        app_paths=app_paths,
        store=store,
        fake_keyring=fake_keyring,
        controller=controller,
    )
    qtbot.addWidget(window)
    window.show()

    tab_titles = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Arbitrage" in tab_titles
    assert hasattr(window, "arb_tab")
    controller.shutdown()
