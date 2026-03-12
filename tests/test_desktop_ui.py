from __future__ import annotations

import time
from typing import Any, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit

from market_data_recorder.config import RecorderSettings
from market_data_recorder_desktop.controller import EngineController
from market_data_recorder_desktop.credentials import CredentialVault
from market_data_recorder_desktop.diagnostics import DiagnosticsService
from market_data_recorder_desktop.main import _smoke_report, main
from market_data_recorder_desktop.paths import AppPaths
from market_data_recorder_desktop.profiles import ProfileStore
from market_data_recorder_desktop.startup import UnsupportedStartupManager
from market_data_recorder_desktop.window import DesktopMainWindow
from market_data_recorder_desktop.wizard import SetupWizard


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
    wizard.recorder_page.market_filters_edit.setText("sports, elections")
    wizard.accept()

    created = store.get_profile(wizard.created_profile_id or "")
    assert created is not None
    assert created.display_name == "Wizard Profile"
    profiles_json = store.profiles_path.read_text(encoding="utf-8")
    assert "secret-value" not in profiles_json
    assert fake_keyring.store


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
    window = DesktopMainWindow(
        paths=app_paths,
        profile_store=store,
        credential_vault=CredentialVault(backend=fake_keyring),
        controller=controller,
        diagnostics=DiagnosticsService(app_paths),
        startup_manager=UnsupportedStartupManager(),
    )
    qtbot.addWidget(window)
    window.show()

    selector_index = window.profile_selector.findData(profile.id)
    window.profile_selector.setCurrentIndex(selector_index)
    qtbot.mouseClick(window.dashboard_tab.start_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: controller.status(profile).state == "running", timeout=1500)
    controller.stop()
    qtbot.waitUntil(lambda: controller.status(profile).state == "completed", timeout=3000)
    window._refresh_status()  # noqa: SLF001
    assert window.dashboard_tab.state_label.text() == "Completed"
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
    window = DesktopMainWindow(
        paths=app_paths,
        profile_store=store,
        credential_vault=CredentialVault(backend=fake_keyring),
        controller=controller,
        diagnostics=DiagnosticsService(app_paths),
        startup_manager=UnsupportedStartupManager(),
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
