from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .app_types import AppProfile, CredentialStatus, EngineStatus, RunPreset
from .controller import EngineController
from .credentials import CredentialProvider, CredentialVault
from .diagnostics import DiagnosticsService
from .paths import AppPaths
from .profiles import ProfileStore
from .startup import StartupManager
from .wizard import SetupWizard


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class DashboardTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self.hero_label = QLabel("Superior control room")
        self.hero_label.setObjectName("heroTitle")
        self.subtitle_label = QLabel("Choose a profile, then record, replay, or verify without touching the terminal.")
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.hero_label)
        layout.addWidget(self.subtitle_label)

        actions = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.replay_button = QPushButton("Replay")
        self.verify_button = QPushButton("Verify")
        self.manage_profiles_button = QPushButton("Manage Profiles")
        for button in (
            self.start_button,
            self.stop_button,
            self.replay_button,
            self.verify_button,
            self.manage_profiles_button,
        ):
            actions.addWidget(button)
        layout.addLayout(actions)

        status_group = QGroupBox("Status")
        status_layout = QFormLayout(status_group)
        self.profile_label = QLabel("No profile selected")
        self.state_label = QLabel("Idle")
        self.message_label = QLabel("Ready.")
        self.message_label.setWordWrap(True)
        self.db_path_label = QLabel("No database yet")
        self.counts_label = QLabel("0 raw messages | 0 books | 0 health events")
        self.warning_label = QLabel("No recent warnings")
        self.warning_label.setWordWrap(True)
        status_layout.addRow("Profile", self.profile_label)
        status_layout.addRow("Engine", self.state_label)
        status_layout.addRow("Last message", self.message_label)
        status_layout.addRow("Data path", self.db_path_label)
        status_layout.addRow("Stored data", self.counts_label)
        status_layout.addRow("Latest warning", self.warning_label)
        layout.addWidget(status_group)
        layout.addStretch(1)

    def update_view(self, profile: AppProfile | None, status: EngineStatus) -> None:
        self.profile_label.setText(profile.display_name if profile is not None else "No profile selected")
        self.state_label.setText(status.state.title())
        self.message_label.setText(status.last_message)
        if status.summary is None:
            self.db_path_label.setText("No database yet")
            self.counts_label.setText("0 raw messages | 0 books | 0 health events")
            self.warning_label.setText("No recent warnings")
            return
        self.db_path_label.setText(str(status.summary.db_path))
        self.counts_label.setText(
            f"{status.summary.raw_messages} raw messages | "
            f"{status.summary.book_snapshots} books | "
            f"{status.summary.health_events} health events"
        )
        self.warning_label.setText(status.summary.latest_warning or "No recent warnings")


class ProfilesTab(QWidget):
    def __init__(self, presets: list[RunPreset]) -> None:
        super().__init__()
        self._profiles: dict[str, AppProfile] = {}
        self._presets = presets

        root = QHBoxLayout(self)

        left = QVBoxLayout()
        self.profile_list = QListWidget()
        left.addWidget(self.profile_list)
        buttons = QHBoxLayout()
        self.new_button = QPushButton("New")
        self.duplicate_button = QPushButton("Duplicate")
        self.delete_button = QPushButton("Delete")
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.duplicate_button)
        buttons.addWidget(self.delete_button)
        left.addLayout(buttons)
        export_buttons = QHBoxLayout()
        self.export_button = QPushButton("Export")
        self.import_button = QPushButton("Import")
        export_buttons.addWidget(self.export_button)
        export_buttons.addWidget(self.import_button)
        left.addLayout(export_buttons)
        root.addLayout(left, stretch=1)

        right = QVBoxLayout()
        form_group = QGroupBox("Profile details")
        form = QFormLayout(form_group)
        self.display_name_edit = QLineEdit()
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Recorder", "Research", "Custom"])
        self.data_dir_edit = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_data_dir)
        data_dir_row = QHBoxLayout()
        data_dir_row.addWidget(self.data_dir_edit, stretch=1)
        data_dir_row.addWidget(browse_button)
        self.market_filters_edit = QLineEdit()
        self.market_filters_edit.setPlaceholderText("elections, sports, crypto")
        self.default_preset_combo = QComboBox()
        for preset in self._presets:
            self.default_preset_combo.addItem(preset.label, preset.id)
        self.notes_edit = QTextEdit()
        self.auto_start_checkbox = QCheckBox("Run app at login")
        self.start_minimized_checkbox = QCheckBox("Start minimized to tray")
        self.polymarket_checkbox = QCheckBox("Polymarket")
        self.kalshi_checkbox = QCheckBox("Kalshi")
        venues_row = QHBoxLayout()
        venues_row.addWidget(self.polymarket_checkbox)
        venues_row.addWidget(self.kalshi_checkbox)

        form.addRow("Display name", self.display_name_edit)
        form.addRow("Template", self.template_combo)
        form.addRow("Data directory", self._wrap_layout(data_dir_row))
        form.addRow("Market filters", self.market_filters_edit)
        form.addRow("Default preset", self.default_preset_combo)
        form.addRow("Venues", self._wrap_layout(venues_row))
        form.addRow("Notes", self.notes_edit)
        right.addWidget(form_group)
        right.addWidget(self.auto_start_checkbox)
        right.addWidget(self.start_minimized_checkbox)
        self.startup_hint = QLabel()
        self.startup_hint.setWordWrap(True)
        right.addWidget(self.startup_hint)
        self.save_button = QPushButton("Save Profile")
        right.addWidget(self.save_button)
        right.addStretch(1)
        root.addLayout(right, stretch=2)

        self.profile_list.currentItemChanged.connect(self._on_selection_changed)

    def load_profiles(
        self,
        profiles: list[AppProfile],
        *,
        selected_profile_id: str | None,
        startup_description: str,
    ) -> None:
        self._profiles = {profile.id: profile for profile in profiles}
        self.startup_hint.setText(startup_description)
        self.profile_list.blockSignals(True)
        self.profile_list.clear()
        selected_item: QListWidgetItem | None = None
        for profile in profiles:
            item = QListWidgetItem(profile.display_name)
            item.setData(Qt.ItemDataRole.UserRole, profile.id)
            self.profile_list.addItem(item)
            if profile.id == selected_profile_id:
                selected_item = item
        self.profile_list.blockSignals(False)
        if selected_item is not None:
            self.profile_list.setCurrentItem(selected_item)
        elif self.profile_list.count() > 0:
            self.profile_list.setCurrentRow(0)
        else:
            self._clear_form()

    def current_profile(self) -> AppProfile | None:
        item = self.profile_list.currentItem()
        if item is None:
            return None
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        return self._profiles.get(profile_id)

    def edited_profile(self) -> AppProfile | None:
        profile = self.current_profile()
        if profile is None:
            return None
        venues: list[str] = []
        if self.polymarket_checkbox.isChecked():
            venues.append("Polymarket")
        if self.kalshi_checkbox.isChecked():
            venues.append("Kalshi")
        return profile.model_copy(
            update={
                "display_name": self.display_name_edit.text().strip() or profile.display_name,
                "template": self.template_combo.currentText(),
                "data_dir": Path(self.data_dir_edit.text().strip() or str(profile.data_dir)),
                "market_filters": [
                    item.strip() for item in self.market_filters_edit.text().split(",") if item.strip()
                ],
                "default_preset": self.default_preset_combo.currentData(),
                "enabled_venues": venues or ["Polymarket"],
                "notes": self.notes_edit.toPlainText().strip() or None,
                "auto_start": self.auto_start_checkbox.isChecked(),
                "start_minimized": self.start_minimized_checkbox.isChecked(),
            }
        )

    def _on_selection_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if current is None:
            self._clear_form()
            return
        profile_id = current.data(Qt.ItemDataRole.UserRole)
        profile = self._profiles.get(profile_id)
        if profile is None:
            self._clear_form()
            return
        self.display_name_edit.setText(profile.display_name)
        self.template_combo.setCurrentText(profile.template)
        self.data_dir_edit.setText(str(profile.data_dir))
        self.market_filters_edit.setText(", ".join(profile.market_filters))
        preset_index = self.default_preset_combo.findData(profile.default_preset)
        if preset_index >= 0:
            self.default_preset_combo.setCurrentIndex(preset_index)
        self.notes_edit.setPlainText(profile.notes or "")
        self.auto_start_checkbox.setChecked(profile.auto_start)
        self.start_minimized_checkbox.setChecked(profile.start_minimized)
        self.polymarket_checkbox.setChecked("Polymarket" in profile.enabled_venues)
        self.kalshi_checkbox.setChecked("Kalshi" in profile.enabled_venues)

    def _clear_form(self) -> None:
        self.display_name_edit.clear()
        self.template_combo.setCurrentIndex(0)
        self.data_dir_edit.clear()
        self.market_filters_edit.clear()
        self.notes_edit.clear()
        self.auto_start_checkbox.setChecked(False)
        self.start_minimized_checkbox.setChecked(False)
        self.polymarket_checkbox.setChecked(True)
        self.kalshi_checkbox.setChecked(False)

    def _browse_data_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Choose data directory")
        if directory:
            self.data_dir_edit.setText(directory)

    @staticmethod
    def _wrap_layout(layout: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget


class CredentialProviderBox(QGroupBox):
    def __init__(self, provider: CredentialProvider):
        super().__init__(provider.provider_label)
        self.provider = provider
        self.fields: dict[str, QLineEdit | QPlainTextEdit] = {}

        layout = QVBoxLayout(self)
        form = QFormLayout()
        for field in provider.fields():
            if field.multiline:
                widget: QLineEdit | QPlainTextEdit = QPlainTextEdit()
                widget.setPlaceholderText(field.placeholder or "")
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(field.placeholder or "")
                if field.secret:
                    widget.setEchoMode(QLineEdit.EchoMode.Password)
            widget.setToolTip(field.help_text)
            self.fields[field.key] = widget
            form.addRow(field.label, widget)
        layout.addLayout(form)
        button_row = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.validate_button = QPushButton("Validate")
        self.delete_button = QPushButton("Delete")
        self.docs_button = QPushButton("Docs")
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.validate_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.docs_button)
        layout.addLayout(button_row)
        self.status_label = QLabel("Not configured")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        for key, widget in self.fields.items():
            if isinstance(widget, QPlainTextEdit):
                payload[key] = widget.toPlainText()
            else:
                payload[key] = widget.text()
        return payload

    def clear_input(self) -> None:
        for widget in self.fields.values():
            widget.clear()

    def update_status(self, status: CredentialStatus) -> None:
        self.status_label.setText(f"{status.status.title()}: {status.message}")


class CredentialsTab(QWidget):
    def __init__(self, providers: list[CredentialProvider]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.profile_label = QLabel("Choose a profile to manage keys.")
        self.profile_label.setWordWrap(True)
        layout.addWidget(self.profile_label)
        self.provider_boxes: dict[str, CredentialProviderBox] = {}
        for provider in providers:
            box = CredentialProviderBox(provider)
            self.provider_boxes[provider.provider_id] = box
            layout.addWidget(box)
        layout.addStretch(1)

    def set_profile(self, profile: AppProfile | None, statuses: list[CredentialStatus]) -> None:
        self.profile_label.setText(
            f"Credentials for {profile.display_name}" if profile is not None else "Choose a profile to manage keys."
        )
        status_by_provider = {status.provider_id: status for status in statuses}
        for provider_id, box in self.provider_boxes.items():
            if provider_id in status_by_provider:
                box.update_status(status_by_provider[provider_id])
            else:
                box.status_label.setText("Not configured")


class DiagnosticsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export Bundle")
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.export_button)
        layout.addLayout(actions)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)


class AboutTab(QWidget):
    def __init__(self, paths: AppPaths) -> None:
        super().__init__()
        self._paths = paths
        layout = QVBoxLayout(self)
        title = QLabel("Trust and About")
        title.setObjectName("heroTitle")
        layout.addWidget(title)
        text = QLabel(
            "Superior is MIT-licensed, open source, and local-first. "
            "Secrets go to the OS keychain, telemetry is off by default, and build scripts live in the repo."
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        info_group = QGroupBox("Paths")
        info_form = QFormLayout(info_group)
        info_form.addRow("Config", QLabel(str(paths.config_dir)))
        info_form.addRow("Data", QLabel(str(paths.data_dir)))
        info_form.addRow("Logs", QLabel(str(paths.log_dir)))
        layout.addWidget(info_group)
        buttons = QHBoxLayout()
        self.source_button = QPushButton("Source Tree")
        self.readme_button = QPushButton("README")
        self.license_button = QPushButton("LICENSE")
        self.notices_button = QPushButton("3rd Party Notices")
        self.security_button = QPushButton("Security")
        buttons.addWidget(self.source_button)
        buttons.addWidget(self.readme_button)
        buttons.addWidget(self.license_button)
        buttons.addWidget(self.notices_button)
        buttons.addWidget(self.security_button)
        layout.addLayout(buttons)
        layout.addStretch(1)


class DesktopMainWindow(QMainWindow):
    def __init__(
        self,
        *,
        paths: AppPaths,
        profile_store: ProfileStore,
        credential_vault: CredentialVault,
        controller: EngineController,
        diagnostics: DiagnosticsService,
        startup_manager: StartupManager,
        allow_setup_wizard_on_empty_profiles: bool = True,
        show_tray_icon: bool = True,
    ) -> None:
        super().__init__()
        self._paths = paths
        self._profile_store = profile_store
        self._credential_vault = credential_vault
        self._controller = controller
        self._diagnostics = diagnostics
        self._startup_manager = startup_manager
        self._profiles: list[AppProfile] = []
        self._previous_state = "idle"

        self.setWindowTitle("Superior")
        self.resize(1180, 820)

        self.dashboard_tab = DashboardTab()
        self.profiles_tab = ProfilesTab(controller.presets())
        self.credentials_tab = CredentialsTab(credential_vault.providers())
        self.diagnostics_tab = DiagnosticsTab()
        self.about_tab = AboutTab(paths)

        self.profile_selector = QComboBox()
        self.profile_selector.currentIndexChanged.connect(self._on_profile_changed)
        self.setup_button = QPushButton("Open Setup Wizard")
        self.setup_button.clicked.connect(self._open_setup_wizard)

        header = QHBoxLayout()
        header.addWidget(QLabel("Active profile"))
        header.addWidget(self.profile_selector, stretch=1)
        header.addWidget(self.setup_button)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.dashboard_tab, "Home")
        self.tabs.addTab(self.profiles_tab, "Profiles")
        self.tabs.addTab(self.credentials_tab, "Credentials")
        self.tabs.addTab(self.diagnostics_tab, "Diagnostics")
        self.tabs.addTab(self.about_tab, "About")

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.addLayout(header)
        central_layout.addWidget(self.tabs)
        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar(self))

        self._setup_connections()
        self._setup_tray(show_tray_icon=show_tray_icon)

        self._refresh_profiles()
        self._refresh_status()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_status)
        self._refresh_timer.start(1000)

        if allow_setup_wizard_on_empty_profiles and not self._profiles:
            QTimer.singleShot(0, self._open_setup_wizard)

    def handle_auto_launch(self, profile_id: str | None = None) -> None:
        profile = self._find_profile(profile_id) if profile_id else None
        if profile is None:
            profile = self._profile_store.auto_start_profile()
        if profile is None:
            return
        selector_index = self.profile_selector.findData(profile.id)
        if selector_index >= 0:
            self.profile_selector.setCurrentIndex(selector_index)
        self._run_preset(profile.default_preset)
        if profile.start_minimized and self._tray.isVisible():
            self.hide()

    def closeEvent(self, event: QCloseEvent) -> None:
        status = self._controller.status(self._current_profile())
        if status.state == "running" and self._tray.isVisible():
            result = QMessageBox.question(
                self,
                "Recorder still running",
                "The recorder is still running. Keep it alive in the tray?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if result == QMessageBox.StandardButton.Yes:
                self.hide()
                event.ignore()
                return
            if result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        self._controller.shutdown()
        self._tray.hide()
        event.accept()

    def _setup_connections(self) -> None:
        self.dashboard_tab.start_button.clicked.connect(self._start_default_preset)
        self.dashboard_tab.stop_button.clicked.connect(self._stop_run)
        self.dashboard_tab.replay_button.clicked.connect(lambda: self._run_preset("replay-latest"))
        self.dashboard_tab.verify_button.clicked.connect(lambda: self._run_preset("verify-latest"))
        self.dashboard_tab.manage_profiles_button.clicked.connect(
            lambda: self.tabs.setCurrentWidget(self.profiles_tab)
        )

        self.profiles_tab.new_button.clicked.connect(self._open_setup_wizard)
        self.profiles_tab.duplicate_button.clicked.connect(self._duplicate_profile)
        self.profiles_tab.delete_button.clicked.connect(self._delete_profile)
        self.profiles_tab.export_button.clicked.connect(self._export_profile)
        self.profiles_tab.import_button.clicked.connect(self._import_profile)
        self.profiles_tab.save_button.clicked.connect(self._save_profile)

        self.diagnostics_tab.refresh_button.clicked.connect(self._refresh_status)
        self.diagnostics_tab.export_button.clicked.connect(self._export_diagnostics)

        for provider_id, box in self.credentials_tab.provider_boxes.items():
            box.save_button.clicked.connect(lambda _checked=False, pid=provider_id: self._save_credentials(pid))
            box.validate_button.clicked.connect(
                lambda _checked=False, pid=provider_id: self._validate_credentials(pid)
            )
            box.delete_button.clicked.connect(lambda _checked=False, pid=provider_id: self._delete_credentials(pid))
            box.docs_button.clicked.connect(
                lambda _checked=False, pid=provider_id: self._open_url(self._credential_vault.provider(pid).docs_url)
            )

        self.about_tab.source_button.clicked.connect(lambda: self._open_local(_project_root()))
        self.about_tab.readme_button.clicked.connect(lambda: self._open_local(_project_root() / "README.md"))
        self.about_tab.license_button.clicked.connect(lambda: self._open_local(_project_root() / "LICENSE"))
        self.about_tab.notices_button.clicked.connect(
            lambda: self._open_local(_project_root() / "THIRD_PARTY_NOTICES.md")
        )
        self.about_tab.security_button.clicked.connect(lambda: self._open_local(_project_root() / "SECURITY.md"))

    def _setup_tray(self, *, show_tray_icon: bool) -> None:
        icon = self.windowIcon()
        if icon.isNull():
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self._tray = QSystemTrayIcon(icon, self)
        tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_from_tray)
        start_action = QAction("Start Default", self)
        start_action.triggered.connect(self._start_default_preset)
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._stop_run)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(show_action)
        tray_menu.addAction(start_action)
        tray_menu.addAction(stop_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        if show_tray_icon:
            self._tray.show()

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_from_tray()

    def _open_setup_wizard(self) -> None:
        wizard = SetupWizard(
            profile_store=self._profile_store,
            credential_vault=self._credential_vault,
            startup_manager=self._startup_manager,
            preset_labels=[(preset.id, preset.label) for preset in self._controller.presets()],
            parent=self,
        )
        if wizard.exec() == SetupWizard.DialogCode.Accepted:
            self._sync_startup_manager()
            self._refresh_profiles(wizard.created_profile_id)
            self.statusBar().showMessage("Profile created.", 4000)

    def _refresh_profiles(self, preferred_profile_id: str | None = None) -> None:
        current_profile = self._current_profile()
        self._profiles = self._profile_store.list_profiles()
        selected_id = preferred_profile_id or (current_profile.id if current_profile is not None else None)
        self.profile_selector.blockSignals(True)
        self.profile_selector.clear()
        for profile in self._profiles:
            self.profile_selector.addItem(profile.display_name, profile.id)
        self.profile_selector.blockSignals(False)
        if self._profiles:
            target_id = selected_id or self._profiles[0].id
            index = self.profile_selector.findData(target_id)
            if index < 0:
                index = 0
            self.profile_selector.setCurrentIndex(index)
        self.profiles_tab.load_profiles(
            self._profiles,
            selected_profile_id=self._current_profile_id(),
            startup_description=self._startup_manager.description(),
        )
        self._refresh_credentials_tab()

    def _refresh_credentials_tab(self) -> None:
        profile = self._current_profile()
        statuses = self._credential_vault.statuses_for_profile(profile.id) if profile is not None else []
        self.credentials_tab.set_profile(profile, statuses)

    def _current_profile_id(self) -> str | None:
        data = self.profile_selector.currentData()
        return data if isinstance(data, str) else None

    def _current_profile(self) -> AppProfile | None:
        return self._find_profile(self._current_profile_id())

    def _find_profile(self, profile_id: str | None) -> AppProfile | None:
        if profile_id is None:
            return None
        for profile in self._profiles:
            if profile.id == profile_id:
                return profile
        return None

    def _on_profile_changed(self) -> None:
        self.profiles_tab.load_profiles(
            self._profiles,
            selected_profile_id=self._current_profile_id(),
            startup_description=self._startup_manager.description(),
        )
        self._refresh_credentials_tab()
        self._refresh_status()

    def _refresh_status(self) -> None:
        profile = self._current_profile()
        status = self._controller.status(profile)
        self.dashboard_tab.update_view(profile, status)
        credential_statuses = self._credential_vault.statuses_for_profile(profile.id) if profile is not None else []
        self.credentials_tab.set_profile(profile, credential_statuses)
        self.diagnostics_tab.text.setPlainText(
            self._diagnostics.diagnostics_text(
                profile=profile,
                status=status,
                credential_statuses=credential_statuses,
            )
        )
        if self._previous_state == "running" and status.state in {"completed", "failed"}:
            self._tray.showMessage("Superior", status.last_message, self._tray.icon(), 5000)
        self._previous_state = status.state

    def _start_default_preset(self) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Create a profile", "Create a profile before starting the recorder.")
            return
        self._run_preset(profile.default_preset)

    def _run_preset(self, preset_id: str) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Create a profile", "Create a profile before starting the recorder.")
            return
        try:
            self._controller.run_preset(profile, preset_id)
        except Exception as exc:
            QMessageBox.warning(self, "Unable to start", str(exc))
            return
        self.statusBar().showMessage(f"Started {preset_id} for {profile.display_name}.", 4000)
        self._refresh_status()

    def _stop_run(self) -> None:
        self._controller.stop()
        self.statusBar().showMessage("Stop requested.", 4000)

    def _save_profile(self) -> None:
        profile = self.profiles_tab.edited_profile()
        if profile is None:
            QMessageBox.information(self, "No profile selected", "Choose a profile to edit first.")
            return
        saved = self._profile_store.save_profile(profile)
        self._sync_startup_manager()
        self._refresh_profiles(saved.id)
        self.statusBar().showMessage("Profile saved.", 4000)

    def _duplicate_profile(self) -> None:
        profile = self.profiles_tab.current_profile()
        if profile is None:
            return
        duplicate = self._profile_store.duplicate_profile(profile.id)
        self._refresh_profiles(duplicate.id)
        self.statusBar().showMessage("Profile duplicated.", 4000)

    def _delete_profile(self) -> None:
        profile = self.profiles_tab.current_profile()
        if profile is None:
            return
        result = QMessageBox.question(
            self,
            "Delete profile",
            f"Delete {profile.display_name}? This does not remove secrets from the OS keychain.",
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        self._profile_store.delete_profile(profile.id)
        self._refresh_profiles()
        self._sync_startup_manager()
        self.statusBar().showMessage("Profile deleted.", 4000)

    def _export_profile(self) -> None:
        profile = self.profiles_tab.current_profile()
        if profile is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export profile",
            str(self._paths.exports_dir / f"{profile.display_name.replace(' ', '_')}.json"),
            "JSON (*.json)",
        )
        if not filename:
            return
        self._profile_store.export_profile(profile.id, Path(filename))
        self.statusBar().showMessage("Profile exported.", 4000)

    def _import_profile(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Import profile", filter="JSON (*.json)")
        if not filename:
            return
        profile = self._profile_store.import_profile(Path(filename))
        self._refresh_profiles(profile.id)
        self.statusBar().showMessage("Profile imported.", 4000)

    def _save_credentials(self, provider_id: str) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        box = self.credentials_tab.provider_boxes[provider_id]
        result = self._credential_vault.save(profile.id, provider_id, box.payload())
        box.update_status(
            CredentialStatus(
                provider_id=provider_id,
                provider_label=self._credential_vault.provider(provider_id).provider_label,
                status=result.status,
                message=result.message,
            )
        )
        if result.status == "invalid":
            QMessageBox.warning(self, "Credential error", result.message)
            return
        box.clear_input()
        self.statusBar().showMessage("Credentials saved locally.", 4000)

    def _validate_credentials(self, provider_id: str) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        status = self._credential_vault.status(profile.id, provider_id)
        self.credentials_tab.provider_boxes[provider_id].update_status(status)
        self.statusBar().showMessage(status.message, 4000)

    def _delete_credentials(self, provider_id: str) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        self._credential_vault.delete(profile.id, provider_id)
        self.credentials_tab.provider_boxes[provider_id].clear_input()
        self.credentials_tab.provider_boxes[provider_id].update_status(
            CredentialStatus(
                provider_id=provider_id,
                provider_label=self._credential_vault.provider(provider_id).provider_label,
                status="missing",
                message="No credentials saved.",
            )
        )
        self.statusBar().showMessage("Credentials deleted from the local keychain.", 4000)

    def _export_diagnostics(self) -> None:
        profile = self._current_profile()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export diagnostics",
            str(self._paths.exports_dir / "diagnostics.json"),
            "JSON (*.json)",
        )
        if not filename:
            return
        status = self._controller.status(profile)
        credential_statuses = self._credential_vault.statuses_for_profile(profile.id) if profile is not None else []
        self._diagnostics.export_bundle(
            profile=profile,
            status=status,
            credential_statuses=credential_statuses,
            output_path=Path(filename),
        )
        self.statusBar().showMessage("Diagnostics bundle exported.", 4000)

    def _sync_startup_manager(self) -> None:
        if not self._startup_manager.supported():
            return
        should_enable = any(profile.auto_start for profile in self._profile_store.list_profiles())
        self._startup_manager.set_enabled(should_enable)

    @staticmethod
    def _open_url(url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    @staticmethod
    def _open_local(path: Path) -> None:
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
