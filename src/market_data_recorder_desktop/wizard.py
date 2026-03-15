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

from .app_types import SetupCompletionRoute, SetupStepState, default_risk_policies
from .credentials import CredentialProvider, CredentialVault
from .profiles import ProfileStore
from .startup import StartupManager
from .ui.setup import SetupCompletionState, SetupStepper


GOAL_GUIDANCE = {
    "learn_and_scan": (
        "Start with public Polymarket recording, learn the scanner, and keep live mode out of view until you need it.",
        "Best for first-time users. You can leave credentials blank and still build local market data.",
    ),
    "paper_arbitrage": (
        "Optimize the profile for scanner refreshes, explainable candidates, and paper execution history.",
        "Recommended once you already understand the core recorder flow and want to test ideas repeatedly.",
    ),
    "live_prepare": (
        "Keep the product in a paper-first posture while you work through credentials, diagnostics, and acknowledgements.",
        "Good if you want a disciplined path toward live readiness without unlocking anything early.",
    ),
    "lab_experiment": (
        "Expose the Lab and keep experiments contained behind paper-only controls.",
        "Use this only if you explicitly want higher-risk research surfaces on day one.",
    ),
}

EXPERIENCE_GUIDANCE = {
    "beginner": "Beginner mode keeps the setup conservative and assumes you want the shortest path to a safe first recording.",
    "intermediate": "Intermediate mode still favors guidance, but expects that recorder, scanner, and paper concepts are familiar.",
    "advanced": "Advanced mode assumes you want faster access to recorder controls and more freedom to customize the profile.",
}

TEMPLATE_RECOMMENDATIONS = {
    "learn_and_scan": "Guided",
    "paper_arbitrage": "Recorder",
    "live_prepare": "Research",
    "lab_experiment": "Custom",
}

RISK_RECOMMENDATIONS = {
    "learn_and_scan": "Starter",
    "paper_arbitrage": "Starter",
    "live_prepare": "Balanced",
    "lab_experiment": "Lab",
}

PRESET_RECOMMENDATIONS = {
    "learn_and_scan": "continuous-record",
    "paper_arbitrage": "continuous-record",
    "live_prepare": "continuous-record",
    "lab_experiment": "fast-smoke-run",
}


class WelcomePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Welcome to Superior")
        self.setSubTitle("A paper-first desktop product with a guided setup path for everyday users.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Superior walks you through a local-first profile, safe defaults, optional credentials, "
            "and a first-run plan. Most users can finish this setup in a few minutes and reach the first paper run without entering keys."
        )
        intro.setWordWrap(True)
        intro.setObjectName("heroText")
        layout.addWidget(intro)

        flow_card = QGroupBox("What setup covers")
        flow_layout = QVBoxLayout(flow_card)
        for line in (
            "Choose a goal, experience level, and starter profile template",
            "Keep Polymarket on by default and add Kalshi only when you need it",
            "Skip credentials for recorder and paper mode, or add them now and keep them in the OS keychain",
        ):
            label = QLabel(f"- {line}")
            label.setWordWrap(True)
            flow_layout.addWidget(label)
        layout.addWidget(flow_card)

        card = QGroupBox("Default product posture")
        card_layout = QVBoxLayout(card)
        for line in (
            "Guided beginner flow by default",
            "Paper-first strategies and deterministic execution",
            "Live mode hidden until the checklist passes",
            "Arcade-style loadout that equips connectors and modules deliberately",
        ):
            label = QLabel(f"- {line}")
            label.setWordWrap(True)
            card_layout.addWidget(label)
        layout.addWidget(card)
        layout.addStretch(1)


class IntentPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("What do you want to do?")
        self.setSubTitle("Pick the first-launch posture. You can change it later without reinstalling.")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.goal_combo = QComboBox()
        self.goal_combo.addItem("Learn Polymarket and scan safely", "learn_and_scan")
        self.goal_combo.addItem("Paper-trade arbitrage ideas", "paper_arbitrage")
        self.goal_combo.addItem("Prepare for future live trading", "live_prepare")
        self.goal_combo.addItem("Experiment in the Lab", "lab_experiment")

        self.experience_combo = QComboBox()
        self.experience_combo.addItem("Beginner", "beginner")
        self.experience_combo.addItem("Intermediate", "intermediate")
        self.experience_combo.addItem("Advanced", "advanced")

        self.guided_mode_checkbox = QCheckBox("Keep Guided mode on")
        self.guided_mode_checkbox.setChecked(True)
        self.lab_checkbox = QCheckBox("Expose the Lab after setup")

        form.addRow("Primary goal", self.goal_combo)
        form.addRow("Experience level", self.experience_combo)
        form.addRow("", self.guided_mode_checkbox)
        form.addRow("", self.lab_checkbox)
        layout.addLayout(form)

        recommendation_group = QGroupBox("Recommended first-launch plan")
        recommendation_layout = QVBoxLayout(recommendation_group)
        self.plan_label = QLabel()
        self.plan_label.setWordWrap(True)
        self.plan_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        recommendation_layout.addWidget(self.plan_label)
        layout.addWidget(recommendation_group)
        layout.addStretch(1)


class ProfilePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Profile")
        self.setSubTitle("Create a profile with the recommended storage path, or import an older JSON export.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Leave the data directory blank unless you need a custom location. Superior will use a per-user app folder automatically."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.name_edit = QLineEdit("My Superior Profile")
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Guided", "Recorder", "Research", "Custom"])
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setPlaceholderText("Recommended per-user app storage")
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
        import_label = QLabel(
            "Import instead of creating a new profile if you already have an exported setup. Secrets still stay outside the JSON file."
        )
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
        self.setTitle("Equip connectors")
        self.setSubTitle("Start simple. Equipping Polymarket is enough for recorder, scanner, and paper score.")
        layout = QVBoxLayout(self)
        self.polymarket_checkbox = QCheckBox("Polymarket")
        self.polymarket_checkbox.setChecked(True)
        self.kalshi_checkbox = QCheckBox("Kalshi")
        layout.addWidget(self.polymarket_checkbox)
        polymarket_hint = QLabel(
            "Recommended first launch. You can record public Polymarket data without adding any credentials."
        )
        polymarket_hint.setWordWrap(True)
        layout.addWidget(polymarket_hint)
        layout.addWidget(self.kalshi_checkbox)
        kalshi_hint = QLabel(
            "Optional for cross-venue research. Add it later if you want exact-match comparisons or bring your own API key."
        )
        kalshi_hint.setWordWrap(True)
        layout.addWidget(kalshi_hint)
        hint = QLabel(
            "You can keep this page minimal: one connector is enough to finish setup cleanly. The live gate still requires key setup."
        )
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
        self.setTitle("Connector credentials")
        self.setSubTitle("Optional for recorder and paper mode. Skip this if you only want the safe starter path.")
        self._providers = [provider for provider in providers if provider.provider_id in {"polymarket", "kalshi"}]
        self._field_widgets: dict[str, dict[str, QLineEdit | QPlainTextEdit]] = {}
        self._groups: dict[str, QGroupBox] = {}

        layout = QVBoxLayout(self)
        hint = QLabel(
            "Leave this blank if you only want scanner and paper flows first. Stored secrets never go into JSON, DuckDB, or logs."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        for provider in self._providers:
            group = QGroupBox(f"{provider.provider_label} credentials")
            group_layout = QFormLayout(group)
            docs_label = QLabel(
                f'<a href="{provider.docs_url}">Open {provider.provider_label} authentication docs</a>'
            )
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
                if isinstance(widget, QPlainTextEdit):
                    provider_payload[key] = widget.toPlainText()
                else:
                    provider_payload[key] = widget.text()
            payloads[provider_id] = provider_payload
        return payloads


class RiskPage(QWizardPage):
    def __init__(self, preset_labels: list[tuple[str, str]]) -> None:
        super().__init__()
        self.setTitle("Risk and bot defaults")
        self.setSubTitle("Choose conservative day-one defaults. You can raise complexity later, not now.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "These settings decide how the product behaves on first launch: which preset starts, how cautious paper sizing stays, and whether the app should appear at login."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.default_preset_combo = QComboBox()
        for preset_id, label in preset_labels:
            self.default_preset_combo.addItem(label, preset_id)
        self.default_preset_combo.setCurrentIndex(0)
        self.market_filters_edit = QLineEdit()
        self.market_filters_edit.setPlaceholderText("elections, sports, crypto")
        self.risk_policy_combo = QComboBox()
        for policy in default_risk_policies():
            self.risk_policy_combo.addItem(f"{policy.label} - {policy.description}", policy.id)
        self.auto_start_checkbox = QCheckBox("Run app at login with this profile")
        self.start_minimized_checkbox = QCheckBox("Start minimized to tray")
        form.addRow("Default preset", self.default_preset_combo)
        form.addRow("Market filters", self.market_filters_edit)
        form.addRow("Risk policy", self.risk_policy_combo)
        layout.addLayout(form)
        layout.addWidget(self.auto_start_checkbox)
        layout.addWidget(self.start_minimized_checkbox)
        recommendation_group = QGroupBox("Day-one guidance")
        recommendation_layout = QVBoxLayout(recommendation_group)
        self.recommendation_label = QLabel()
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        recommendation_layout.addWidget(self.recommendation_label)
        layout.addWidget(recommendation_group)
        layout.addStretch(1)


class CoachPage(QWizardPage):
    def __init__(self, provider: CredentialProvider) -> None:
        super().__init__()
        self.setTitle("Optional AI coach")
        self.setSubTitle("The coach explains opportunities and logs. It never places or tunes live trades.")
        self._provider = provider
        self._field_widgets: dict[str, QLineEdit | QPlainTextEdit] = {}

        layout = QVBoxLayout(self)
        intro = QLabel(
            "The coach link is optional. Leave it off if you want the cleanest setup; you can still use local docs and profile state later."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.enable_checkbox = QCheckBox("Enable AI coach for this profile")
        layout.addWidget(self.enable_checkbox)

        group = QGroupBox(provider.provider_label)
        form = QFormLayout(group)
        docs_label = QLabel(f'<a href="{provider.docs_url}">Open coach docs</a>')
        docs_label.setOpenExternalLinks(True)
        form.addRow("", docs_label)
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
            form.addRow(field.label, widget)
            self._field_widgets[field.key] = widget
        layout.addWidget(group)

        hint = QLabel(
            "BYO model keys are optional in v1. Superior can still answer coaching prompts from local docs and profile state."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

    def payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        for key, widget in self._field_widgets.items():
            if isinstance(widget, QPlainTextEdit):
                payload[key] = widget.toPlainText()
            else:
                payload[key] = widget.text()
        return payload


class FinishPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Review")
        self.setSubTitle("Confirm the setup summary before Superior opens Hangar.")
        layout = QVBoxLayout(self)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)


class CompletionPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Completion handoff")
        self.setSubTitle("Finish setup and launch into Hangar with the recorder-first mission highlighted.")
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Superior will open your Hangar mission control with the first paper-safe action framed clearly."
        )
        intro.setWordWrap(True)
        intro.setObjectName("heroText")
        layout.addWidget(intro)
        self.completion_state = SetupCompletionState()
        layout.addWidget(self.completion_state)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setProperty("muted", True)
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
        self.resize(920, 680)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setButtonText(QWizard.WizardButton.NextButton, "Next")
        self.setButtonText(QWizard.WizardButton.BackButton, "Back")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Cancel")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Launch Hangar")

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
        self.completion_page = CompletionPage()

        self._stepper = SetupStepper(
            [
                "Welcome",
                "Goal selection",
                "Starter posture",
                "Connector defaults",
                "Review",
                "Completion",
            ]
        )
        self.setSideWidget(self._stepper)

        self._welcome_id = self.addPage(self.welcome_page)
        self._intent_id = self.addPage(self.intent_page)
        self._profile_id = self.addPage(self.profile_page)
        self._venue_id = self.addPage(self.venue_page)
        self._credentials_id = self.addPage(self.credentials_page)
        self._risk_id = self.addPage(self.risk_page)
        self._coach_id = self.addPage(self.coach_page)
        self._finish_id = self.addPage(self.finish_page)
        self._completion_id = self.addPage(self.completion_page)

        self.currentIdChanged.connect(self._refresh_dynamic_content)
        self.intent_page.goal_combo.currentIndexChanged.connect(self._refresh_dynamic_content)
        self.intent_page.experience_combo.currentIndexChanged.connect(self._refresh_dynamic_content)
        self.intent_page.guided_mode_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.intent_page.lab_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.profile_page.name_edit.textChanged.connect(self._refresh_dynamic_content)
        self.profile_page.template_combo.currentIndexChanged.connect(self._refresh_dynamic_content)
        self.profile_page.import_path_edit.textChanged.connect(self._refresh_dynamic_content)
        self.venue_page.polymarket_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.venue_page.kalshi_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.risk_page.default_preset_combo.currentIndexChanged.connect(self._refresh_dynamic_content)
        self.risk_page.risk_policy_combo.currentIndexChanged.connect(self._refresh_dynamic_content)
        self.risk_page.auto_start_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.risk_page.start_minimized_checkbox.toggled.connect(self._refresh_dynamic_content)
        self.coach_page.enable_checkbox.toggled.connect(self._refresh_dynamic_content)
        for widgets in self.credentials_page._field_widgets.values():
            for widget in widgets.values():
                if isinstance(widget, QPlainTextEdit):
                    widget.textChanged.connect(self._refresh_dynamic_content)
                else:
                    widget.textChanged.connect(self._refresh_dynamic_content)
        for widget in self.coach_page._field_widgets.values():
            if isinstance(widget, QPlainTextEdit):
                widget.textChanged.connect(self._refresh_dynamic_content)
            else:
                widget.textChanged.connect(self._refresh_dynamic_content)
        self._refresh_dynamic_content()

    def _refresh_dynamic_content(self) -> None:
        self.credentials_page.set_enabled_providers(
            [venue.lower() for venue in self.venue_page.selected_venues()]
        )
        self.intent_page.plan_label.setText(self._intent_plan_text())
        self.risk_page.recommendation_label.setText(self._risk_guidance_text())
        self.finish_page.summary_label.setText(self._summary_text())
        self.completion_page.summary_label.setText(self._completion_summary_text())
        self.completion_page.completion_state.set_route(self._completion_route())
        self._stepper.set_steps(self._step_states())

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
                ai_coach_enabled=self.coach_page.enable_checkbox.isChecked(),
                default_strategy_tier="lab" if self.intent_page.lab_checkbox.isChecked() else "core",
                risk_policy_id=self.risk_page.risk_policy_combo.currentData(),
                primary_goal=self.intent_page.goal_combo.currentData(),
            )
            for provider_id, payload in self.credentials_page.payloads().items():
                if provider_id not in [venue.lower() for venue in selected_venues]:
                    continue
                if not any(value.strip() for value in payload.values()):
                    continue
                result = self._credential_vault.save(profile.id, provider_id, payload)
                if result.status == "invalid":
                    QMessageBox.warning(
                        self,
                        "Fix credentials",
                        f"{provider_id.title()} credentials are incomplete: {result.message}",
                    )
                    return
            if self.coach_page.enable_checkbox.isChecked():
                result = self._credential_vault.save(profile.id, "coach", self.coach_page.payload())
                if result.status == "invalid":
                    QMessageBox.warning(
                        self,
                        "Fix AI coach credentials",
                        result.message,
                    )
                    return
        if profile.auto_start:
            self._startup_manager.set_enabled(True)
        self.created_profile_id = profile.id
        super().accept()

    def _market_filters(self) -> list[str]:
        raw_filters = self.risk_page.market_filters_edit.text()
        return [item.strip() for item in raw_filters.split(",") if item.strip()]

    def _intent_plan_text(self) -> str:
        goal_id = self.intent_page.goal_combo.currentData()
        experience_id = self.intent_page.experience_combo.currentData()
        goal_summary, goal_detail = GOAL_GUIDANCE.get(
            goal_id,
            GOAL_GUIDANCE["learn_and_scan"],
        )
        experience_detail = EXPERIENCE_GUIDANCE.get(
            experience_id,
            EXPERIENCE_GUIDANCE["beginner"],
        )
        template = TEMPLATE_RECOMMENDATIONS.get(goal_id, "Guided")
        preset_label = self._preset_labels.get(
            PRESET_RECOMMENDATIONS.get(goal_id, "continuous-record"),
            "Continuous recorder",
        )
        risk_label = RISK_RECOMMENDATIONS.get(goal_id, "Starter")
        lab_line = (
            "Lab stays visible after setup."
            if self.intent_page.lab_checkbox.isChecked()
            else "Lab stays hidden until you explicitly enable it."
        )
        guided_line = (
            "Guided mode stays on, which is the recommended consumer setup path."
            if self.intent_page.guided_mode_checkbox.isChecked()
            else "Guided mode is off, so Home will expose a less opinionated starting state."
        )
        return (
            f"{goal_summary}\n\n"
            f"{goal_detail}\n"
            f"{experience_detail}\n\n"
            f"Recommended template: {template}\n"
            f"Recommended first preset: {preset_label}\n"
            f"Recommended risk policy: {risk_label}\n"
            f"{guided_line}\n"
            f"{lab_line}"
        )

    def _risk_guidance_text(self) -> str:
        goal_id = self.intent_page.goal_combo.currentData()
        recommended_risk = RISK_RECOMMENDATIONS.get(goal_id, "Starter")
        recommended_preset = self._preset_labels.get(
            PRESET_RECOMMENDATIONS.get(goal_id, "continuous-record"),
            "Continuous recorder",
        )
        startup_line = (
            "The app will auto-launch with this profile."
            if self.risk_page.auto_start_checkbox.isChecked()
            else "The app will only open when you launch it manually."
        )
        tray_line = (
            "Start minimized is on, so the recorder can stay out of the way after login."
            if self.risk_page.start_minimized_checkbox.isChecked()
            else "Start minimized is off, which is easier while you are still learning the workflow."
        )
        market_filters = ", ".join(self._market_filters()) or "none yet"
        return (
            f"Recommended for this goal: {recommended_risk} risk policy and the {recommended_preset} preset.\n\n"
            f"Current preset: {self.risk_page.default_preset_combo.currentText()}\n"
            f"Current risk policy: {self.risk_page.risk_policy_combo.currentText()}\n"
            f"Market filters: {market_filters}\n"
            f"{startup_line}\n"
            f"{tray_line}"
        )

    def _summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return (
                "Import mode\n"
                f"Source JSON: {self.profile_page.import_path_edit.text().strip()}\n"
                "Secrets remain outside the JSON file and stay in the OS keychain.\n"
                "Superior will open Hangar after the import finishes."
            )
        venues = ", ".join(self.venue_page.selected_venues()) or "No venues selected yet"
        default_preset = self.risk_page.default_preset_combo.currentText() or "Continuous recorder"
        credential_labels = []
        for provider_id, payload in self.credentials_page.payloads().items():
            if provider_id not in [venue.lower() for venue in self.venue_page.selected_venues()]:
                continue
            if any(value.strip() for value in payload.values()):
                credential_labels.append(self._provider_labels.get(provider_id, provider_id.title()))
        data_dir = self.profile_page.data_dir_edit.text().strip() or "Recommended per-user app storage"
        return (
            "New profile summary\n"
            f"Profile: {self.profile_page.name_edit.text().strip() or 'My Superior Profile'}\n"
            f"Template: {self.profile_page.template_combo.currentText()}\n"
            f"Goal: {self.intent_page.goal_combo.currentText()}\n"
            f"Experience: {self.intent_page.experience_combo.currentText()}\n"
            f"Equipped connectors: {venues}\n"
            f"Data directory: {data_dir}\n"
            f"Default preset: {default_preset}\n"
            f"Risk policy: {self.risk_page.risk_policy_combo.currentText()}\n"
            f"Guided mode: {'On' if self.intent_page.guided_mode_checkbox.isChecked() else 'Off'}\n"
            f"Lab enabled: {'Yes' if self.intent_page.lab_checkbox.isChecked() else 'No'}\n"
            f"Connector credentials entered now: {', '.join(credential_labels) if credential_labels else 'None'}\n"
            f"Coach link: {'Equipped' if self.coach_page.enable_checkbox.isChecked() else 'Not equipped'}\n"
            "First launch plan:\n"
            "- Open Hangar and boot the recorder to build local market data.\n"
            "- Scan edge after the first recording sample completes.\n"
            "- Run one paper route and use Score as the main progression surface.\n"
            "- Keep live-gate work optional until you intentionally want it."
        )

    def _completion_summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return (
                "Imported profiles still land in Hangar with the same safe default: boot recorder first, "
                "then inspect one scanner route before worrying about anything live."
            )
        selected_venues = ", ".join(self.venue_page.selected_venues()) or "Polymarket"
        risk_policy = self.risk_page.risk_policy_combo.currentText()
        return (
            f"Loadout ready: {selected_venues}. "
            f"Risk posture: {risk_policy}. "
            "The Hangar opens with the recorder-first checklist visible so the first paper-safe loop is obvious."
        )

    def _completion_route(self) -> SetupCompletionRoute:
        if self.profile_page.import_path_edit.text().strip():
            return SetupCompletionRoute(
                title="Imported profile routes to Hangar",
                detail=(
                    "Superior will open Hangar, preserve the imported loadout, and keep Boot recorder framed "
                    "as the next useful action."
                ),
            )
        if self.venue_page.kalshi_checkbox.isChecked():
            return SetupCompletionRoute(
                title="Hangar opens with recorder-first guidance",
                detail=(
                    "Polymarket stays the first pass. Kalshi remains equipped, but Hangar still highlights Boot "
                    "recorder before any cross-venue work."
                ),
            )
        return SetupCompletionRoute(
            title="Hangar highlights Boot recorder",
            detail=(
                "Superior will open Hangar mission control, show the first-pass checklist, and keep Boot recorder "
                "visibly dominant until the first local sample lands."
            ),
        )

    def _step_states(self) -> list[SetupStepState]:
        current_step = self._current_step_index()
        labels = [
            "Welcome",
            "Goal selection",
            "Starter posture",
            "Connector defaults",
            "Review",
            "Completion",
        ]
        states: list[SetupStepState] = []
        for index, label in enumerate(labels):
            states.append(
                SetupStepState(
                    id=f"step-{index}",
                    label=label,
                    index=index,
                    active=index == current_step,
                    complete=index < current_step,
                )
            )
        return states

    def _current_step_index(self) -> int:
        current_page_id = self.currentId()
        if current_page_id == self._welcome_id:
            return 0
        if current_page_id == self._intent_id:
            return 1
        if current_page_id in {self._profile_id, self._risk_id}:
            return 2
        if current_page_id in {self._venue_id, self._credentials_id, self._coach_id}:
            return 3
        if current_page_id == self._finish_id:
            return 4
        return 5
