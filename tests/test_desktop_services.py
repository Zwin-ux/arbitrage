from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from market_data_recorder.config import RecorderSettings
from market_data_recorder_desktop.controller import EngineController
from market_data_recorder_desktop.credentials import CredentialVault
from market_data_recorder_desktop.paths import AppPaths
from market_data_recorder_desktop.profiles import ProfileStore
from market_data_recorder_desktop.startup import WindowsStartupManager


def test_profile_store_round_trip_and_import_export(app_paths: AppPaths) -> None:
    store = ProfileStore(app_paths)
    created = store.create_profile(
        display_name="Primary",
        template="Recorder",
        enabled_venues=["Polymarket"],
        market_filters=["elections"],
        auto_start=True,
        default_preset="continuous-record",
    )

    duplicate = store.duplicate_profile(created.id)
    export_path = app_paths.exports_dir / "profile.json"
    store.export_profile(created.id, export_path)
    imported = store.import_profile(export_path)

    profiles = store.list_profiles()
    assert len(profiles) == 3
    assert store.auto_start_profile() is not None
    assert duplicate.display_name.endswith("Copy")
    assert imported.id != created.id
    assert "elections" in created.market_filters


def test_credential_vault_uses_keyring_only(app_paths: AppPaths, fake_keyring: Any) -> None:
    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Secrets",
        template="Recorder",
        enabled_venues=["Polymarket"],
    )
    vault = CredentialVault(backend=fake_keyring)
    result = vault.save(
        profile.id,
        "polymarket",
        {
            "api_key": "public-key",
            "api_secret": "super-secret",
            "api_passphrase": "secret-passphrase",
        },
    )

    assert result.status == "validated"
    assert "super-secret" not in store.profiles_path.read_text(encoding="utf-8")
    assert fake_keyring.store
    status = vault.status(profile.id, "polymarket")
    assert status.status == "validated"


def test_engine_controller_runs_and_stops(app_paths: AppPaths) -> None:
    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Runner",
        template="Recorder",
        enabled_venues=["Polymarket"],
    )

    def fake_record_runner(
        settings: RecorderSettings,
        preset: Any,
        stop_requested: Any,
    ) -> None:
        settings.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        settings.duckdb_path.touch()
        deadline = time.time() + 1.0
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
        deadline = time.time() + 1.0
        while time.time() < deadline:
            if controller.status(profile).state == "running":
                break
            time.sleep(0.01)
        assert controller.status(profile).state == "running"

        controller.stop()
        deadline = time.time() + 2.0
        while time.time() < deadline:
            if controller.status(profile).state == "completed":
                break
            time.sleep(0.02)
        assert controller.status(profile).state == "completed"
    finally:
        controller.shutdown()


def test_windows_startup_manager_writes_launcher(tmp_path: Path) -> None:
    manager = WindowsStartupManager(startup_dir=tmp_path)
    manager.set_enabled(True)
    assert manager.is_enabled()
    launcher = tmp_path / "market-data-recorder-app.cmd"
    assert launcher.exists()
    manager.set_enabled(False)
    assert not launcher.exists()


def test_arbitrage_service_returns_empty_when_no_db(app_paths: AppPaths) -> None:
    from market_data_recorder_desktop.bot_services import ArbitrageService
    from market_data_recorder_desktop.profiles import ProfileStore

    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Arb",
        template="Recorder",
        enabled_venues=["Polymarket"],
    )
    service = ArbitrageService()
    result = service.find_opportunities(profile, min_edge="0")
    assert result == []


def test_arbitrage_service_finds_buy_all_outcomes_opportunity(app_paths: AppPaths) -> None:
    from datetime import datetime, timezone

    from market_data_recorder.models import BestBidAskEvent
    from market_data_recorder.storage import DuckDBStorage
    from market_data_recorder_desktop.bot_services import ArbitrageService
    from market_data_recorder_desktop.profiles import ProfileStore

    store = ProfileStore(app_paths)
    profile = store.create_profile(
        display_name="Arb",
        template="Recorder",
        enabled_venues=["Polymarket"],
    )
    db_path = profile.data_dir / "market_data.duckdb"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    storage = DuckDBStorage(db_path)
    try:
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="yes-token",
                market="market-a",
                best_bid="0.45",
                best_ask="0.47",
                spread=None,
                timestamp="1000",
            ),
            recorded_at=datetime.now(timezone.utc),
        )
        storage.store_best_bid_ask(
            BestBidAskEvent(
                event_type="best_bid_ask",
                asset_id="no-token",
                market="market-a",
                best_bid="0.48",
                best_ask="0.50",
                spread=None,
                timestamp="1000",
            ),
            recorded_at=datetime.now(timezone.utc),
        )
    finally:
        storage.close()

    service = ArbitrageService()
    opportunities = service.find_opportunities(profile, min_edge="0.01")
    assert len(opportunities) == 1
    assert opportunities[0].market == "market-a"
    assert opportunities[0].strategy == "buy_all_outcomes"
    assert float(opportunities[0].guaranteed_profit) > 0.01
