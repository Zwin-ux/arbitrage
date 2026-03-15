from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
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
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .app_types import (
    AppProfile,
    AssistantSession,
    CapabilityState,
    ConnectorLoadout,
    CredentialStatus,
    EngineStatus,
    ExperimentalLiveStatus,
    LiveUnlockChecklist,
    OpportunityCandidate,
    PaperRunResult,
    PortfolioSummary,
    ScoreLedgerEntry,
    ScoreSnapshot,
    StrategyModule,
    VenueConnection,
)
from .bot_services import (
    AssistantService,
    CapabilityService,
    ConnectorLoadoutService,
    ExperimentalLiveService,
    LiveExecutionEngine,
    OpportunityEngine,
    PaperExecutionEngine,
    PaperRunStore,
    ScoreService,
    UnlockService,
    VenueAdapter,
)
from .controller import EngineController
from .credentials import CredentialVault
from .diagnostics import DiagnosticsService
from .paths import AppPaths
from .profiles import ProfileStore
from .startup import StartupManager
from .wizard import SetupWizard


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class HomeTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self.safe_state_label = QLabel("Paper mode active | Live gate locked | Lab off")
        self.safe_state_label.setObjectName("heroTitle")
        self.next_step_label = QLabel("Create a loadout and record your first local Polymarket book.")
        self.next_step_label.setWordWrap(True)
        layout.addWidget(self.safe_state_label)
        layout.addWidget(self.next_step_label)

        mission_group = QGroupBox("Mission board")
        mission_layout = QVBoxLayout(mission_group)
        self.mission_label = QLabel("Mission: Equip Polymarket and record your first book.")
        self.mission_label.setObjectName("heroText")
        self.mission_label.setWordWrap(True)
        self.score_label = QLabel("Paper score: waiting for first run")
        self.score_label.setWordWrap(True)
        mission_layout.addWidget(self.mission_label)
        mission_layout.addWidget(self.score_label)
        layout.addWidget(mission_group)

        setup_group = QGroupBox("Launch lane")
        setup_layout = QVBoxLayout(setup_group)
        self.setup_progress_label = QLabel("Most users can finish the first-run path in a few minutes.")
        self.setup_progress_label.setObjectName("heroText")
        self.setup_progress_label.setWordWrap(True)
        self.setup_steps_label = QLabel()
        self.setup_steps_label.setWordWrap(True)
        self.setup_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        setup_actions = QHBoxLayout()
        self.open_setup_button = QPushButton("Open guided setup")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("View trust docs")
        self.view_docs_button.setProperty("buttonRole", "secondary")
        setup_actions.addWidget(self.open_setup_button)
        setup_actions.addWidget(self.view_docs_button)
        setup_actions.addStretch(1)
        setup_layout.addWidget(self.setup_progress_label)
        setup_layout.addWidget(self.setup_steps_label)
        setup_layout.addLayout(setup_actions)
        layout.addWidget(setup_group)

        loop_group = QGroupBox("Golden path")
        loop_layout = QVBoxLayout(loop_group)
        self.loop_label = QLabel("Golden path: 0 of 4 milestones complete")
        self.loop_label.setObjectName("heroText")
        self.loop_label.setWordWrap(True)
        self.loop_steps_label = QLabel()
        self.loop_steps_label.setWordWrap(True)
        self.loop_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        loop_layout.addWidget(self.loop_label)
        loop_layout.addWidget(self.loop_steps_label)
        layout.addWidget(loop_group)

        action_row = QHBoxLayout()
        self.start_button = QPushButton("Boot recorder")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("buttonRole", "secondary")
        self.replay_button = QPushButton("Replay")
        self.replay_button.setProperty("buttonRole", "secondary")
        self.verify_button = QPushButton("Verify")
        self.verify_button.setProperty("buttonRole", "secondary")
        self.scan_button = QPushButton("Scan edge")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Paper top route")
        self.paper_button.setProperty("buttonRole", "secondary")
        for button in (
            self.start_button,
            self.stop_button,
            self.replay_button,
            self.verify_button,
            self.scan_button,
            self.paper_button,
        ):
            action_row.addWidget(button)
        layout.addLayout(action_row)

        status_group = QGroupBox("Hangar state")
        status_layout = QFormLayout(status_group)
        self.brand_label = QLabel("Superior")
        self.profile_label = QLabel("No profile selected")
        self.goal_label = QLabel("No goal set")
        self.engine_label = QLabel("Idle")
        self.data_label = QLabel("No database yet")
        self.risk_label = QLabel("Starter")
        self.warning_label = QLabel("No warnings")
        self.warning_label.setWordWrap(True)
        status_layout.addRow("Brand", self.brand_label)
        status_layout.addRow("Profile", self.profile_label)
        status_layout.addRow("Goal", self.goal_label)
        status_layout.addRow("Recorder", self.engine_label)
        status_layout.addRow("Data", self.data_label)
        status_layout.addRow("Risk preset", self.risk_label)
        status_layout.addRow("Latest warning", self.warning_label)
        layout.addWidget(status_group)

        capability_group = QGroupBox("Capability lights")
        capability_layout = QVBoxLayout(capability_group)
        self.capability_text = QPlainTextEdit()
        self.capability_text.setReadOnly(True)
        capability_layout.addWidget(self.capability_text)
        layout.addWidget(capability_group)

        connections_group = QGroupBox("Equipped connectors")
        connections_layout = QVBoxLayout(connections_group)
        self.connections_text = QPlainTextEdit()
        self.connections_text.setReadOnly(True)
        connections_layout.addWidget(self.connections_text)
        layout.addWidget(connections_group)
        layout.addStretch(1)

    def update_view(
        self,
        *,
        profile: AppProfile | None,
        status: EngineStatus,
        connections: list[VenueConnection],
        checklist: LiveUnlockChecklist | None,
        score_snapshot: ScoreSnapshot,
        capability_states: list[CapabilityState],
    ) -> None:
        if profile is None:
            self.brand_label.setText("Superior")
            self.profile_label.setText("No profile selected")
            self.goal_label.setText("Create your first loadout")
            self.engine_label.setText(status.state.title())
            self.data_label.setText("No database yet")
            self.risk_label.setText("No risk policy")
            self.warning_label.setText("No warnings")
            self.safe_state_label.setText("Paper mode active | Live gate locked | Lab off")
            self.next_step_label.setText("Use setup to create a Superior profile and equip Polymarket.")
            self.mission_label.setText("Mission: Equip Polymarket and record your first book.")
            self.score_label.setText("Paper score: waiting for first run")
            self.setup_progress_label.setText(
                "The easiest start is a guided loadout with Polymarket equipped, no credentials yet, and one clean recorder sample."
            )
            self.setup_steps_label.setText(
                "1. Create your first profile with Guided mode on.\n"
                "2. Equip Polymarket and leave credentials blank if you only want recorder plus paper mode.\n"
                "3. Boot the recorder, then scan edge after market data appears."
            )
            self.loop_label.setText("Golden path: 0 of 4 milestones complete")
            self.loop_steps_label.setText(
                "[NEXT] Equip Polymarket loadout - Create a guided profile with Polymarket equipped.\n"
                "[WAIT] Record local sample - Recorder stays off until a profile exists.\n"
                "[WAIT] Inspect scanner route - Scanner waits for local market data.\n"
                "[WAIT] Earn paper score - Score lights up after the first paper route."
            )
            self.open_setup_button.setText("Create first profile")
            self.capability_text.setPlainText(
                "Recorder: blocked until Polymarket is equipped.\n"
                "Scanner: blocked until recorder data exists.\n"
                "Paper score: blocked until the first paper run lands."
            )
            self.connections_text.setPlainText("No active venue connections.")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.replay_button.setEnabled(False)
            self.verify_button.setEnabled(False)
            self.scan_button.setEnabled(False)
            self.paper_button.setEnabled(False)
            return
        has_data = status.summary is not None and (
            status.summary.raw_messages > 0 or status.summary.book_snapshots > 0
        )
        is_running = status.state == "running"
        live_state_map = {
            "locked": "Live gate locked",
            "shadow": "Shadow live staged",
            "micro": "Micro live staged",
            "experimental": "Experimental live staged",
        }
        live_state = live_state_map.get(profile.live_mode, "Live gate locked")
        lab_state = "Lab on" if profile.lab_enabled else "Lab off"
        self.safe_state_label.setText(f"Paper mode active | {live_state} | {lab_state}")
        scanner_ready = any(state.capability_id == "scanner" and state.ready for state in capability_states)
        loadout_ready = "polymarket" in profile.equipped_connectors and bool(profile.equipped_modules)
        score_ready = score_snapshot.total_runs > 0
        if not loadout_ready:
            self.next_step_label.setText("Next step: save a loadout with Polymarket and at least one strategy module.")
        elif is_running:
            self.next_step_label.setText("Next step: let the recorder finish a clean local sample, then refresh scan.")
        elif not has_data:
            self.next_step_label.setText("Next step: boot the recorder so Superior has local books to inspect.")
        elif not score_ready:
            self.next_step_label.setText("Next step: inspect a scanner route and paper it to light up the score board.")
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            self.next_step_label.setText(
                "Next step: keep scoring in paper mode or stage shadow live if you want an experimental dry run."
            )
        elif checklist is not None and checklist.outstanding:
            self.next_step_label.setText("Next step: keep the paper loop healthy. Live-gate items are optional for now.")
        else:
            self.next_step_label.setText("Next step: keep recorder data healthy and grow paper score with discipline.")
        self.brand_label.setText(profile.brand_name)
        self.profile_label.setText(profile.display_name)
        self.goal_label.setText(profile.primary_goal.replace("_", " ").title())
        self.engine_label.setText(f"{status.state.title()} - {status.last_message}")
        self.risk_label.setText(profile.risk_policy_id.title())
        self.mission_label.setText(f"Mission: {profile.primary_mission}")
        if score_snapshot.total_runs:
            self.score_label.setText(
                f"Paper score ${score_snapshot.paper_realized_pnl_cents / 100:.2f} | "
                f"Runs {score_snapshot.completed_runs} | Hit rate {score_snapshot.hit_rate:.1f}%"
            )
        else:
            self.score_label.setText("Paper score: waiting for first run")
        if status.summary is not None:
            self.data_label.setText(
                f"{status.summary.raw_messages} raw messages, {status.summary.book_snapshots} books"
            )
            self.warning_label.setText(status.summary.latest_warning or "No warnings")
        else:
            self.data_label.setText("No database yet")
            self.warning_label.setText("No warnings")
        self.connections_text.setPlainText(
            "\n".join(
                f"{connection.venue_label}: {connection.mode} - {connection.message}"
                for connection in connections
            )
            or "No active venue connections."
        )
        self.capability_text.setPlainText(
            "\n".join(
                f"{state.label}: {'ready' if state.ready else 'blocked'} - {state.message}"
                for state in capability_states
            )
        )
        step_specs = [
            (
                "Equip loadout",
                loadout_ready,
                "Polymarket and at least one strategy module are equipped."
                if loadout_ready
                else "Save a loadout with Polymarket and one strategy module.",
            ),
            (
                "Record local sample",
                has_data,
                "Local recorder data is present and ready for the scanner."
                if has_data
                else "Boot the recorder and wait for raw messages plus book snapshots.",
            ),
            (
                "Inspect scanner route",
                scanner_ready,
                "Scanner explanations are ready to inspect the next route."
                if scanner_ready
                else "Recorder data has to land before the scanner becomes useful.",
            ),
            (
                "Earn paper score",
                score_ready,
                "Paper score is live in the local ledger."
                if score_ready
                else "Run one paper route to create the first score entry.",
            ),
        ]
        completed_steps = sum(1 for _label, ready, _message in step_specs if ready)
        self.loop_label.setText(f"Golden path: {completed_steps} of {len(step_specs)} milestones complete")
        first_incomplete_seen = False
        loop_lines: list[str] = []
        for label, ready, message in step_specs:
            if ready:
                marker = "DONE"
            elif not first_incomplete_seen:
                marker = "NEXT"
                first_incomplete_seen = True
            else:
                marker = "WAIT"
            loop_lines.append(f"[{marker}] {label} - {message}")
        self.loop_steps_label.setText("\n".join(loop_lines))
        self.open_setup_button.setText("Edit setup")
        if profile.live_unlocked:
            self.setup_progress_label.setText(
                "This profile has cleared the local gate. Keep score, diagnostics, and connector state explicit."
            )
            self.setup_steps_label.setText(
                "1. Recorder, scanner, and paper score are already in place.\n"
                "2. Revisit Loadout if you want to change connectors or strategy modules.\n"
                "3. Treat live execution as a separate decision, not the default workflow."
            )
        elif is_running:
            self.setup_progress_label.setText(
                "Recorder is running now. Let it gather a sample so the scanner can read real local market data."
            )
            self.setup_steps_label.setText(
                "1. Wait for message and book counts to grow in Hangar state.\n"
                "2. Scan edge when the recorder finishes or once the data looks healthy.\n"
                "3. Paper the top route before thinking about live readiness."
            )
        elif not has_data:
            self.setup_progress_label.setText(
                "Loadout is nearly complete. The next useful step is a first recorder pass so the rest of the product has context."
            )
            self.setup_steps_label.setText(
                "1. Click Boot recorder to build your local database.\n"
                "2. Watch for raw message and book counts to appear.\n"
                "3. Scan edge, then run a paper test from Hangar or Scanner."
            )
        elif checklist is not None and checklist.outstanding:
            outstanding = "\n".join(
                f"- {check.label}: {check.message}" for check in checklist.outstanding[:3]
            )
            self.setup_progress_label.setText(
                "Paper workflow is healthy. The remaining gate items are optional until you intentionally want live readiness."
            )
            self.setup_steps_label.setText(
                "Outstanding live-gate items:\n"
                f"{outstanding}\n"
                "You can keep using recorder, scanner, and paper score without finishing these right now."
            )
        elif profile.live_mode == "shadow":
            self.setup_progress_label.setText(
                "Shadow live is staged. Superior can now record would-be live decisions while keeping real orders off."
            )
            self.setup_steps_label.setText(
                "1. Keep scanning and papering so the score board stays honest.\n"
                "2. Use Scanner preview to inspect the live plan before thinking about micro-live.\n"
                "3. Only arm micro-live after credentials and diagnostics stay clean."
            )
        elif profile.live_mode in {"micro", "experimental"}:
            self.setup_progress_label.setText(
                "Experimental live is armed. Keep caps tiny, diagnostics clear, and treat paper score as the primary truth."
            )
            self.setup_steps_label.setText(
                "1. Use Scanner preview to confirm each candidate still clears the live gate.\n"
                "2. Keep loadout scope narrow and avoid enabling extra connectors casually.\n"
                "3. Reset to locked if diagnostics or confidence degrade."
            )
        else:
            self.setup_progress_label.setText(
                "This profile is in a clean paper-first state with local data ready for scanning and paper score."
            )
            self.setup_steps_label.setText(
                "1. Scan edge whenever you want the newest candidates.\n"
                "2. Use Paper Runs or the Hangar quick action to test the top opportunity.\n"
                "3. Revisit Loadout only if you want to change connectors, coach, or modules."
            )
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.replay_button.setEnabled(has_data and not is_running)
        self.verify_button.setEnabled(has_data and not is_running)
        self.scan_button.setEnabled(has_data)
        self.paper_button.setEnabled(has_data)


class LoadoutTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel("Equip connectors and modules to shape what the app exposes.")
        self.header_label.setObjectName("heroTitle")
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)

        connectors_group = QGroupBox("Connector loadout")
        connectors_layout = QVBoxLayout(connectors_group)
        self.polymarket_checkbox = QCheckBox("Equip Polymarket Connector")
        self.kalshi_checkbox = QCheckBox("Equip Kalshi Connector")
        self.coach_checkbox = QCheckBox("Equip Coach Link")
        for checkbox in (self.polymarket_checkbox, self.kalshi_checkbox, self.coach_checkbox):
            connectors_layout.addWidget(checkbox)
        layout.addWidget(connectors_group)

        modules_group = QGroupBox("Strategy loadout")
        modules_layout = QVBoxLayout(modules_group)
        self.internal_binary_checkbox = QCheckBox("Equip Internal Binary")
        self.cross_venue_checkbox = QCheckBox("Equip Cross-Venue")
        self.neg_risk_checkbox = QCheckBox("Equip Neg Risk Lab")
        self.maker_lab_checkbox = QCheckBox("Equip Maker Lab")
        for checkbox in (
            self.internal_binary_checkbox,
            self.cross_venue_checkbox,
            self.neg_risk_checkbox,
            self.maker_lab_checkbox,
        ):
            modules_layout.addWidget(checkbox)
        layout.addWidget(modules_group)

        action_row = QHBoxLayout()
        self.save_button = QPushButton("Save loadout")
        self.refresh_button = QPushButton("Refresh status")
        self.refresh_button.setProperty("buttonRole", "secondary")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.refresh_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.state_text = QPlainTextEdit()
        self.state_text.setReadOnly(True)
        layout.addWidget(self.state_text)
        layout.addStretch(1)

    def update_view(
        self,
        profile: AppProfile | None,
        *,
        loadout: ConnectorLoadout | None,
        connector_states: list[CapabilityState],
        module_states: list[CapabilityState],
    ) -> None:
        if profile is None or loadout is None:
            self.header_label.setText("Create a profile to equip your first connector.")
            self.state_text.setPlainText("No loadout yet.")
            for checkbox in (
                self.polymarket_checkbox,
                self.kalshi_checkbox,
                self.coach_checkbox,
                self.internal_binary_checkbox,
                self.cross_venue_checkbox,
                self.neg_risk_checkbox,
                self.maker_lab_checkbox,
            ):
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
            self.save_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            return
        self.header_label.setText(f"Loadout for {profile.display_name}")
        connector_ids = set(loadout.equipped_connectors)
        module_ids = set(loadout.equipped_modules)
        self.polymarket_checkbox.setChecked("polymarket" in connector_ids)
        self.kalshi_checkbox.setChecked("kalshi" in connector_ids)
        self.coach_checkbox.setChecked("coach" in connector_ids)
        self.internal_binary_checkbox.setChecked("internal-binary" in module_ids)
        self.cross_venue_checkbox.setChecked("cross-venue-complement" in module_ids)
        self.neg_risk_checkbox.setChecked("negative-risk-basket" in module_ids)
        self.maker_lab_checkbox.setChecked("maker-rebate-lab" in module_ids)
        self.polymarket_checkbox.setEnabled(True)
        self.kalshi_checkbox.setEnabled(True)
        self.coach_checkbox.setEnabled(True)
        self.internal_binary_checkbox.setEnabled(True)
        self.cross_venue_checkbox.setEnabled(True)
        self.neg_risk_checkbox.setEnabled(profile.lab_enabled)
        self.maker_lab_checkbox.setEnabled(profile.lab_enabled)
        self.save_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        lines = [f"Primary mission: {profile.primary_mission}", ""]
        lines.append("Connector lights:")
        lines.extend(
            f"- {state.label}: {'equipped' if state.equipped else 'idle'} / {'ready' if state.ready else 'blocked'}"
            f" - {state.message}"
            for state in connector_states
        )
        lines.append("")
        lines.append("Module lights:")
        lines.extend(
            f"- {state.label}: {'equipped' if state.equipped else 'idle'} / {'ready' if state.ready else 'blocked'}"
            f" - {state.message}"
            for state in module_states
        )
        self.state_text.setPlainText("\n".join(lines))


class LearnTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        intro_group = QGroupBox("Learn first")
        intro_layout = QVBoxLayout(intro_group)
        for line in (
            "Superior is paper-first by default. The coach can explain what the scanner sees, but it cannot place trades.",
            "Use the recorder to gather local Polymarket books, then scan edge to surface explainable opportunities.",
            "Kalshi stays optional until you want to compare exact cross-venue matches.",
        ):
            label = QLabel(line)
            label.setWordWrap(True)
            intro_layout.addWidget(label)
        layout.addWidget(intro_group)

        coach_group = QGroupBox("Ask the coach")
        coach_layout = QVBoxLayout(coach_group)
        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setPlaceholderText("Why was this route rejected?\nWhat blocks the live gate?\nExplain my loadout.")
        self.ask_button = QPushButton("Ask coach")
        self.response_text = QPlainTextEdit()
        self.response_text.setReadOnly(True)
        coach_layout.addWidget(self.prompt_edit)
        coach_layout.addWidget(self.ask_button)
        coach_layout.addWidget(self.response_text)
        layout.addWidget(coach_group)
        layout.addStretch(1)

    def set_response(self, session: AssistantSession) -> None:
        last_message = session.messages[-1].content if session.messages else ""
        sources = ", ".join(session.sources) if session.sources else "local profile state"
        self.response_text.setPlainText(f"{last_message}\n\nSources: {sources}")


class ScannerTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel(
            "Scanner reads your local market sample and explains whether a route survives cost deductions."
        )
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)
        actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh scan")
        self.paper_button = QPushButton("Paper selected")
        self.live_preview_button = QPushButton("Preview live lock")
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.paper_button)
        actions.addWidget(self.live_preview_button)
        layout.addLayout(actions)

        self.candidate_list = QListWidget()
        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.candidate_list)
        layout.addWidget(self.details_text)

    def update_candidates(self, candidates: list[OpportunityCandidate]) -> None:
        self.candidate_list.clear()
        for candidate in candidates:
            item = QListWidgetItem(
                f"{candidate.strategy_label} | {candidate.net_edge_bps} bps | {candidate.status}"
            )
            item.setData(32, candidate.id)
            self.candidate_list.addItem(item)
        if not candidates:
            self.details_text.setPlainText(
                "No scanner candidates yet.\n\n"
                "The fastest path is:\n"
                "1. Record one clean local sample.\n"
                "2. Refresh scan.\n"
                "3. Paper the first route that still clears net edge."
            )

    def set_details(self, candidate: OpportunityCandidate | None) -> None:
        if candidate is None:
            self.details_text.setPlainText("Choose a scanner result to inspect the full explanation.")
            return
        deductions = (
            [f"- {key.replace('_', ' ')}: {value} bps" for key, value in candidate.explanation.cost_adjustments_bps.items()]
            or ["- none"]
        )
        matched_contracts = candidate.explanation.matched_contracts or ["No exact contract pair was attached."]
        assumptions = candidate.explanation.assumptions or ["No extra assumptions recorded."]
        self.details_text.setPlainText(
            "\n".join(
                [
                    f"Candidate: {candidate.strategy_label}",
                    f"Status: {candidate.status}",
                    f"What the scanner saw: {candidate.summary}",
                    f"Gross edge before deductions: {candidate.gross_edge_bps} bps",
                    f"Net edge after deductions: {candidate.net_edge_bps} bps",
                    f"Venues in play: {', '.join(candidate.venues)}",
                    f"Suggested paper stake: ${candidate.recommended_stake_cents / 100:.2f}",
                    (
                        "Suggested next move: paper this route and watch how it lands in Score."
                        if candidate.net_edge_bps > 0
                        else "Suggested next move: skip this route and wait for a cleaner net-positive setup."
                    ),
                    "",
                    "Why it passed or failed",
                    candidate.explanation.summary,
                    "",
                    "What matched",
                    *[f"- {item}" for item in matched_contracts],
                    "",
                    "Assumptions still in play",
                    *[f"- {item}" for item in assumptions],
                    "",
                    "Deductions from gross edge",
                    *deductions,
                ]
            )
        )


class PaperBotsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel(
            "Paper Runs turns scanner ideas into a local score history. This is the main progression loop in v1."
        )
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)
        actions = QHBoxLayout()
        self.run_top_button = QPushButton("Paper top route")
        self.refresh_button = QPushButton("Refresh runs")
        actions.addWidget(self.run_top_button)
        actions.addWidget(self.refresh_button)
        layout.addLayout(actions)

        self.last_run_text = QPlainTextEdit()
        self.last_run_text.setReadOnly(True)
        self.runs_list = QListWidget()
        layout.addWidget(self.last_run_text)
        layout.addWidget(self.runs_list)

    def update_runs(self, runs: list[PaperRunResult]) -> None:
        self.runs_list.clear()
        for run in reversed(runs[-20:]):
            self.runs_list.addItem(
                f"{run.executed_at.isoformat()} | {run.status} | paper ${run.realized_pnl_cents / 100:.2f}"
            )
        if not runs:
            self.last_run_text.setPlainText(
                "No paper runs yet.\n\n"
                "The shortest path is:\n"
                "1. Record a local sample.\n"
                "2. Inspect one scanner route.\n"
                "3. Paper it, then check Score."
            )

    def set_last_run(self, run: PaperRunResult | None) -> None:
        if run is None:
            self.last_run_text.setPlainText("Run one paper route to create your first score entry and recent-run card.")
            return
        self.last_run_text.setPlainText(
            "\n".join(
                [
                    f"Run ID: {run.run_id}",
                    f"Status: {run.status}",
                    f"Expected edge: {run.expected_edge_bps} bps",
                    f"Realized edge: {run.realized_edge_bps} bps",
                    f"Fill ratio: {run.execution.fill_ratio:.2f}",
                    f"Deployed capital: ${run.deployed_capital_cents / 100:.2f}",
                    f"Realized paper PnL: ${run.realized_pnl_cents / 100:.2f}",
                    f"Opportunity quality: {run.opportunity_quality_score}",
                    f"Notes: {run.notes}",
                ]
            )
        )


class ScoreTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary_label = QLabel("Paper Score waiting for first route | Live Score locked")
        self.summary_label.setObjectName("heroTitle")
        self.summary_label.setWordWrap(True)
        self.mode_label = QLabel(
            "Paper score is the main progression system in v1. Live score stays empty until a future release."
        )
        self.mode_label.setWordWrap(True)
        self.detail_text = QPlainTextEdit()
        self.detail_text.setReadOnly(True)
        self.ledger_text = QPlainTextEdit()
        self.ledger_text.setReadOnly(True)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.detail_text)
        layout.addWidget(self.ledger_text)
        layout.addStretch(1)

    def update_summary(
        self,
        snapshot: ScoreSnapshot,
        ledger_entries: list[ScoreLedgerEntry],
        runs: list[PaperRunResult],
    ) -> None:
        if not runs:
            self.summary_label.setText("Paper Score waiting for first route | Live Score locked")
            self.detail_text.setPlainText(
                "Paper score is the main loop in Superior v1.\n\n"
                "1. Record a local sample.\n"
                "2. Inspect one scanner route.\n"
                "3. Paper it.\n"
                "4. Come back here for the first score update."
            )
            self.ledger_text.setPlainText(
                "No ledger entries yet.\n\n"
                "Your first paper route will create stake and realized-PnL entries here."
            )
            return
        self.summary_label.setText(
            f"Paper Score ${snapshot.paper_realized_pnl_cents / 100:.2f} | "
            f"Runs {snapshot.completed_runs} | Hit {snapshot.hit_rate:.1f}%"
        )
        lines = [
            f"Total paper runs: {snapshot.total_runs}",
            f"Completed runs: {snapshot.completed_runs}",
            f"Average expected edge: {snapshot.average_expected_edge_bps} bps",
            f"Average realized edge: {snapshot.average_realized_edge_bps} bps",
            f"Current positive streak: {snapshot.current_streak}",
            f"Opportunity quality: {snapshot.opportunity_quality_score}",
            "Live score: reserved for a later release and intentionally empty in v1.",
            "",
            "Recent paper routes:",
        ]
        lines.extend(
            f"- {run.strategy_ids[0] if run.strategy_ids else 'unknown'} | {run.status} | ${run.realized_pnl_cents / 100:.2f}"
            for run in reversed(runs[-5:])
        )
        self.detail_text.setPlainText("\n".join(lines))
        self.ledger_text.setPlainText(
            "\n".join(
                f"{entry.recorded_at.isoformat()} | {entry.ledger_type} | ${entry.amount_cents / 100:.2f}"
                for entry in ledger_entries
            )
            or "No ledger entries yet."
        )


class LiveUnlockTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary_label = QLabel("Live gate is locked.")
        self.summary_label.setObjectName("heroTitle")
        self.summary_label.setWordWrap(True)
        self.mode_label = QLabel(
            "Experimental Live graduates from paper into shadow, then tiny Polymarket live modes."
        )
        self.mode_label.setWordWrap(True)
        self.checklist_text = QPlainTextEdit()
        self.checklist_text.setReadOnly(True)
        self.policy_text = QPlainTextEdit()
        self.policy_text.setReadOnly(True)
        self.live_rules_checkbox = QCheckBox("I understand that Superior does not guarantee profits and that live trading can lose money.")
        self.risk_ack_checkbox = QCheckBox("I understand the active risk policy and daily loss caps.")
        actions = QHBoxLayout()
        self.save_button = QPushButton("Save acknowledgements")
        self.refresh_button = QPushButton("Refresh checklist")
        self.shadow_button = QPushButton("Enter shadow")
        self.shadow_button.setProperty("buttonRole", "secondary")
        self.micro_button = QPushButton("Arm micro-live")
        self.micro_button.setProperty("buttonRole", "secondary")
        self.experimental_button = QPushButton("Arm experimental")
        self.experimental_button.setProperty("buttonRole", "secondary")
        self.reset_button = QPushButton("Reset to locked")
        self.reset_button.setProperty("buttonRole", "secondary")
        actions.addWidget(self.save_button)
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.shadow_button)
        actions.addWidget(self.micro_button)
        actions.addWidget(self.experimental_button)
        actions.addWidget(self.reset_button)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.checklist_text)
        layout.addWidget(self.policy_text)
        layout.addWidget(self.live_rules_checkbox)
        layout.addWidget(self.risk_ack_checkbox)
        layout.addLayout(actions)
        layout.addStretch(1)

    def update_view(
        self,
        profile: AppProfile | None,
        checklist: LiveUnlockChecklist | None,
        live_status: ExperimentalLiveStatus | None,
    ) -> None:
        if profile is None or checklist is None or live_status is None:
            self.summary_label.setText("Live gate is locked.")
            self.mode_label.setText("Choose a profile to inspect the experimental live rollout.")
            self.checklist_text.setPlainText("Choose a profile to see the live-gate checklist.")
            self.policy_text.setPlainText("No experimental live profile loaded.")
            self.shadow_button.setEnabled(False)
            self.micro_button.setEnabled(False)
            self.experimental_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            return
        self.live_rules_checkbox.setChecked(profile.live_rules_accepted)
        self.risk_ack_checkbox.setChecked(profile.risk_limits_acknowledged)
        mode_titles = {
            "locked": "Live gate is locked.",
            "shadow": "Shadow live is armed.",
            "micro": "Micro-live is armed.",
            "experimental": "Experimental live is armed.",
        }
        self.summary_label.setText(mode_titles.get(profile.live_mode, "Live gate is locked."))
        available = ", ".join(live_status.available_modes)
        self.mode_label.setText(
            f"Current mode: {profile.live_mode}. Recommended next mode: {live_status.recommended_mode}. "
            f"Available modes now: {available}."
        )
        lines = []
        for check in checklist.checks:
            status = "PASS" if check.passed else "BLOCKED"
            lines.append(f"[{status}] {check.label}")
            lines.append(f"  {check.message}")
        self.checklist_text.setPlainText("\n".join(lines))
        policy_lines = [
            f"Paper gate passed: {'yes' if live_status.paper_gate_passed else 'no'}",
            f"Venue scope: {', '.join(live_status.venue_scope) or 'none'}",
            f"Strategy scope: {', '.join(live_status.strategy_scope) or 'none'}",
            f"Position cap: ${live_status.position_cap_cents / 100:.2f}",
            f"Daily cap: ${live_status.daily_cap_cents / 100:.2f}",
            "",
            "Mode notes:",
        ]
        policy_lines.extend(f"- {note}" for note in live_status.notes)
        if live_status.warnings:
            policy_lines.extend(["", "Warnings:"])
            policy_lines.extend(f"- {warning}" for warning in live_status.warnings)
        self.policy_text.setPlainText("\n".join(policy_lines))
        self.shadow_button.setEnabled("shadow" in live_status.available_modes and profile.live_mode != "shadow")
        self.micro_button.setEnabled("micro" in live_status.available_modes and profile.live_mode != "micro")
        self.experimental_button.setEnabled(
            "experimental" in live_status.available_modes and profile.live_mode != "experimental"
        )
        self.reset_button.setEnabled(profile.live_mode != "locked" or profile.experimental_live_enabled)


class LabTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Lab is off.")
        self.status_label.setObjectName("heroTitle")
        self.enable_checkbox = QCheckBox("Enable Lab for this profile")
        self.save_button = QPushButton("Save Lab setting")
        self.modules_text = QPlainTextEdit()
        self.modules_text.setReadOnly(True)
        layout.addWidget(self.status_label)
        layout.addWidget(self.enable_checkbox)
        layout.addWidget(self.save_button)
        layout.addWidget(self.modules_text)
        layout.addStretch(1)

    def update_view(self, profile: AppProfile | None, modules: list[StrategyModule]) -> None:
        if profile is None:
            self.status_label.setText("Lab is off.")
            self.modules_text.setPlainText("Choose a profile to inspect Lab modules.")
            return
        self.enable_checkbox.setChecked(profile.lab_enabled)
        self.status_label.setText("Lab is on." if profile.lab_enabled else "Lab is off.")
        lines = [
            "High-risk and experimental strategies stay paper-only in v1.",
            "",
        ]
        for module in modules:
            if module.tier != "lab":
                continue
            lines.append(f"{module.label}: {module.description}")
        self.modules_text.setPlainText("\n".join(lines))


class DiagnosticsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export bundle")
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.export_button)
        layout.addLayout(actions)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)


class AboutTab(QWidget):
    def __init__(self, paths: AppPaths) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Trust and About")
        title.setObjectName("heroTitle")
        layout.addWidget(title)
        text = QLabel(
            "Superior is MIT-licensed, Windows-first, and local-first. It is built to teach and paper-test first, "
            "with explicit guardrails around live unlock."
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        release_group = QGroupBox("Product build")
        release_form = QFormLayout(release_group)
        release_form.addRow("Version", QLabel(__version__))
        release_form.addRow("Runtime", QLabel("Desktop app for recorder, scanner, paper runs, and diagnostics"))
        release_form.addRow("Storage posture", QLabel("Config and data stay local. Secrets stay in the OS keychain."))
        layout.addWidget(release_group)
        info_group = QGroupBox("Paths")
        info_form = QFormLayout(info_group)
        info_form.addRow("Config", QLabel(str(paths.config_dir)))
        info_form.addRow("Data", QLabel(str(paths.data_dir)))
        info_form.addRow("Logs", QLabel(str(paths.log_dir)))
        info_form.addRow("Exports", QLabel(str(paths.exports_dir)))
        layout.addWidget(info_group)
        buttons = QHBoxLayout()
        self.source_button = QPushButton("Source tree")
        self.readme_button = QPushButton("README")
        self.risk_button = QPushButton("Risk model")
        self.live_button = QPushButton("Live limits")
        self.privacy_button = QPushButton("Privacy")
        self.testing_button = QPushButton("Testing")
        self.issues_button = QPushButton("Open issues")
        self.contrib_button = QPushButton("Strategy guide")
        buttons.addWidget(self.source_button)
        buttons.addWidget(self.readme_button)
        buttons.addWidget(self.risk_button)
        buttons.addWidget(self.live_button)
        buttons.addWidget(self.privacy_button)
        buttons.addWidget(self.testing_button)
        buttons.addWidget(self.contrib_button)
        buttons.addWidget(self.issues_button)
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
        venue_adapters: list[VenueAdapter],
        loadout_service: ConnectorLoadoutService,
        capability_service: CapabilityService,
        opportunity_engine: OpportunityEngine,
        paper_store: PaperRunStore,
        score_service: ScoreService,
        paper_execution_engine: PaperExecutionEngine,
        experimental_live_service: ExperimentalLiveService,
        live_execution_engine: LiveExecutionEngine,
        unlock_service: UnlockService,
        assistant_service: AssistantService,
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
        self._venue_adapters = venue_adapters
        self._loadout_service = loadout_service
        self._capability_service = capability_service
        self._opportunity_engine = opportunity_engine
        self._paper_store = paper_store
        self._score_service = score_service
        self._paper_execution_engine = paper_execution_engine
        self._experimental_live_service = experimental_live_service
        self._live_execution_engine = live_execution_engine
        self._unlock_service = unlock_service
        self._assistant_service = assistant_service
        self._profiles: list[AppProfile] = []
        self._latest_candidates: list[OpportunityCandidate] = []
        self._last_paper_run: PaperRunResult | None = None
        self._previous_state = "idle"

        self.setWindowTitle("Superior")
        self.resize(1260, 880)

        self.home_tab = HomeTab()
        self.loadout_tab = LoadoutTab()
        self.learn_tab = LearnTab()
        self.scanner_tab = ScannerTab()
        self.paper_bots_tab = PaperBotsTab()
        self.score_tab = ScoreTab()
        self.live_unlock_tab = LiveUnlockTab()
        self.lab_tab = LabTab()
        self.diagnostics_tab = DiagnosticsTab()
        self.about_tab = AboutTab(paths)

        self.profile_selector = QComboBox()
        self.profile_selector.currentIndexChanged.connect(self._on_profile_changed)
        self.setup_button = QPushButton("Open guided setup")
        self.setup_button.setProperty("buttonRole", "secondary")
        self.setup_button.clicked.connect(self._open_setup_wizard)

        header = QHBoxLayout()
        header.addWidget(QLabel("Active profile"))
        header.addWidget(self.profile_selector, stretch=1)
        header.addWidget(self.setup_button)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.home_tab, "Hangar")
        self.tabs.addTab(self.loadout_tab, "Loadout")
        self.tabs.addTab(self.learn_tab, "Learn")
        self.tabs.addTab(self.scanner_tab, "Scanner")
        self.tabs.addTab(self.paper_bots_tab, "Paper Runs")
        self.tabs.addTab(self.score_tab, "Score")
        self.tabs.addTab(self.live_unlock_tab, "Live Gate")
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
        self._refresh_all_views()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_status_only)
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
        self._controller.run_preset(profile, profile.default_preset)
        if profile.start_minimized and self._tray.isVisible():
            self.hide()

    def closeEvent(self, event: QCloseEvent) -> None:
        status = self._controller.status(self._current_profile())
        if status.state == "running" and self._tray.isVisible():
            result = QMessageBox.question(
                self,
                "Recorder still running",
                "The recorder is still running. Keep Superior alive in the tray?",
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
        self.home_tab.open_setup_button.clicked.connect(self._open_setup_wizard)
        self.home_tab.view_docs_button.clicked.connect(lambda: self._open_local(_project_root() / "README.md"))
        self.home_tab.start_button.clicked.connect(self._start_default_preset)
        self.home_tab.stop_button.clicked.connect(self._stop_run)
        self.home_tab.replay_button.clicked.connect(lambda: self._run_preset("replay-latest"))
        self.home_tab.verify_button.clicked.connect(lambda: self._run_preset("verify-latest"))
        self.home_tab.scan_button.clicked.connect(self._refresh_scanner)
        self.home_tab.paper_button.clicked.connect(self._paper_top_opportunity)

        self.loadout_tab.save_button.clicked.connect(self._save_loadout)
        self.loadout_tab.refresh_button.clicked.connect(self._refresh_all_views)

        self.learn_tab.ask_button.clicked.connect(self._ask_coach)

        self.scanner_tab.refresh_button.clicked.connect(self._refresh_scanner)
        self.scanner_tab.paper_button.clicked.connect(self._paper_selected_opportunity)
        self.scanner_tab.live_preview_button.clicked.connect(self._preview_live_lock)
        self.scanner_tab.candidate_list.currentItemChanged.connect(self._on_candidate_changed)

        self.paper_bots_tab.run_top_button.clicked.connect(self._paper_top_opportunity)
        self.paper_bots_tab.refresh_button.clicked.connect(self._refresh_portfolio_views)

        self.live_unlock_tab.save_button.clicked.connect(self._save_unlock_preferences)
        self.live_unlock_tab.refresh_button.clicked.connect(self._refresh_all_views)
        self.live_unlock_tab.shadow_button.clicked.connect(lambda: self._set_live_mode("shadow"))
        self.live_unlock_tab.micro_button.clicked.connect(lambda: self._set_live_mode("micro"))
        self.live_unlock_tab.experimental_button.clicked.connect(lambda: self._set_live_mode("experimental"))
        self.live_unlock_tab.reset_button.clicked.connect(lambda: self._set_live_mode("locked"))

        self.lab_tab.save_button.clicked.connect(self._save_lab_setting)

        self.diagnostics_tab.refresh_button.clicked.connect(self._refresh_all_views)
        self.diagnostics_tab.export_button.clicked.connect(self._export_diagnostics)

        self.about_tab.source_button.clicked.connect(lambda: self._open_local(_project_root()))
        self.about_tab.readme_button.clicked.connect(lambda: self._open_local(_project_root() / "README.md"))
        self.about_tab.risk_button.clicked.connect(lambda: self._open_local(_project_root() / "docs" / "risk-model.md"))
        self.about_tab.live_button.clicked.connect(
            lambda: self._open_local(_project_root() / "docs" / "live-trading-limitations.md")
        )
        self.about_tab.privacy_button.clicked.connect(
            lambda: self._open_local(_project_root() / "docs" / "privacy-and-secrets.md")
        )
        self.about_tab.testing_button.clicked.connect(lambda: self._open_local(_project_root() / "docs" / "testing.md"))
        self.about_tab.contrib_button.clicked.connect(
            lambda: self._open_local(_project_root() / "docs" / "strategy-contributor-guide.md")
        )
        self.about_tab.issues_button.clicked.connect(
            lambda: self._open_url("https://github.com/Zwin-ux/arbitrage/issues")
        )

    def _setup_tray(self, *, show_tray_icon: bool) -> None:
        icon = self.windowIcon()
        if icon.isNull():
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self._tray = QSystemTrayIcon(icon, self)
        tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_from_tray)
        start_action = QAction("Start recorder", self)
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

    def _refresh_status_only(self) -> None:
        profile = self._current_profile()
        status = self._controller.status(profile)
        connections = self._venue_connections(profile)
        credential_statuses = self._credential_statuses(profile)
        score_snapshot = self._score_service.snapshot(profile)
        checklist = (
            self._unlock_service.checklist(
                profile,
                venue_connections=connections,
                engine_status=status,
                credential_statuses=credential_statuses,
            )
            if profile is not None
            else None
        )
        capability_states = (
            self._capability_service.states(
                profile=profile,
                engine_status=status,
                connections=connections,
                score_snapshot=score_snapshot,
                checklist=checklist,
            )
            if profile is not None and checklist is not None
            else []
        )
        live_status = (
            self._experimental_live_service.status(
                profile,
                score_snapshot=score_snapshot,
                engine_status=status,
                venue_connections=connections,
                credential_statuses=credential_statuses,
                checklist=checklist,
            )
            if profile is not None and checklist is not None
            else None
        )
        self.home_tab.update_view(
            profile=profile,
            status=status,
            connections=connections,
            checklist=checklist,
            score_snapshot=score_snapshot,
            capability_states=capability_states,
        )
        self.live_unlock_tab.update_view(profile, checklist, live_status)
        self.diagnostics_tab.text.setPlainText(
            self._diagnostics.diagnostics_text(
                profile=profile,
                status=status,
                credential_statuses=credential_statuses,
            )
        )
        if profile is not None:
            self.loadout_tab.update_view(
                profile,
                loadout=self._loadout_service.build_loadout(profile),
                connector_states=self._loadout_service.connector_states(profile, connections, credential_statuses),
                module_states=self._loadout_service.module_states(profile, self._opportunity_engine.strategy_modules()),
            )
        else:
            self.loadout_tab.update_view(
                None,
                loadout=None,
                connector_states=[],
                module_states=[],
            )
        if self._previous_state == "running" and status.state in {"completed", "failed"}:
            self._tray.showMessage("Superior", status.last_message, self._tray.icon(), 5000)
        self._previous_state = status.state

    def _refresh_all_views(self) -> None:
        self._refresh_status_only()
        self._refresh_scanner()
        self._refresh_portfolio_views()
        profile = self._current_profile()
        self.lab_tab.update_view(profile, self._opportunity_engine.strategy_modules())
        self._sync_lab_tab_visibility(profile)

    def _refresh_scanner(self) -> None:
        profile = self._current_profile()
        self._latest_candidates = self._opportunity_engine.scan(profile) if profile is not None else []
        self.scanner_tab.update_candidates(self._latest_candidates)
        self.scanner_tab.set_details(self._selected_candidate())

    def _refresh_portfolio_views(self) -> None:
        profile = self._current_profile()
        if profile is None:
            self.paper_bots_tab.update_runs([])
            self.paper_bots_tab.set_last_run(None)
            self.score_tab.update_summary(ScoreSnapshot(), [], [])
            return
        runs = self._paper_store.list_runs(profile)
        score_snapshot = self._score_service.snapshot(profile)
        ledger_entries = self._score_service.ledger(profile, limit=10)
        last_run = self._last_paper_run or (runs[-1] if runs else None)
        self.paper_bots_tab.update_runs(runs)
        self.paper_bots_tab.set_last_run(last_run)
        self.score_tab.update_summary(score_snapshot, ledger_entries, runs)

    def _venue_connections(self, profile: AppProfile | None) -> list[VenueConnection]:
        if profile is None:
            return []
        return [adapter.connection(profile, self._credential_vault) for adapter in self._venue_adapters]

    def _credential_statuses(self, profile: AppProfile | None) -> list[CredentialStatus]:
        if profile is None:
            return []
        return self._credential_vault.statuses_for_profile(profile.id)

    def _experimental_live_status(self, profile: AppProfile) -> ExperimentalLiveStatus:
        status = self._controller.status(profile)
        connections = self._venue_connections(profile)
        credential_statuses = self._credential_statuses(profile)
        checklist = self._unlock_service.checklist(
            profile,
            venue_connections=connections,
            engine_status=status,
            credential_statuses=credential_statuses,
        )
        return self._experimental_live_service.status(
            profile,
            score_snapshot=self._score_service.snapshot(profile),
            engine_status=status,
            venue_connections=connections,
            credential_statuses=credential_statuses,
            checklist=checklist,
        )

    def _selected_candidate(self) -> OpportunityCandidate | None:
        current_item = self.scanner_tab.candidate_list.currentItem()
        if current_item is None:
            return self._latest_candidates[0] if self._latest_candidates else None
        candidate_id = current_item.data(32)
        for candidate in self._latest_candidates:
            if candidate.id == candidate_id:
                return candidate
        return None

    def _on_candidate_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if current is None:
            self.scanner_tab.set_details(self._latest_candidates[0] if self._latest_candidates else None)
            return
        self.scanner_tab.set_details(self._selected_candidate())

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
            self._refresh_all_views()
            self.statusBar().showMessage("Profile created.", 4000)

    def _on_profile_changed(self) -> None:
        self._refresh_all_views()

    def _start_default_preset(self) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Create a profile", "Create a profile before starting the recorder.")
            return
        self._run_preset(profile.default_preset)

    def _save_loadout(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        equipped_connectors: list[str] = []
        enabled_venues: list[str] = []
        if self.loadout_tab.polymarket_checkbox.isChecked():
            equipped_connectors.append("polymarket")
            enabled_venues.append("Polymarket")
        if self.loadout_tab.kalshi_checkbox.isChecked():
            equipped_connectors.append("kalshi")
            enabled_venues.append("Kalshi")
        if self.loadout_tab.coach_checkbox.isChecked():
            equipped_connectors.append("coach")
        if not enabled_venues:
            QMessageBox.warning(self, "Equip a connector", "Equip at least one venue connector before saving the loadout.")
            return
        equipped_modules: list[str] = []
        if self.loadout_tab.internal_binary_checkbox.isChecked():
            equipped_modules.append("internal-binary")
        if self.loadout_tab.cross_venue_checkbox.isChecked():
            equipped_modules.append("cross-venue-complement")
        if self.loadout_tab.neg_risk_checkbox.isChecked():
            equipped_modules.append("negative-risk-basket")
        if self.loadout_tab.maker_lab_checkbox.isChecked():
            equipped_modules.append("maker-rebate-lab")
        if not equipped_modules:
            QMessageBox.warning(self, "Equip a module", "Equip at least one strategy module before saving the loadout.")
            return
        lab_enabled = any(module in {"negative-risk-basket", "maker-rebate-lab"} for module in equipped_modules)
        updated = profile.model_copy(
            update={
                "enabled_venues": enabled_venues,
                "equipped_connectors": equipped_connectors,
                "equipped_modules": equipped_modules,
                "ai_coach_enabled": "coach" in equipped_connectors,
                "lab_enabled": lab_enabled or profile.lab_enabled,
                "default_strategy_tier": "lab" if lab_enabled else "core",
                "live_target_venue": "Polymarket" if "polymarket" in equipped_connectors else enabled_venues[0],
                "live_allowed_strategy_ids": [
                    module_id
                    for module_id in equipped_modules
                    if module_id in {"internal-binary", "cross-venue-complement"}
                ]
                or profile.live_allowed_strategy_ids,
            }
        )
        if "polymarket" in equipped_connectors and not updated.first_run_completed:
            updated.primary_mission = "Record your first local sample, inspect one route, and paper it."
        self._profile_store.save_profile(updated)
        self._refresh_profiles(updated.id)
        self._refresh_all_views()
        self.statusBar().showMessage("Loadout saved.", 4000)

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
        self._refresh_status_only()

    def _stop_run(self) -> None:
        self._controller.stop()
        self.statusBar().showMessage("Stop requested.", 4000)

    def _paper_top_opportunity(self) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Choose a profile", "Create or choose a profile before running a paper bot.")
            return
        candidates = [candidate for candidate in self._latest_candidates if candidate.net_edge_bps > 0]
        if not candidates:
            self._refresh_scanner()
            candidates = [candidate for candidate in self._latest_candidates if candidate.net_edge_bps > 0]
        if not candidates:
            QMessageBox.information(self, "No paper candidate", "No current candidate clears the net-edge threshold.")
            return
        self._execute_paper_candidate(profile, candidates[0])

    def _paper_selected_opportunity(self) -> None:
        profile = self._current_profile()
        candidate = self._selected_candidate()
        if profile is None or candidate is None:
            QMessageBox.information(self, "Choose a candidate", "Pick a scanner result before paper-testing it.")
            return
        self._execute_paper_candidate(profile, candidate)

    def _execute_paper_candidate(self, profile: AppProfile, candidate: OpportunityCandidate) -> None:
        self._last_paper_run = self._paper_execution_engine.paper_trade(profile, candidate)
        active_profile = profile
        if not profile.first_run_completed:
            active_profile = profile.model_copy(
                update={
                    "first_run_completed": True,
                    "primary_mission": "Check Score, then repeat the record, scan, and paper loop with discipline.",
                }
            )
            self._profile_store.save_profile(active_profile)
            self._refresh_profiles(active_profile.id)
        live_status = self._experimental_live_status(active_profile)
        if live_status.paper_gate_passed and not active_profile.paper_gate_passed:
            active_profile = active_profile.model_copy(
                update={
                    "paper_gate_passed": True,
                    "paper_gate_passed_at": datetime.now(timezone.utc),
                    "primary_mission": "Paper gate passed. Keep score honest, then decide whether to stage shadow live.",
                }
            )
            self._profile_store.save_profile(active_profile)
            self._refresh_profiles(active_profile.id)
        self._refresh_portfolio_views()
        self._refresh_status_only()
        self.statusBar().showMessage("Paper route recorded.", 4000)

    def _preview_live_lock(self) -> None:
        profile = self._current_profile()
        candidate = self._selected_candidate()
        if profile is None or candidate is None:
            QMessageBox.information(self, "Choose a candidate", "Pick a scanner result first.")
            return
        live_status = self._experimental_live_status(profile)
        QMessageBox.information(
            self,
            "Experimental live preview",
            self._live_execution_engine.preview(profile, candidate, live_status),
        )

    def _ask_coach(self) -> None:
        profile = self._current_profile()
        question = self.learn_tab.prompt_edit.toPlainText().strip()
        if not question:
            QMessageBox.information(self, "Ask something", "Enter a question for the coach first.")
            return
        status = self._controller.status(profile)
        checklist = (
            self._unlock_service.checklist(
                profile,
                venue_connections=self._venue_connections(profile),
                engine_status=status,
                credential_statuses=self._credential_statuses(profile),
            )
            if profile is not None
            else None
        )
        summary = self._paper_store.summary(profile) if profile is not None else None
        remote_configured = (
            profile is not None and self._credential_vault.status(profile.id, "coach").status == "validated"
        )
        session = self._assistant_service.answer(
            question=question,
            profile=profile,
            candidates=self._latest_candidates,
            checklist=checklist,
            portfolio_summary=summary,
            remote_configured=remote_configured,
        )
        self.learn_tab.set_response(session)

    def _save_unlock_preferences(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        updated = profile.model_copy(
            update={
                "live_rules_accepted": self.live_unlock_tab.live_rules_checkbox.isChecked(),
                "risk_limits_acknowledged": self.live_unlock_tab.risk_ack_checkbox.isChecked(),
            }
        )
        self._profile_store.save_profile(updated)
        self._refresh_profiles(updated.id)
        self._refresh_status_only()
        self.statusBar().showMessage("Unlock preferences saved.", 4000)

    def _set_live_mode(self, target_mode: str) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        self._save_unlock_preferences()
        updated_profile = self._current_profile()
        assert updated_profile is not None
        live_status = self._experimental_live_status(updated_profile)
        if target_mode != "locked" and not self._experimental_live_service.can_promote(live_status, target_mode):
            QMessageBox.warning(
                self,
                "Experimental live still blocked",
                f"{target_mode.title()} mode is not ready yet. Check the checklist and warnings first.",
            )
            self._refresh_status_only()
            return
        promoted = self._experimental_live_service.promote(
            updated_profile,
            status=live_status,
            target_mode=target_mode,
        )
        if target_mode == "shadow" and not promoted.primary_mission.startswith("Review shadow-live"):
            promoted = promoted.model_copy(
                update={
                    "primary_mission": "Review shadow-live plans before arming any real-money path.",
                }
            )
        self._profile_store.save_profile(promoted)
        self._refresh_profiles(promoted.id)
        self._refresh_status_only()
        mode_message = {
            "locked": "Profile returned to the fully locked paper-first posture.",
            "shadow": "Shadow live is armed. Superior will keep this in dry-run mode only.",
            "micro": "Micro-live is armed. Keep the caps tiny and the venue scope narrow.",
            "experimental": "Experimental live is armed. This stays deterministic and high-friction on purpose.",
        }
        QMessageBox.information(self, "Experimental live", mode_message[target_mode])

    def _save_lab_setting(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        updated = profile.model_copy(
            update={
                "lab_enabled": self.lab_tab.enable_checkbox.isChecked(),
                "default_strategy_tier": "lab" if self.lab_tab.enable_checkbox.isChecked() else "core",
            }
        )
        self._profile_store.save_profile(updated)
        self._refresh_profiles(updated.id)
        self._refresh_all_views()
        self.statusBar().showMessage("Lab setting saved.", 4000)

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
        credential_statuses = self._credential_statuses(profile)
        self._diagnostics.export_bundle(
            profile=profile,
            status=status,
            credential_statuses=credential_statuses,
            output_path=Path(filename),
        )
        self.statusBar().showMessage("Diagnostics bundle exported.", 4000)

    def _sync_lab_tab_visibility(self, profile: AppProfile | None) -> None:
        tab_index = self.tabs.indexOf(self.lab_tab)
        should_show = profile is not None and profile.lab_enabled
        if should_show and tab_index < 0:
            self.tabs.insertTab(self.tabs.count() - 2, self.lab_tab, "Lab")
        if not should_show and tab_index >= 0:
            self.tabs.removeTab(tab_index)

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
