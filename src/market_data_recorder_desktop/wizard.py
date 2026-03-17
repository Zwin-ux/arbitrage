from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget, QWizard, QWizardPage

from .app_types import SetupCompletionRoute, SetupStepState, default_risk_policies
from .credentials import CredentialProvider, CredentialVault
from .profiles import ProfileStore
from .startup import StartupManager
from .ui.setup import SetupCompletionState, SetupStepper


GOAL_GUIDANCE = {
    "learn_and_scan": ("ARM POLYMARKET. LEARN THE RADAR. KEEP THE GATE DARK.", "BEST FOR FIRST-TIME OPERATORS. LEAVE KEY SLOTS BLANK."),
    "paper_arbitrage": ("RUN FAST SCANS, EXPLAINABLE ROUTES, AND REPEAT PAPER RUNS.", "BEST ONCE YOU ALREADY KNOW THE SAMPLE -> SCAN -> RUN LOOP."),
    "live_prepare": ("KEEP THE MACHINE PAPER-FIRST WHILE YOU CLEAR KEYS, DIAG, AND ACKS.", "BEST IF YOU WANT A DISCIPLINED PATH TOWARD THE GATE."),
    "lab_experiment": ("EXPOSE LAB SURFACES WHILE KEEPING RISK INSIDE PAPER-ONLY CONTROLS.", "USE THIS ONLY IF YOU WANT RESEARCH SURFACES ON DAY ONE."),
}
EXPERIENCE_GUIDANCE = {
    "beginner": "BEGINNER POSTURE KEEPS THE BOOT PATH SHORT, SAFE, AND HIGH SIGNAL.",
    "intermediate": "INTERMEDIATE POSTURE KEEPS GUIDANCE ON BUT ASSUMES YOU KNOW SAMPLE, SCAN, AND PAPER BASICS.",
    "advanced": "ADVANCED POSTURE EXPECTS YOU WANT FASTER ACCESS TO CONTROL SURFACES.",
}
TEMPLATE_RECOMMENDATIONS = {"learn_and_scan": "Guided", "paper_arbitrage": "Recorder", "live_prepare": "Research", "lab_experiment": "Custom"}
RISK_RECOMMENDATIONS = {"learn_and_scan": "Starter", "paper_arbitrage": "Starter", "live_prepare": "Balanced", "lab_experiment": "Lab"}
PRESET_RECOMMENDATIONS = {"learn_and_scan": "continuous-record", "paper_arbitrage": "continuous-record", "live_prepare": "continuous-record", "lab_experiment": "fast-smoke-run"}
PHASE_LABELS = ["PHASE 01 // WAKE", "PHASE 02 // MISSION", "PHASE 03 // MODE", "PHASE 04 // LOADOUT", "PHASE 05 // CHECK", "PHASE 06 // IGNITION"]


class WelcomePage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("BOOT SEQUENCE")
        self.setSubTitle("PAPER-FIRST SIGNAL MACHINE. LOCAL-FIRST PROFILE CART.")
        layout = QVBoxLayout(self)
        intro = QLabel("LOAD A PROFILE CART, LOCK SAFE DEFAULTS, AND IGNITE THE FIRST SAMPLE LOOP. MOST OPERATORS REACH THE FIRST PAPER RUN WITHOUT KEYS.")
        intro.setWordWrap(True)
        intro.setObjectName("heroText")
        layout.addWidget(intro)
        boot_map = QGroupBox("BOOT MAP")
        boot_layout = QVBoxLayout(boot_map)
        for line in ("SELECT MISSION, POSTURE, AND CART MODE", "ARM POLYMARKET BY DEFAULT", "SKIP KEY SLOTS FOR SAMPLE + PAPER OR STORE THEM IN THE OS KEYCHAIN"):
            label = QLabel(f"- {line}")
            label.setWordWrap(True)
            boot_layout.addWidget(label)
        layout.addWidget(boot_map)
        layout.addStretch(1)


class IntentPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("MISSION SELECT")
        self.setSubTitle("PICK THE FIRST CART POSTURE.")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.goal_combo = QComboBox()
        self.goal_combo.addItem("LEARN POLYMARKET + SCAN SAFE", "learn_and_scan")
        self.goal_combo.addItem("RUN PAPER ARB IDEAS", "paper_arbitrage")
        self.goal_combo.addItem("PREP FOR GATE WORK", "live_prepare")
        self.goal_combo.addItem("OPEN LAB EXPERIMENTS", "lab_experiment")
        self.experience_combo = QComboBox()
        self.experience_combo.addItem("BEGINNER", "beginner")
        self.experience_combo.addItem("INTERMEDIATE", "intermediate")
        self.experience_combo.addItem("ADVANCED", "advanced")
        self.guided_mode_checkbox = QCheckBox("KEEP GUIDED BOOT ON")
        self.guided_mode_checkbox.setChecked(True)
        self.lab_checkbox = QCheckBox("EXPOSE LAB AFTER IGNITION")
        form.addRow("MISSION", self.goal_combo)
        form.addRow("POSTURE", self.experience_combo)
        form.addRow("", self.guided_mode_checkbox)
        form.addRow("", self.lab_checkbox)
        layout.addLayout(form)
        group = QGroupBox("MISSION READOUT")
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
        self.setTitle("MODE SELECT")
        self.setSubTitle("CUT A NEW PROFILE CART OR LOAD AN OLDER EXPORT.")
        layout = QVBoxLayout(self)
        intro = QLabel("LEAVE DATA SLOT BLANK UNLESS YOU NEED A CUSTOM PATH. SUPERIOR USES A PER-USER STORAGE BAY BY DEFAULT.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.name_edit = QLineEdit("MY SUPERIOR CART")
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Guided", "Recorder", "Research", "Custom"])
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setPlaceholderText("RECOMMENDED PER-USER STORAGE BAY")
        browse_button = QPushButton("BROWSE")
        browse_button.clicked.connect(self._browse_data_dir)
        data_dir_row = QHBoxLayout()
        data_dir_row.addWidget(self.data_dir_edit, stretch=1)
        data_dir_row.addWidget(browse_button)
        form.addRow("CART NAME", self.name_edit)
        form.addRow("MODE", self.template_combo)
        form.addRow("DATA SLOT", self._wrap_layout(data_dir_row))
        layout.addLayout(form)
        import_row = QHBoxLayout()
        self.import_path_edit = QLineEdit()
        self.import_path_edit.setPlaceholderText("OPTIONAL PROFILE JSON EXPORT")
        import_button = QPushButton("LOAD JSON")
        import_button.clicked.connect(self._browse_import_path)
        import_row.addWidget(self.import_path_edit, stretch=1)
        import_row.addWidget(import_button)
        import_label = QLabel("LOAD A PRIOR CART IF YOU ALREADY EXPORTED ONE. SECRETS STAY OUTSIDE THE JSON FILE.")
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
        self.setTitle("LOADOUT")
        self.setSubTitle("ARM THE CONNECTORS YOU WANT IN THIS CART.")
        layout = QVBoxLayout(self)
        self.polymarket_checkbox = QCheckBox("POLYMARKET")
        self.polymarket_checkbox.setChecked(True)
        self.kalshi_checkbox = QCheckBox("KALSHI")
        layout.addWidget(self.polymarket_checkbox)
        for text in ("DEFAULT SIGNAL FEED. PUBLIC SAMPLE DATA WORKS WITHOUT KEYS.", "OPTIONAL SECOND FEED. ARM IT LATER FOR CROSS-VENUE CHECKS."):
            label = QLabel(text)
            label.setWordWrap(True)
            layout.addWidget(label)
        layout.addWidget(self.kalshi_checkbox)
        hint = QLabel("ONE CONNECTOR IS ENOUGH TO IGNITE CLEANLY. THE GATE STILL REQUIRES KEY SETUP.")
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
        self.setTitle("KEY SLOT")
        self.setSubTitle("OPTIONAL FOR SAMPLE + PAPER MODE. SKIP FOR THE SAFE STARTER PATH.")
        self._providers = [provider for provider in providers if provider.provider_id in {"polymarket", "kalshi"}]
        self._field_widgets: dict[str, dict[str, QLineEdit | QPlainTextEdit]] = {}
        self._groups: dict[str, QGroupBox] = {}
        layout = QVBoxLayout(self)
        hint = QLabel("LEAVE THIS BLANK IF YOU ONLY WANT SAMPLE + PAPER FIRST. STORED KEYS NEVER GO INTO JSON, DUCKDB, OR LOGS.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        for provider in self._providers:
            group = QGroupBox(f"{provider.provider_label} KEY SLOT")
            group_layout = QFormLayout(group)
            docs_label = QLabel(f'<a href="{provider.docs_url}">OPEN {provider.provider_label} AUTH DOCS</a>')
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
                group_layout.addRow(field.label.upper(), widget)
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
        self.setTitle("POSTURE")
        self.setSubTitle("LOCK SAFE DEFAULTS NOW. RAISE COMPLEXITY LATER.")
        layout = QVBoxLayout(self)
        intro = QLabel("LOCK THE FIRST BOOT: WHICH PRESET STARTS, HOW TIGHT PAPER SIZING STAYS, AND WHETHER THE CART WAKES AT LOGIN.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.default_preset_combo = QComboBox()
        for preset_id, label in preset_labels:
            self.default_preset_combo.addItem(label, preset_id)
        self.market_filters_edit = QLineEdit()
        self.market_filters_edit.setPlaceholderText("ELECTIONS, SPORTS, CRYPTO")
        self.risk_policy_combo = QComboBox()
        for policy in default_risk_policies():
            self.risk_policy_combo.addItem(f"{policy.label} - {policy.description}", policy.id)
        self.auto_start_checkbox = QCheckBox("WAKE CART AT LOGIN")
        self.start_minimized_checkbox = QCheckBox("START MINIMIZED TO TRAY")
        form.addRow("BOOT PRESET", self.default_preset_combo)
        form.addRow("MARKET FILTERS", self.market_filters_edit)
        form.addRow("RISK POSTURE", self.risk_policy_combo)
        layout.addLayout(form)
        layout.addWidget(self.auto_start_checkbox)
        layout.addWidget(self.start_minimized_checkbox)
        group = QGroupBox("POSTURE READOUT")
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
        self.setTitle("COACH LINK")
        self.setSubTitle("OPTIONAL READ-ONLY HELP LINK. NEVER ARMS EXECUTION.")
        self._field_widgets: dict[str, QLineEdit | QPlainTextEdit] = {}
        layout = QVBoxLayout(self)
        intro = QLabel("LEAVE THIS OFF FOR THE CLEANEST CART. LOCAL DOCS AND PROFILE STATE STILL HANDLE THE FIRST LOOP.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.enable_checkbox = QCheckBox("ARM COACH LINK FOR THIS CART")
        layout.addWidget(self.enable_checkbox)
        group = QGroupBox(provider.provider_label.upper())
        form = QFormLayout(group)
        docs_label = QLabel(f'<a href="{provider.docs_url}">OPEN COACH DOCS</a>')
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
            form.addRow(field.label.upper(), widget)
            self._field_widgets[field.key] = widget
        layout.addWidget(group)
        hint = QLabel("BYO MODEL KEYS ARE OPTIONAL. THE MACHINE CAN STILL ANSWER FROM LOCAL DOCS + PROFILE STATE.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

    def payload(self) -> dict[str, str]:
        return {key: widget.toPlainText() if isinstance(widget, QPlainTextEdit) else widget.text() for key, widget in self._field_widgets.items()}


class FinishPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("FINAL CHECK")
        self.setSubTitle("LOCK THE CART SUMMARY BEFORE HANGAR IGNITION.")
        layout = QVBoxLayout(self)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)


class CompletionPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("IGNITION")
        self.setSubTitle("BOOT INTO HANGAR WITH THE SAMPLE LOOP ALREADY FRAMED.")
        layout = QVBoxLayout(self)
        intro = QLabel("SUPERIOR WILL OPEN HANGAR WITH THE FIRST SAFE COMMAND FRAMED CLEARLY.")
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
    def __init__(self, *, profile_store: ProfileStore, credential_vault: CredentialVault, startup_manager: StartupManager, preset_labels: list[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SUPERIOR // BOOT")
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.resize(920, 680)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setButtonText(QWizard.WizardButton.NextButton, "A NEXT")
        self.setButtonText(QWizard.WizardButton.BackButton, "B BACK")
        self.setButtonText(QWizard.WizardButton.CancelButton, "SELECT EXIT")
        self.setButtonText(QWizard.WizardButton.FinishButton, "START IGNITION")
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
        self._stepper = SetupStepper(PHASE_LABELS)
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
            self.coach_page.enable_checkbox.toggled,
        ):
            signal.connect(self._refresh_dynamic_content)
        for widgets in self.credentials_page._field_widgets.values():
            for widget in widgets.values():
                (widget.textChanged if isinstance(widget, QPlainTextEdit) else widget.textChanged).connect(self._refresh_dynamic_content)
        for widget in self.coach_page._field_widgets.values():
            (widget.textChanged if isinstance(widget, QPlainTextEdit) else widget.textChanged).connect(self._refresh_dynamic_content)
        self._refresh_dynamic_content()

    def _refresh_dynamic_content(self) -> None:
        self.credentials_page.set_enabled_providers([venue.lower() for venue in self.venue_page.selected_venues()])
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
                QMessageBox.warning(self, "ARM A FEED", "SELECT AT LEAST ONE CONNECTOR BEFORE IGNITION.")
                return
            data_dir = Path(self.profile_page.data_dir_edit.text().strip()) if self.profile_page.data_dir_edit.text().strip() else None
            profile = self._profile_store.create_profile(
                display_name=self.profile_page.name_edit.text().strip() or "MY SUPERIOR CART",
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
            selected_provider_ids = [venue.lower() for venue in selected_venues]
            for provider_id, payload in self.credentials_page.payloads().items():
                if provider_id not in selected_provider_ids or not any(value.strip() for value in payload.values()):
                    continue
                result = self._credential_vault.save(profile.id, provider_id, payload)
                if result.status == "invalid":
                    QMessageBox.warning(self, "FIX KEY SLOT", f"{provider_id.title()} KEY SLOT IS INCOMPLETE: {result.message.upper()}")
                    return
            if self.coach_page.enable_checkbox.isChecked():
                result = self._credential_vault.save(profile.id, "coach", self.coach_page.payload())
                if result.status == "invalid":
                    QMessageBox.warning(self, "FIX COACH LINK", result.message.upper())
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
        guided_line = "GUIDED BOOT STAYS ON." if self.intent_page.guided_mode_checkbox.isChecked() else "GUIDED BOOT IS OFF."
        lab_line = "LAB STAYS VISIBLE AFTER IGNITION." if self.intent_page.lab_checkbox.isChecked() else "LAB STAYS HIDDEN UNTIL LATER."
        return f"{goal_summary}\n\n{goal_detail}\n{experience_detail}\n\nRECOMMENDED MODE: {template}\nRECOMMENDED BOOT PRESET: {preset_label}\nRECOMMENDED RISK POSTURE: {risk_label}\n{guided_line}\n{lab_line}"

    def _risk_guidance_text(self) -> str:
        goal_id = self.intent_page.goal_combo.currentData()
        recommended_risk = RISK_RECOMMENDATIONS.get(goal_id, "Starter")
        recommended_preset = self._preset_labels.get(PRESET_RECOMMENDATIONS.get(goal_id, "continuous-record"), "Continuous recorder")
        startup_line = "THE CART WILL AUTO-WAKE WITH THIS PROFILE." if self.risk_page.auto_start_checkbox.isChecked() else "THE CART WAKES MANUALLY."
        tray_line = "START MINIMIZED IS ON." if self.risk_page.start_minimized_checkbox.isChecked() else "START MINIMIZED IS OFF."
        market_filters = ", ".join(self._market_filters()) or "NONE"
        return f"RECOMMENDED FOR THIS MISSION: {recommended_risk} RISK + {recommended_preset} BOOT PRESET.\n\nCURRENT PRESET: {self.risk_page.default_preset_combo.currentText()}\nCURRENT RISK POSTURE: {self.risk_page.risk_policy_combo.currentText()}\nMARKET FILTERS: {market_filters}\n{startup_line}\n{tray_line}"

    def _summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return f"IMPORT MODE\nSOURCE JSON: {self.profile_page.import_path_edit.text().strip()}\nSECRETS STAY OUTSIDE THE JSON FILE.\nSUPERIOR WILL OPEN HANGAR AFTER IMPORT."
        venues = ", ".join(self.venue_page.selected_venues()) or "NONE"
        default_preset = self.risk_page.default_preset_combo.currentText() or "Continuous recorder"
        selected_provider_ids = [venue.lower() for venue in self.venue_page.selected_venues()]
        credential_labels = [self._provider_labels.get(provider_id, provider_id.title()) for provider_id, payload in self.credentials_page.payloads().items() if provider_id in selected_provider_ids and any(value.strip() for value in payload.values())]
        data_dir = self.profile_page.data_dir_edit.text().strip() or "RECOMMENDED PER-USER STORAGE BAY"
        return (
            f"NEW CART SUMMARY\nCART: {self.profile_page.name_edit.text().strip() or 'MY SUPERIOR CART'}\nMODE: {self.profile_page.template_combo.currentText()}\nMISSION: {self.intent_page.goal_combo.currentText()}\nPOSTURE: {self.intent_page.experience_combo.currentText()}\nLOADOUT: {venues}\nDATA SLOT: {data_dir}\nBOOT PRESET: {default_preset}\nRISK POSTURE: {self.risk_page.risk_policy_combo.currentText()}\nGUIDED BOOT: {'ON' if self.intent_page.guided_mode_checkbox.isChecked() else 'OFF'}\nLAB: {'ON' if self.intent_page.lab_checkbox.isChecked() else 'OFF'}\nCONNECTOR KEYS ENTERED NOW: {', '.join(credential_labels) if credential_labels else 'NONE'}\nCOACH LINK: {'ARMED' if self.coach_page.enable_checkbox.isChecked() else 'OFFLINE'}\nIGNITION PLAN:\n- OPEN HANGAR AND BOOT THE RECORDER.\n- RUN SCAN AFTER THE FIRST SAMPLE LANDS.\n- START ONE PAPER RUN AND USE SCORE AS THE MAIN PROGRESSION SURFACE."
        )

    def _completion_summary_text(self) -> str:
        if self.profile_page.import_path_edit.text().strip():
            return "IMPORTED CARTS STILL LAND IN HANGAR WITH THE SAME SAFE DEFAULT: BOOT FIRST, THEN STAGE ONE ROUTE."
        selected_venues = ", ".join(self.venue_page.selected_venues()) or "POLYMARKET"
        return f"LOADOUT READY: {selected_venues}. RISK POSTURE: {self.risk_page.risk_policy_combo.currentText()}. HANGAR OPENS WITH THE BOOT LIST VISIBLE."

    def _completion_route(self) -> SetupCompletionRoute:
        if self.profile_page.import_path_edit.text().strip():
            return SetupCompletionRoute(title="IMPORTED CART ROUTES TO HANGAR", detail="SUPERIOR OPENS HANGAR, PRESERVES THE IMPORTED LOADOUT, AND KEEPS BOOT RECORDER FRAMED.")
        if self.venue_page.kalshi_checkbox.isChecked():
            return SetupCompletionRoute(title="HANGAR OPENS WITH BOOT PRIORITY", detail="POLYMARKET STAYS THE FIRST PASS. KALSHI REMAINS ARMED, BUT BOOT RECORDER STILL GETS TOP PRIORITY.")
        return SetupCompletionRoute(title="HANGAR HIGHLIGHTS BOOT RECORDER", detail="SUPERIOR OPENS HANGAR, SHOWS THE BOOT LIST, AND KEEPS BOOT RECORDER DOMINANT UNTIL THE FIRST SAMPLE LANDS.")

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
        if current_page_id in {self._venue_id, self._credentials_id, self._coach_id}:
            return 3
        if current_page_id == self._finish_id:
            return 4
        return 5
