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

from .app_types import ModelProviderConfig, SetupStepState, default_risk_policies
from .copilot import default_model_presets
from .credentials import CredentialProvider, CredentialVault
from .profiles import ProfileStore
from .startup import StartupManager
from .ui.setup import SetupStepper


GOAL_GUIDANCE = {
    "learn_and_scan": (
        "Start with Polymarket, one recorder pass, and one scanner refresh.",
        "Best for a first run. You can leave keys blank and stay fully in practice mode.",
    ),
    "paper_arbitrage": (
        "Run fast scans, review routes clearly, and repeat practice runs.",
        "Best once you already understand the record, scan, and practice loop.",
    ),
    "live_prepare": (
        "Keep everything practice-first while you prepare keys, diagnostics, and approvals.",
        "Best if you want a deliberate path toward live review later.",
    ),
    "lab_experiment": (
        "Turn on research surfaces while keeping execution inside practice-only controls.",
        "Use this only if you want more depth on day one.",
    ),
}
EXPERIENCE_GUIDANCE = {
    "beginner": "Beginner keeps the path short, safe, and clear.",
    "intermediate": "Intermediate keeps guidance on but assumes you know the basics.",
    "advanced": "Advanced keeps the setup lighter and gives you more control sooner.",
}
TEMPLATE_RECOMMENDATIONS = {"learn_and_scan": "Guided", "paper_arbitrage": "Recorder", "live_prepare": "Research", "lab_experiment": "Custom"}
RISK_RECOMMENDATIONS = {"learn_and_scan": "Starter", "paper_arbitrage": "Starter", "live_prepare": "Balanced", "lab_experiment": "Lab"}
PRESET_RECOMMENDATIONS = {"learn_and_scan": "continuous-record", "paper_arbitrage": "continuous-record", "live_prepare": "continuous-record", "lab_experiment": "fast-smoke-run"}
PHASE_LABELS = ["Start", "Goal", "Profile", "Connect", "Review"]


class WelcomePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Set up your first profile")
        self.setSubTitle("Keep the first run local, practice-first, and easy to reverse.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "This setup keeps the first pass simple: Polymarket on, practice mode first, and no exchange keys required."
        )
        intro.setWordWrap(True)
        intro.setObjectName("heroText")
        layout.addWidget(intro)
        boot_map = QGroupBox("What this setup does")
        boot_layout = QVBoxLayout(boot_map)
        for line in (
            "Choose a starter goal and default risk posture.",
            "Turn on Polymarket by default.",
            "Leave keys empty for the first practice-safe run, or store them in the OS keychain.",
        ):
            label = QLabel(f"- {line}")
            label.setWordWrap(True)
            boot_layout.addWidget(label)
        layout.addWidget(boot_map)
        layout.addStretch(1)


class IntentPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Choose your first goal")
        self.setSubTitle("This only sets the starter defaults. You can change it later.")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.goal_combo = QComboBox()
        self.goal_combo.addItem("Learn Polymarket and scan safely", "learn_and_scan")
        self.goal_combo.addItem("Practice route ideas", "paper_arbitrage")
        self.goal_combo.addItem("Prepare for live review", "live_prepare")
        self.goal_combo.addItem("Open lab experiments", "lab_experiment")
        self.experience_combo = QComboBox()
        self.experience_combo.addItem("Beginner", "beginner")
        self.experience_combo.addItem("Intermediate", "intermediate")
        self.experience_combo.addItem("Advanced", "advanced")
        self.guided_mode_checkbox = QCheckBox("Keep guided setup on")
        self.guided_mode_checkbox.setChecked(True)
        self.lab_checkbox = QCheckBox("Show lab tools later")
        form.addRow("Goal", self.goal_combo)
        form.addRow("Experience", self.experience_combo)
        form.addRow("", self.guided_mode_checkbox)
        form.addRow("", self.lab_checkbox)
        layout.addLayout(form)
        group = QGroupBox("Recommended setup")
        group_layout = QVBoxLayout(group)
        self.plan_label = QLabel()
        self.plan_label.setWordWrap(True)
        self.plan_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        group_layout.addWidget(self.plan_label)
        layout.addWidget(group)
        layout.addStretch(1)


class ProfilePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("New or imported profile")
        self.setSubTitle("Create a profile now, or load an older export first.")
        layout = QVBoxLayout(self)
        intro = QLabel("If you already have an export, load it on this step. Otherwise leave the data folder blank and Superior will use the normal per-user location.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.name_edit = QLineEdit("My Superior Profile")
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Guided", "Recorder", "Research", "Custom"])
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setPlaceholderText("Recommended per-user folder")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_data_dir)
        data_dir_row = QHBoxLayout()
        data_dir_row.addWidget(self.data_dir_edit, stretch=1)
        data_dir_row.addWidget(browse_button)
        form.addRow("Profile name", self.name_edit)
        form.addRow("Mode", self.template_combo)
        form.addRow("Data folder", self._wrap_layout(data_dir_row))
        layout.addLayout(form)
        import_row = QHBoxLayout()
        self.import_path_edit = QLineEdit()
        self.import_path_edit.setPlaceholderText("Optional profile JSON export")
        import_button = QPushButton("Load JSON")
        import_button.clicked.connect(self._browse_import_path)
        import_row.addWidget(self.import_path_edit, stretch=1)
        import_row.addWidget(import_button)
        import_label = QLabel("Import an older profile if you already exported one. Secrets stay outside the JSON file.")
        import_label.setWordWrap(True)
        layout.addWidget(import_label)
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
        self.setTitle("Market feed")
        self.setSubTitle("Pick the feeds you want ready on day one.")
        layout = QVBoxLayout(self)
        self.polymarket_checkbox = QCheckBox("Polymarket")
        self.polymarket_checkbox.setChecked(True)
        self.kalshi_checkbox = QCheckBox("Kalshi")
        layout.addWidget(self.polymarket_checkbox)
        for text in (
            "Default signal feed. Public sample data works without keys.",
            "Optional second feed. Add it later for cross-venue checks.",
        ):
            label = QLabel(text)
            label.setWordWrap(True)
            layout.addWidget(label)
        layout.addWidget(self.kalshi_checkbox)
        hint = QLabel("One connector is enough for a clean first run. Live work still requires key setup later.")
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
        self.setTitle("API keys")
        self.setSubTitle("Optional. Skip this for the first practice-first run.")
        self._providers = [provider for provider in providers if provider.provider_id in {"polymarket", "kalshi"}]
        self._field_widgets: dict[str, dict[str, QLineEdit | QPlainTextEdit]] = {}
        self._groups: dict[str, QGroupBox] = {}
        layout = QVBoxLayout(self)
        hint = QLabel("Leave this blank if you only want sample data and practice mode first. Stored keys never go into JSON, DuckDB, or logs.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        for provider in self._providers:
            group = QGroupBox(f"{provider.provider_label} keys")
            group_layout = QFormLayout(group)
            docs_label = QLabel(f'<a href="{provider.docs_url}">Open {provider.provider_label} auth docs</a>')
            docs_label.setOpenExternalLinks(True)
            group_layout.addRow("", docs_label)
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
                provider_payload[key] = widget.toPlainText() if isinstance(widget, QPlainTextEdit) else widget.text()
            payloads[provider_id] = provider_payload
        return payloads


class RiskPage(QWizardPage):
    def __init__(self, preset_labels: list[tuple[str, str]]) -> None:
        super().__init__()
        self.setTitle("Recorder defaults")
        self.setSubTitle("Set the starter recorder and risk defaults for the first run.")
        layout = QVBoxLayout(self)
        intro = QLabel("Pick the starter preset, keep risk sizing conservative, and decide whether the profile starts with Windows.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.default_preset_combo = QComboBox()
        for preset_id, label in preset_labels:
            self.default_preset_combo.addItem(label, preset_id)
        self.market_filters_edit = QLineEdit()
        self.market_filters_edit.setPlaceholderText("elections, sports, crypto")
        self.risk_policy_combo = QComboBox()
        for policy in default_risk_policies():
            self.risk_policy_combo.addItem(f"{policy.label} - {policy.description}", policy.id)
        self.auto_start_checkbox = QCheckBox("Start with Windows")
        self.start_minimized_checkbox = QCheckBox("Start minimized")
        form.addRow("Recorder preset", self.default_preset_combo)
        form.addRow("Market filters", self.market_filters_edit)
        form.addRow("Risk posture", self.risk_policy_combo)
        layout.addLayout(form)
        layout.addWidget(self.auto_start_checkbox)
        layout.addWidget(self.start_minimized_checkbox)
        group = QGroupBox("Recommended start")
        group_layout = QVBoxLayout(group)
        self.recommendation_label = QLabel()
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        group_layout.addWidget(self.recommendation_label)
        layout.addWidget(group)
        layout.addStretch(1)


class CoachPage(QWizardPage):
    def __init__(self, provider: CredentialProvider) -> None:
        super().__init__()
        self.setTitle("Copilot")
        self.setSubTitle("Optional model help. You can skip this and still use the app fully in practice mode.")
        self._provider = provider
        self._presets = [
            ModelProviderConfig(
                provider_id=preset.provider_id,
                provider_label=preset.label,
                model_name=preset.model_name,
                base_url=preset.base_url,
                api_key_required=preset.api_key_required,
                local_only=preset.provider_id in {"none", "ollama"},
            )
            for preset in default_model_presets()
        ]
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Skip this for now if you just want the recorder, scanner, and practice loop. "
            "When you do add a model, the key stays local and Copilot stays read-only."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        group = QGroupBox("Copilot source")
        form = QFormLayout(group)
        self.provider_combo = QComboBox()
        for preset in self._presets:
            self.provider_combo.addItem(preset.provider_label, preset.provider_id)
        self.model_edit = QLineEdit()
        self.base_url_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        docs_label = QLabel(f'<a href="{provider.docs_url}">Open Copilot docs</a>')
        docs_label.setOpenExternalLinks(True)
        form.addRow("", docs_label)
        form.addRow("Provider", self.provider_combo)
        form.addRow("Model", self.model_edit)
        form.addRow("Base URL", self.base_url_edit)
        form.addRow("API key", self.api_key_edit)
        layout.addWidget(group)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        hint = QLabel(
            "OpenAI-compatible, Anthropic, Gemini, and Ollama are supported. "
            "Copilot can explain and draft, but it cannot trade or unlock live."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)
        self.provider_combo.currentIndexChanged.connect(self._apply_selected_preset)
        self._apply_selected_preset()

    def _selected_preset(self) -> ModelProviderConfig:
        provider_id = self.provider_combo.currentData()
        for preset in self._presets:
            if preset.provider_id == provider_id:
                return preset
        return self._presets[0]

    def _apply_selected_preset(self) -> None:
        preset = self._selected_preset()
        self.model_edit.setText(preset.model_name)
        self.base_url_edit.setText(preset.base_url)
        self.api_key_edit.setEnabled(preset.api_key_required)
        if preset.api_key_required:
            self.api_key_edit.setPlaceholderText("Stored in the OS keychain only")
        else:
            self.api_key_edit.clear()
            self.api_key_edit.setPlaceholderText("No API key needed for local models")
        if preset.provider_id == "none":
            self.status_label.setText("Skip for now keeps Superior local-first. You can add a model later.")
        else:
            self.status_label.setText(
                f"{preset.provider_label} stays optional. Save the key only if you want Copilot to rewrite or summarize with that model."
            )

    def is_enabled(self) -> bool:
        return self._selected_preset().provider_id != "none"

    def config(self) -> ModelProviderConfig:
        preset = self._selected_preset()
        return preset.model_copy(
            update={
                "model_name": self.model_edit.text().strip(),
                "base_url": self.base_url_edit.text().strip(),
            }
        )

    def api_key(self) -> str:
        return self.api_key_edit.text().strip()

    def payload(self) -> dict[str, str]:
        config = self.config()
        return {
            "provider_name": config.provider_label,
            "model_name": config.model_name,
            "api_key": self.api_key(),
        }


class FinishPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Finish setup")
        self.setSubTitle("Check the starter defaults before Superior opens.")
        layout = QVBoxLayout(self)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)


class SetupWizard(QWizard):
    def __init__(self, *, profile_store: ProfileStore, credential_vault: CredentialVault, startup_manager: StartupManager, preset_labels: list[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Superior Setup")
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.resize(920, 680)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setButtonText(QWizard.WizardButton.NextButton, "Continue")
        self.setButtonText(QWizard.WizardButton.BackButton, "Back")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Cancel")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish setup")
        self._profile_store = profile_store
        self._credential_vault = credential_vault
        self._startup_manager = startup_manager
        self.created_profile_id: str | None = None
        providers = credential_vault.providers()
        self._provider_labels = {provider.provider_id: provider.provider_label for provider in providers}
        self._preset_labels = {preset_id: label for preset_id, label in preset_labels}
        coach_provider = next(provider for provider in providers if provider.provider_id == "coach")
        self.welcome_page = WelcomePage()
        self.intent_page = IntentPage()
        self.profile_page = ProfilePage()
        self.venue_page = VenuePage()
        self.credentials_page = CredentialsPage(providers)
        self.risk_page = RiskPage(preset_labels)
        self.coach_page = CoachPage(coach_provider)
        self.finish_page = FinishPage()
        self._stepper = SetupStepper(PHASE_LABELS)
        self.setSideWidget(self._stepper)
        self._welcome_id = self.addPage(self.welcome_page)
        self._intent_id = self.addPage(self.intent_page)
        self._profile_id = self.addPage(self.profile_page)
        self._venue_id = self.addPage(self.venue_page)
        self._risk_id = self.addPage(self.risk_page)
        self._finish_id = self.addPage(self.finish_page)
        self.currentIdChanged.connect(self._refresh_dynamic_content)
        for signal in (
            self.intent_page.goal_combo.currentIndexChanged,
            self.intent_page.experience_combo.currentIndexChanged,
            self.intent_page.guided_mode_checkbox.toggled,
            self.intent_page.lab_checkbox.toggled,
            self.profile_page.name_edit.textChanged,
            self.profile_page.template_combo.currentIndexChanged,
            self.profile_page.import_path_edit.textChanged,
            self.venue_page.polymarket_checkbox.toggled,
            self.venue_page.kalshi_checkbox.toggled,
            self.risk_page.default_preset_combo.currentIndexChanged,
            self.risk_page.risk_policy_combo.currentIndexChanged,
            self.risk_page.auto_start_checkbox.toggled,
            self.risk_page.start_minimized_checkbox.toggled,
            self.coach_page.provider_combo.currentIndexChanged,
        ):
            signal.connect(self._refresh_dynamic_content)
        for widgets in self.credentials_page._field_widgets.values():
            for widget in widgets.values():
                (widget.textChanged if isinstance(widget, QPlainTextEdit) else widget.textChanged).connect(self._refresh_dynamic_content)
        self.coach_page.model_edit.textChanged.connect(self._refresh_dynamic_content)
        self.coach_page.base_url_edit.textChanged.connect(self._refresh_dynamic_content)
        self.coach_page.api_key_edit.textChanged.connect(self._refresh_dynamic_content)
        self._refresh_dynamic_content()

    def _refresh_dynamic_content(self) -> None:
        self.credentials_page.set_enabled_providers([venue.lower() for venue in self.venue_page.selected_venues()])
        self.intent_page.plan_label.setText(self._intent_plan_text())
        self.risk_page.recommendation_label.setText(self._risk_guidance_text())
        self.finish_page.summary_label.setText(self._summary_text())
        self._stepper.set_steps(self._step_states())

    def accept(self) -> None:
        import_path = self.profile_page.import_path_edit.text().strip()
        if import_path:
            profile = self._profile_store.import_profile(Path(import_path))
        else:
            selected_venues = self.venue_page.selected_venues()
            if not selected_venues:
                QMessageBox.warning(self, "Choose a connector", "Select at least one connector before finishing setup.")
                return
            data_dir = Path(self.profile_page.data_dir_edit.text().strip()) if self.profile_page.data_dir_edit.text().strip() else None
            profile = self._profile_store.create_profile(
                display_name=self.profile_page.name_edit.text().strip() or "My Superior Profile",
                brand_name="Superior",
                template=self.profile_page.template_combo.currentText(),
                enabled_venues=selected_venues,
                market_filters=self._market_filters(),
                auto_start=self.risk_page.auto_start_checkbox.isChecked(),
                start_minimized=self.risk_page.start_minimized_checkbox.isChecked(),
                default_preset=self.risk_page.default_preset_combo.currentData(),
                data_dir=data_dir,
                experience_level=self.intent_page.experience_combo.currentData(),
                guided_mode=self.intent_page.guided_mode_checkbox.isChecked(),
                lab_enabled=self.intent_page.lab_checkbox.isChecked(),
                ai_coach_enabled=self.coach_page.is_enabled(),
                default_strategy_tier="lab" if self.intent_page.lab_checkbox.isChecked() else "core",
                risk_policy_id=self.risk_page.risk_policy_combo.currentData(),
                primary_goal=self.intent_page.goal_combo.currentData(),
                copilot_provider_id=self.coach_page.config().provider_id,
                copilot_model_name=self.coach_page.config().model_name,
                copilot_base_url=self.coach_page.config().base_url,
            )
            selected_provider_ids = [venue.lower() for venue in selected_venues]
            for provider_id, payload in self.credentials_page.payloads().items():
                if provider_id not in selected_provider_ids or not any(value.strip() for value in payload.values()):
                    continue
                result = self._credential_vault.save(profile.id, provider_id, payload)
                if result.status == "invalid":
                    QMessageBox.warning(self, "Fix keys", f"{provider_id.title()} keys are incomplete: {result.message}")
                    return
            if self.coach_page.api_key().strip():
                result = self._credential_vault.save(profile.id, "coach", self.coach_page.payload())
                if result.status == "invalid":
                    QMessageBox.warning(self, "Fix Copilot", result.message)
                    return
        if profile.auto_start:
            self._startup_manager.set_enabled(True)
        self.created_profile_id = profile.id
        super().accept()

    def _market_filters(self) -> list[str]:
        return [item.strip() for item in self.risk_page.market_filters_edit.text().split(",") if item.strip()]

    def _intent_plan_text(self) -> str:
        goal_id = self.intent_page.goal_combo.currentData()
        experience_id = self.intent_page.experience_combo.currentData()
        goal_summary, goal_detail = GOAL_GUIDANCE.get(goal_id, GOAL_GUIDANCE["learn_and_scan"])
        experience_detail = EXPERIENCE_GUIDANCE.get(experience_id, EXPERIENCE_GUIDANCE["beginner"])
        template = TEMPLATE_RECOMMENDATIONS.get(goal_id, "Guided")
        preset_label = self._preset_labels.get(PRESET_RECOMMENDATIONS.get(goal_id, "continuous-record"), "Continuous recorder")
        risk_label = RISK_RECOMMENDATIONS.get(goal_id, "Starter")
        guided_line = "Guided setup stays on." if self.intent_page.guided_mode_checkbox.isChecked() else "Guided setup is off."
        lab_line = "Lab tools stay visible after setup." if self.intent_page.lab_checkbox.isChecked() else "Lab tools stay hidden until later."
        return (
            f"{goal_summary}\n\n"
            f"{goal_detail}\n"
            f"{experience_detail}\n\n"
            f"Recommended mode: {template}\n"
            f"Recommended recorder preset: {preset_label}\n"
            f"Recommended risk posture: {risk_label}\n"
            f"{guided_line}\n"
            f"{lab_line}"
        )

    def _risk_guidance_text(self) -> str:
        goal_id = self.intent_page.goal_combo.currentData()
        recommended_risk = RISK_RECOMMENDATIONS.get(goal_id, "Starter")
        recommended_preset = self._preset_labels.get(PRESET_RECOMMENDATIONS.get(goal_id, "continuous-record"), "Continuous recorder")
        startup_line = "This profile starts with Windows." if self.risk_page.auto_start_checkbox.isChecked() else "This profile starts manually."
        tray_line = "Start minimized is on." if self.risk_page.start_minimized_checkbox.isChecked() else "Start minimized is off."
        market_filters = ", ".join(self._market_filters()) or "None"
        return (
            f"Recommended for this goal: {recommended_risk} risk with the {recommended_preset} preset.\n\n"
            f"Current preset: {self.risk_page.default_preset_combo.currentText()}\n"
            f"Current risk posture: {self.risk_page.risk_policy_combo.currentText()}\n"
            f"Market filters: {market_filters}\n"
            f"{startup_line}\n"
            f"{tray_line}"
        )

    def _summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return (
                f"Import profile\n"
                f"Source JSON: {self.profile_page.import_path_edit.text().strip()}\n"
                "Secrets stay outside the JSON file.\n"
                "Superior will open Home after import."
            )
        venues = ", ".join(self.venue_page.selected_venues()) or "None"
        default_preset = self.risk_page.default_preset_combo.currentText() or "Continuous recorder"
        selected_provider_ids = [venue.lower() for venue in self.venue_page.selected_venues()]
        credential_labels = [self._provider_labels.get(provider_id, provider_id.title()) for provider_id, payload in self.credentials_page.payloads().items() if provider_id in selected_provider_ids and any(value.strip() for value in payload.values())]
        data_dir = self.profile_page.data_dir_edit.text().strip() or "Recommended per-user folder"
        copilot_config = self.coach_page.config()
        copilot_line = (
            f"Copilot: {copilot_config.provider_label} / {copilot_config.model_name or 'Default model'}"
            if self.coach_page.is_enabled()
            else "Copilot: Skip for now"
        )
        copilot_key_line = "Copilot key entered now" if self.coach_page.api_key().strip() else "Copilot key saved later"
        return (
            f"New profile\n"
            f"Profile: {self.profile_page.name_edit.text().strip() or 'My Superior Profile'}\n"
            f"Mode: {self.profile_page.template_combo.currentText()}\n"
            f"Goal: {self.intent_page.goal_combo.currentText()}\n"
            f"Experience: {self.intent_page.experience_combo.currentText()}\n"
            f"Connectors: {venues}\n"
            f"Data folder: {data_dir}\n"
            f"Recorder preset: {default_preset}\n"
            f"Risk posture: {self.risk_page.risk_policy_combo.currentText()}\n"
            f"Guided setup: {'On' if self.intent_page.guided_mode_checkbox.isChecked() else 'Off'}\n"
            f"Lab: {'On' if self.intent_page.lab_checkbox.isChecked() else 'Off'}\n"
            f"Keys entered now: {', '.join(credential_labels) if credential_labels else 'None'}\n"
            f"{copilot_line}\n"
            f"{copilot_key_line}\n\n"
            "Next:\n"
            "- Open Home and run the recorder.\n"
            "- Refresh Scan after the first sample lands.\n"
            "- Start one practice run."
        )

    def _step_states(self) -> list[SetupStepState]:
        current_step = self._current_step_index()
        return [SetupStepState(id=f"step-{index}", label=label, index=index, active=index == current_step, complete=index < current_step) for index, label in enumerate(PHASE_LABELS)]

    def _current_step_index(self) -> int:
        current_page_id = self.currentId()
        if current_page_id == self._welcome_id:
            return 0
        if current_page_id == self._intent_id:
            return 1
        if current_page_id in {self._profile_id, self._risk_id}:
            return 2
        if current_page_id == self._venue_id:
            return 3
        return 4
