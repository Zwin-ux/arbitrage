from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from .app_types import AppProfile
from .credentials import CredentialProvider, CredentialVault
from .profiles import ProfileStore
from .startup import StartupManager


class WelcomePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Welcome")
        self.setSubTitle("This app is open source, local-first, and built for bring-your-own profiles.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "You can record public market data without any credentials. "
            "If you want to save venue keys for future trading work, they stay in your OS keychain."
        )
        intro.setWordWrap(True)
        intro.setObjectName("heroText")
        layout.addWidget(intro)

        card = QGroupBox("What this setup does")
        card_layout = QVBoxLayout(card)
        for line in (
            "Create or import a profile",
            "Choose venues and optional credentials",
            "Pick a storage location and default preset",
            "Land on a dashboard with Start, Stop, Replay, and Verify",
        ):
            label = QLabel(f"- {line}")
            label.setWordWrap(True)
            card_layout.addWidget(label)
        layout.addWidget(card)
        layout.addStretch(1)


class ProfilePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Profile")
        self.setSubTitle("Create a new profile or import one of your own JSON exports.")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit("My Recorder Profile")
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Recorder", "Research", "Custom"])
        self.data_dir_edit = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_data_dir)
        data_dir_row = QHBoxLayout()
        data_dir_row.addWidget(self.data_dir_edit, stretch=1)
        data_dir_row.addWidget(browse_button)
        form.addRow("Display name", self.name_edit)
        form.addRow("Template", self.template_combo)
        form.addRow("Data directory", self._wrap_layout(data_dir_row))
        layout.addLayout(form)

        import_row = QHBoxLayout()
        self.import_path_edit = QLineEdit()
        self.import_path_edit.setPlaceholderText("Optional profile JSON export")
        import_button = QPushButton("Import JSON")
        import_button.clicked.connect(self._browse_import_path)
        import_row.addWidget(self.import_path_edit, stretch=1)
        import_row.addWidget(import_button)
        layout.addWidget(QLabel("Import instead of creating a new profile"))
        layout.addLayout(import_row)
        layout.addStretch(1)

    def _browse_data_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Choose profile data folder")
        if directory:
            self.data_dir_edit.setText(directory)

    def _browse_import_path(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Import profile", filter="JSON (*.json)")
        if filename:
            self.import_path_edit.setText(filename)

    @staticmethod
    def _wrap_layout(layout: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget


class VenuePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Venues")
        self.setSubTitle("Pick the venues you want this profile to know about.")
        layout = QVBoxLayout(self)
        self.polymarket_checkbox = QCheckBox("Polymarket")
        self.polymarket_checkbox.setChecked(True)
        self.kalshi_checkbox = QCheckBox("Kalshi")
        layout.addWidget(self.polymarket_checkbox)
        layout.addWidget(self.kalshi_checkbox)
        hint = QLabel("You can always add or remove venues later in the app.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

    def selected_venues(self) -> list[str]:
        venues: list[str] = []
        if self.polymarket_checkbox.isChecked():
            venues.append("Polymarket")
        if self.kalshi_checkbox.isChecked():
            venues.append("Kalshi")
        return venues


class CredentialsPage(QWizardPage):
    def __init__(self, providers: list[CredentialProvider]) -> None:
        super().__init__()
        self.setTitle("Credentials")
        self.setSubTitle("Add credentials now or skip and use public recorder features first.")
        self._providers = providers
        self._field_widgets: dict[str, dict[str, QLineEdit | QPlainTextEdit]] = {}
        self._groups: dict[str, QGroupBox] = {}

        layout = QVBoxLayout(self)
        hint = QLabel(
            "This step is optional. Stored secrets go into your OS keychain and never into JSON, DuckDB, or logs."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        for provider in self._providers:
            group = QGroupBox(provider.provider_label)
            group_layout = QFormLayout(group)
            widgets: dict[str, QLineEdit | QPlainTextEdit] = {}
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
                group_layout.addRow(field.label, widget)
                widgets[field.key] = widget
            self._field_widgets[provider.provider_id] = widgets
            self._groups[provider.provider_id] = group
            layout.addWidget(group)
        layout.addStretch(1)

    def set_enabled_providers(self, provider_ids: list[str]) -> None:
        for provider_id, group in self._groups.items():
            group.setVisible(provider_id in provider_ids)

    def payloads(self) -> dict[str, dict[str, str]]:
        payloads: dict[str, dict[str, str]] = {}
        for provider_id, widgets in self._field_widgets.items():
            provider_payload: dict[str, str] = {}
            for key, widget in widgets.items():
                if isinstance(widget, QPlainTextEdit):
                    provider_payload[key] = widget.toPlainText()
                else:
                    provider_payload[key] = widget.text()
            payloads[provider_id] = provider_payload
        return payloads


class RecorderPage(QWizardPage):
    def __init__(self, preset_labels: list[tuple[str, str]]) -> None:
        super().__init__()
        self.setTitle("Recorder defaults")
        self.setSubTitle("Choose where this profile should start when the app launches.")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.default_preset_combo = QComboBox()
        for preset_id, label in preset_labels:
            self.default_preset_combo.addItem(label, preset_id)
        self.market_filters_edit = QLineEdit()
        self.market_filters_edit.setPlaceholderText("elections, sports, crypto")
        self.auto_start_checkbox = QCheckBox("Run app at login with this profile")
        self.start_minimized_checkbox = QCheckBox("Start minimized to tray")
        form.addRow("Default preset", self.default_preset_combo)
        form.addRow("Market filters", self.market_filters_edit)
        layout.addLayout(form)
        layout.addWidget(self.auto_start_checkbox)
        layout.addWidget(self.start_minimized_checkbox)
        layout.addStretch(1)


class FinishPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Finish")
        self.setSubTitle("Review the final setup summary before creating the profile.")
        layout = QVBoxLayout(self)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)


class SetupWizard(QWizard):
    def __init__(
        self,
        *,
        profile_store: ProfileStore,
        credential_vault: CredentialVault,
        startup_manager: StartupManager,
        preset_labels: list[tuple[str, str]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Superior setup")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.resize(860, 620)

        self._profile_store = profile_store
        self._credential_vault = credential_vault
        self._startup_manager = startup_manager
        self.created_profile_id: str | None = None

        providers = credential_vault.providers()
        self.welcome_page = WelcomePage()
        self.profile_page = ProfilePage()
        self.venue_page = VenuePage()
        self.credentials_page = CredentialsPage(providers)
        self.recorder_page = RecorderPage(preset_labels)
        self.finish_page = FinishPage()

        self.addPage(self.welcome_page)
        self.addPage(self.profile_page)
        self.addPage(self.venue_page)
        self.addPage(self.credentials_page)
        self.addPage(self.recorder_page)
        self.addPage(self.finish_page)

        self.currentIdChanged.connect(self._refresh_dynamic_content)

    def _refresh_dynamic_content(self) -> None:
        self.credentials_page.set_enabled_providers(
            [venue.lower() for venue in self.venue_page.selected_venues()]
        )
        self.finish_page.summary_label.setText(self._summary_text())

    def accept(self) -> None:
        import_path = self.profile_page.import_path_edit.text().strip()
        if import_path:
            profile = self._profile_store.import_profile(Path(import_path))
        else:
            selected_venues = self.venue_page.selected_venues()
            if not selected_venues:
                QMessageBox.warning(self, "Choose a venue", "Select at least one venue for this profile.")
                return
            data_dir_text = self.profile_page.data_dir_edit.text().strip()
            data_dir = Path(data_dir_text) if data_dir_text else None
            profile = self._profile_store.create_profile(
                display_name=self.profile_page.name_edit.text().strip() or "My Recorder Profile",
                template=self.profile_page.template_combo.currentText(),
                enabled_venues=selected_venues,
                market_filters=self._market_filters(),
                auto_start=self.recorder_page.auto_start_checkbox.isChecked(),
                start_minimized=self.recorder_page.start_minimized_checkbox.isChecked(),
                default_preset=self.recorder_page.default_preset_combo.currentData(),
                data_dir=data_dir,
            )
            for provider_id, payload in self.credentials_page.payloads().items():
                if provider_id not in [venue.lower() for venue in selected_venues]:
                    continue
                result = self._credential_vault.save(profile.id, provider_id, payload)
                if result.status == "invalid":
                    QMessageBox.warning(
                        self,
                        "Fix credentials",
                        f"{provider_id.title()} credentials are incomplete: {result.message}",
                    )
                    return
        if profile.auto_start:
            self._startup_manager.set_enabled(True)
        self.created_profile_id = profile.id
        super().accept()

    def _market_filters(self) -> list[str]:
        raw_filters = self.recorder_page.market_filters_edit.text()
        return [item.strip() for item in raw_filters.split(",") if item.strip()]

    def _summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return (
                "The wizard will import the selected profile JSON, keep secrets in the OS keychain, "
                "and open the dashboard when it finishes."
            )
        venues = ", ".join(self.venue_page.selected_venues()) or "No venues selected yet"
        default_preset = self.recorder_page.default_preset_combo.currentText() or "Continuous recorder"
        return (
            f"Profile: {self.profile_page.name_edit.text().strip() or 'My Recorder Profile'}\n"
            f"Template: {self.profile_page.template_combo.currentText()}\n"
            f"Venues: {venues}\n"
            f"Default preset: {default_preset}\n"
            f"Auto-start: {'Yes' if self.recorder_page.auto_start_checkbox.isChecked() else 'No'}\n"
            f"Start minimized: {'Yes' if self.recorder_page.start_minimized_checkbox.isChecked() else 'No'}"
        )
