from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import (
    QAction,
    QColor,
    QCloseEvent,
    QDesktopServices,
    QFont,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
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
    QVBoxLayout,
    QWidget,
)

from market_data_recorder.models import ArbitrageOpportunity
from . import __version__
from .app_types import (
    AgentDraft,
    DraftAction,
    AgentSkillId,
    AppProfile,
    AssistantSession,
    BenchmarkAudit,
    BenchmarkInterval,
    BenchmarkInstrumentType,
    BotConfig,
    BotRecipe,
    BotRegistryEntry,
    BotSlot,
    CapabilityState,
    ConnectorLoadout,
    CredentialStatus,
    EngineStatus,
    ExperimentalLiveStatus,
    LiveUnlockChecklist,
    ModelProviderConfig,
    OpportunityCandidate,
    PaperBotEvent,
    PaperBotSession,
    PaperRunResult,
    PortfolioSnapshot,
    PortfolioSummary,
    ProviderHealth,
    ScoreLedgerEntry,
    ScoreSnapshot,
    StrategyModule,
    UnlockState,
    VenueConnection,
)
from .benchmark_lab import BenchmarkAuditService, BenchmarkLinkService, BenchmarkStore, resolve_benchmark_api_key
from .bot_services import (
    ArbitrageService,
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
from .bot_recipes import BotRecipeStore
from .controller import EngineController
from .credentials import CredentialVault
from .diagnostics import DiagnosticsService
from .paths import AppPaths
from .profiles import ProfileStore
from .score_attack import (
    BotRegistryService,
    DecisionTraceFormatter,
    BotConfigService,
    PaperSimulationEngine,
    PortfolioEngine,
    ProgressionService,
    SessionEventStore,
    UnlockTrackService,
)
from .startup import StartupManager
from .ui.hangar import HomeTab as HangarHomeTab
from .ui.scanner import ArcadeScannerWidget
from .ui.shell import DesktopShell
from .wizard import SetupWizard


_log = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class _LegacySignalBadge(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("signalBadge", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        self.title_label = QLabel(label.upper())
        self.title_label.setProperty("signalTitle", True)
        self.value_label = QLabel("OFFLINE")
        self.value_label.setProperty("signalValue", True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.set_state("offline", tone="locked")

    def set_state(self, value: str, *, tone: str) -> None:
        self.value_label.setText(value.upper())
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        _repolish(self)
        _repolish(self.value_label)


class _LegacyStatusTile(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setProperty("statusTile", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        self.title_label = QLabel(title.upper())
        self.title_label.setProperty("statusTitle", True)
        self.value_label = QLabel("IDLE")
        self.value_label.setProperty("statusValue", True)
        self.detail_label = QLabel("")
        self.detail_label.setWordWrap(True)
        self.detail_label.setProperty("statusDetail", True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)
        self.set_state("idle", "Waiting for input.", tone="idle")

    def set_state(self, value: str, detail: str, *, tone: str) -> None:
        self.value_label.setText(value.upper())
        self.detail_label.setText(detail)
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        _repolish(self)
        _repolish(self.value_label)


class _LegacyArcadeScannerWidget(QWidget):
    """Retired in favor of ui.scanner.ArcadeScannerWidget."""


class _LegacyHomeTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.safe_state_label = QLabel("System status")
        self.safe_state_label.setObjectName("heroTitle")
        self.next_step_label = QLabel("Set up a profile, keep Polymarket on, then run the recorder.")
        self.next_step_label.setWordWrap(True)
        layout.addWidget(self.safe_state_label)

        signal_row = QHBoxLayout()
        signal_row.setSpacing(8)
        self.paper_state_badge = _LegacySignalBadge("Practice mode")
        self.live_state_badge = _LegacySignalBadge("Live gate")
        self.lab_state_badge = _LegacySignalBadge("Lab")
        signal_row.addWidget(self.paper_state_badge)
        signal_row.addWidget(self.live_state_badge)
        signal_row.addWidget(self.lab_state_badge)
        signal_row.addStretch(1)
        layout.addLayout(signal_row)
        layout.addWidget(self.next_step_label)

        mission_group = QGroupBox("Mission")
        mission_group.setProperty("panelTone", "primary")
        mission_layout = QHBoxLayout(mission_group)
        mission_layout.setSpacing(16)
        self.mission_label = QLabel("Equip -> Record -> Inspect")
        self.mission_label.setObjectName("heroText")
        self.mission_label.setWordWrap(True)
        self.score_label = QLabel("Practice score: waiting")
        self.score_label.setObjectName("heroText")
        self.score_label.setWordWrap(True)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        mission_layout.addWidget(self.mission_label, 1)
        mission_layout.addWidget(self.score_label, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(mission_group)

        action_group = QGroupBox("Primary action")
        action_group.setProperty("panelTone", "normal")
        action_layout = QVBoxLayout(action_group)
        self.primary_action_hint = QLabel("Run recorder is the main action. The rest unlocks after the first sample lands.")
        self.primary_action_hint.setObjectName("heroText")
        self.primary_action_hint.setWordWrap(True)
        action_layout.addWidget(self.primary_action_hint)

        primary_action_row = QHBoxLayout()
        primary_action_row.setSpacing(10)
        self.start_button = QPushButton("Run recorder")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("buttonRole", "secondary")
        primary_action_row.addWidget(self.start_button)
        primary_action_row.addWidget(self.stop_button)
        primary_action_row.addStretch(1)
        action_layout.addLayout(primary_action_row)

        self.secondary_actions_hint = QLabel("Replay, Verify, Scan routes, and Start practice unlock after a recorder pass.")
        self.secondary_actions_hint.setWordWrap(True)
        action_layout.addWidget(self.secondary_actions_hint)

        self.secondary_actions_widget = QWidget()
        tool_action_row = QHBoxLayout(self.secondary_actions_widget)
        tool_action_row.setContentsMargins(0, 0, 0, 0)
        tool_action_row.setSpacing(8)
        self.replay_button = QPushButton("Replay")
        self.replay_button.setProperty("buttonRole", "secondary")
        self.verify_button = QPushButton("Verify")
        self.verify_button.setProperty("buttonRole", "secondary")
        self.scan_button = QPushButton("Scan routes")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Start practice")
        self.paper_button.setProperty("buttonRole", "secondary")
        for button in (self.replay_button, self.verify_button, self.scan_button, self.paper_button):
            tool_action_row.addWidget(button)
        tool_action_row.addStretch(1)
        self.secondary_actions_widget.hide()
        action_layout.addWidget(self.secondary_actions_widget)
        layout.addWidget(action_group)

        console_group = QGroupBox("System console")
        console_group.setProperty("panelTone", "normal")
        console_layout = QVBoxLayout(console_group)
        tile_row = QHBoxLayout()
        tile_row.setSpacing(8)
        self.recorder_tile = _LegacyStatusTile("Recorder")
        self.scanner_tile = _LegacyStatusTile("Scanner")
        self.route_tile = _LegacyStatusTile("Route")
        tile_row.addWidget(self.recorder_tile)
        tile_row.addWidget(self.scanner_tile)
        tile_row.addWidget(self.route_tile)
        console_layout.addLayout(tile_row)
        self.system_log = QPlainTextEdit()
        self.system_log.setReadOnly(True)
        self.system_log.setProperty("consoleRole", "system")
        self.system_log.setMaximumHeight(120)
        console_layout.addWidget(self.system_log)
        layout.addWidget(console_group)

        progress_group = QGroupBox("Progress")
        progress_group.setProperty("panelTone", "subtle")
        progress_layout = QVBoxLayout(progress_group)
        self.setup_progress_label = QLabel("First run")
        self.setup_progress_label.setObjectName("heroText")
        self.setup_progress_label.setWordWrap(True)
        self.setup_steps_label = QLabel()
        self.setup_steps_label.setWordWrap(True)
        self.setup_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.loop_label = QLabel("Milestones: 0/4 complete")
        self.loop_label.setObjectName("heroText")
        self.loop_label.setWordWrap(True)
        self.loop_steps_label = QLabel()
        self.loop_steps_label.setWordWrap(True)
        self.loop_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        progress_actions = QHBoxLayout()
        self.open_setup_button = QPushButton("Set up profile")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("Read setup guide")
        self.view_docs_button.setProperty("buttonRole", "secondary")
        progress_actions.addWidget(self.open_setup_button)
        progress_actions.addWidget(self.view_docs_button)
        progress_actions.addStretch(1)
        progress_divider = QFrame()
        progress_divider.setFrameShape(QFrame.Shape.HLine)
        progress_layout.addWidget(self.setup_progress_label)
        progress_layout.addWidget(self.setup_steps_label)
        progress_layout.addLayout(progress_actions)
        progress_layout.addWidget(progress_divider)
        progress_layout.addWidget(self.loop_label)
        progress_layout.addWidget(self.loop_steps_label)
        layout.addWidget(progress_group)

        telemetry_group = QGroupBox("Telemetry")
        telemetry_group.setProperty("panelTone", "ghost")
        telemetry_layout = QVBoxLayout(telemetry_group)
        self.brand_label = QLabel("Superior")
        self.profile_label = QLabel("No profile selected")
        self.goal_label = QLabel("No goal set")
        self.engine_label = QLabel("Idle")
        self.data_label = QLabel("No database yet")
        self.risk_label = QLabel("Starter")
        self.warning_label = QLabel("No warnings")
        self.warning_label.setWordWrap(True)
        self.telemetry_text = QPlainTextEdit()
        self.telemetry_text.setReadOnly(True)
        self.telemetry_text.setProperty("consoleRole", "system")
        self.telemetry_text.setMaximumHeight(176)
        telemetry_layout.addWidget(self.telemetry_text)
        layout.addWidget(telemetry_group)
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
        candidate_count: int = 0,
    ) -> None:
        if profile is None:
            self.brand_label.setText("Superior")
            self.profile_label.setText("No profile selected")
            self.goal_label.setText("Create your first setup")
            self.engine_label.setText(status.state.title())
            self.data_label.setText("No database yet")
            self.risk_label.setText("No risk policy")
            self.warning_label.setText("No warnings")
            self.safe_state_label.setText("System status")
            self.paper_state_badge.set_state("active", tone="active")
            self.live_state_badge.set_state("locked", tone="locked")
            self.lab_state_badge.set_state("offline", tone="idle")
            self.next_step_label.setText("Set up a profile, keep Polymarket on, then run the recorder.")
            self.mission_label.setText("Equip -> Record -> Inspect")
            self.score_label.setText("Practice score: waiting")
            self.primary_action_hint.setText("Set up a profile first. Run recorder becomes available after setup is saved.")
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Set up your first profile."),
                        ("WAIT", "Keep Polymarket and one play style on."),
                        ("WAIT", "Run the recorder after setup is saved."),
                    ]
                )
            )
            self.loop_label.setText("Milestones: 0/4 complete")
            self.loop_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Finish the starter setup."),
                        ("WAIT", "Record a local sample."),
                        ("WAIT", "Refresh Scan."),
            ("WAIT", "Finish one practice run."),
                    ]
                )
            )
            self.open_setup_button.setText("Set up profile")
            self.secondary_actions_hint.setText(
                "Replay, Verify, Scan routes, and Start practice unlock after the first recorder pass."
            )
            self._set_telemetry(
                connection_lines=["No active venue connections."],
                system_lines=[
                    "Recorder: blocked until setup is saved.",
                    "Scanner: waiting for recorder data.",
                    "Practice: waiting for a viable route.",
                ],
            )
            self.recorder_tile.set_state("blocked", "Finish setup before recorder boot is available.", tone="locked")
            self.scanner_tile.set_state("waiting", "Scanner unlocks after local book capture starts.", tone="idle")
            self.route_tile.set_state("empty", "No route can be priced until scanner data exists.", tone="idle")
            self.system_log.setPlainText(
                "\n".join(
                    [
                        "[SYS] No active profile loaded.",
                        "[REC] Recorder offline until a Polymarket setup exists.",
                        "[SCAN] Waiting for first local book sample.",
                        "[ROUTE] Practice stays dark until the first clean scan lands.",
                    ]
                )
            )
            self._set_action_button(
                self.start_button,
                enabled=False,
                label="Run recorder",
                reason="Set up a profile first.",
            )
            self._set_action_button(
                self.stop_button,
                enabled=False,
                label="Stop",
                reason="Recorder is not running.",
            )
            self._set_action_button(
                self.replay_button,
                enabled=False,
                label="Replay",
                reason="No local data yet.",
            )
            self._set_action_button(
                self.verify_button,
                enabled=False,
                label="Verify",
                reason="No local data yet.",
            )
            self._set_action_button(
                self.scan_button,
                enabled=False,
                label="Scan routes",
                reason="Recorder data must land first.",
            )
            self._set_action_button(
                self.paper_button,
                enabled=False,
                label="Start practice",
                reason="Scanner needs a route first.",
            )
            self._set_secondary_tools_visibility(
                False,
                "Replay, Verify, Scan routes, and Start practice unlock after the first recorder pass.",
            )
            return
        has_data = status.summary is not None and (
            status.summary.raw_messages > 0 or status.summary.book_snapshots > 0
        )
        is_running = status.state == "running"
        self.safe_state_label.setText("System status")
        self.paper_state_badge.set_state("active", tone="active")
        self.live_state_badge.set_state(
            "locked" if profile.live_mode == "locked" else profile.live_mode,
            tone="locked" if profile.live_mode == "locked" else "warning",
        )
        self.lab_state_badge.set_state("online" if profile.lab_enabled else "offline", tone="warning" if profile.lab_enabled else "idle")
        scanner_ready = any(state.capability_id == "scanner" and state.ready for state in capability_states)
        loadout_ready = "polymarket" in profile.equipped_connectors and bool(profile.equipped_modules)
        score_ready = score_snapshot.total_runs > 0
        tools_visible = has_data or status.state in {"completed", "failed"}
        if not loadout_ready:
            self.next_step_label.setText("Save setup with Polymarket and one play style.")
            self.primary_action_hint.setText("Setup is incomplete. Save it before trying to run the recorder.")
        elif is_running:
            self.next_step_label.setText("Recorder is running. Let one clean sample finish before scanning.")
            self.primary_action_hint.setText("Recorder is active. Stop only if you need to abort this pass.")
        elif not has_data:
            self.next_step_label.setText("Run recorder so Superior has local books to inspect.")
            self.primary_action_hint.setText("Run recorder first. Secondary tools stay hidden until local data exists.")
        elif not score_ready:
            self.next_step_label.setText("Scan one route and run practice to light up the score board.")
            self.primary_action_hint.setText("Recorder is ready. Use the unlocked tools below to inspect and test routes.")
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            self.next_step_label.setText(
                "Keep scoring in practice mode or stage shadow live if you want a dry run."
            )
            self.primary_action_hint.setText("Recorder is stable. Use the unlocked tools to keep practice performance honest.")
        elif checklist is not None and checklist.outstanding:
            self.next_step_label.setText("Keep the paper loop healthy. Live-gate items are optional.")
            self.primary_action_hint.setText("Recorder is stable. Use replay, verify, and scan to inspect weak spots.")
        else:
            self.next_step_label.setText("Keep recorder data healthy and grow practice score with discipline.")
            self.primary_action_hint.setText("Recorder is stable. Keep using the unlocked tools to inspect routes and verify data.")
        self.brand_label.setText(profile.brand_name)
        self.profile_label.setText(profile.display_name)
        self.goal_label.setText(profile.primary_goal.replace("_", " ").title())
        self.engine_label.setText(f"{status.state.title()} - {status.last_message}")
        self.risk_label.setText(profile.risk_policy_id.title())
        self.mission_label.setText(profile.primary_mission)
        if score_snapshot.total_runs:
            self.score_label.setText(
                f"Practice score ${score_snapshot.paper_realized_pnl_cents / 100:.2f} | "
                f"Runs {score_snapshot.completed_runs} | Hit rate {score_snapshot.hit_rate:.1f}%"
            )
        else:
            self.score_label.setText("Practice score: waiting")
        if status.summary is not None:
            self.data_label.setText(
                f"{status.summary.raw_messages} raw messages, {status.summary.book_snapshots} books"
            )
            self.warning_label.setText(status.summary.latest_warning or "No warnings")
        else:
            self.data_label.setText("No database yet")
            self.warning_label.setText("No warnings")
        self._set_telemetry(
            connection_lines=[
                f"{connection.venue_label}: {connection.mode.upper()} - {connection.message}"
                for connection in connections
            ]
            or ["No active venue connections."],
            system_lines=[
                f"{state.label}: {'READY' if state.ready else 'BLOCKED'} - {state.message}"
                for state in capability_states
            ]
            or ["No system telemetry yet."],
        )
        step_specs = [
            (
                "Finish setup",
                loadout_ready,
                "Polymarket and one play style are ready."
                if loadout_ready
                else "Turn on Polymarket and one play style.",
            ),
            (
                "Record local sample",
                has_data,
                "Local recorder data is ready for the scanner."
                if has_data
                else "Run recorder and wait for books.",
            ),
            (
                "Inspect scanner route",
                scanner_ready,
                "Scanner explanations are ready."
                if scanner_ready
                else "Recorder data has to land first.",
            ),
            (
                "Earn practice score",
                score_ready,
                "Practice score is live."
                if score_ready
                else "Run one practice run.",
            ),
        ]
        completed_steps = sum(1 for _label, ready, _message in step_specs if ready)
        self.loop_label.setText(f"Milestones: {completed_steps}/{len(step_specs)} complete")
        first_incomplete_seen = False
        loop_lines: list[tuple[str, str]] = []
        for label, ready, message in step_specs:
            if ready:
                marker = "DONE"
            elif not first_incomplete_seen:
                marker = "NEXT"
                first_incomplete_seen = True
            else:
                marker = "WAIT"
            loop_lines.append((marker, f"{label} - {message}"))
        self.loop_steps_label.setText(self._format_checklist(loop_lines))
        self.open_setup_button.setText("Edit profile")
        if profile.live_unlocked:
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
            ("DONE", "Recorder, scanner, and practice score are in place."),
                        ("NEXT", "Revisit setup only when changing scope."),
                        ("WAIT", "Keep live execution optional."),
                    ]
                )
            )
        elif is_running:
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Recorder is running."),
                        ("NEXT", "Wait for message and book counts."),
                        ("WAIT", "Refresh scan when the pass completes."),
                        ("WAIT", "Run practice on the top route after scan."),
                    ]
                )
            )
        elif not has_data:
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Run recorder."),
                        ("WAIT", "Wait for message and book counts."),
                        ("WAIT", "Refresh Scan, then start one practice run."),
                    ]
                )
            )
        elif checklist is not None and checklist.outstanding:
            outstanding = self._format_checklist(
                [
                    ("BLOCKED", f"{check.label}: {check.message}")
                    for check in checklist.outstanding[:3]
                ]
            )
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                f"{outstanding}\n[ ] Keep using practice mode while these stay open."
            )
        elif profile.live_mode == "shadow":
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Shadow live is staged with real orders still off."),
                        ("NEXT", "Keep scanning and practicing so score stays honest."),
                        ("WAIT", "Use Scanner preview before thinking about micro-live."),
                        ("WAIT", "Only arm micro-live after diagnostics stay clean."),
                    ]
                )
            )
        elif profile.live_mode in {"micro", "experimental"}:
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Experimental live is armed."),
                        ("NEXT", "Use Scanner preview before each candidate."),
                        ("WAIT", "Keep setup scope narrow."),
                        ("WAIT", "Reset to locked if diagnostics degrade."),
                    ]
                )
            )
        else:
            self.setup_progress_label.setText("First run")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Local recorder data is ready."),
                        ("NEXT", "Refresh Scan for the newest candidates."),
                        ("WAIT", "Run practice on the top opportunity."),
                        ("WAIT", "Edit setup only when scope changes."),
                    ]
                )
            )
        recorder_detail = (
            f"{status.summary.raw_messages} messages / {status.summary.book_snapshots} books captured."
            if status.summary is not None
            else "No local market file yet."
        )
        if is_running:
            self.recorder_tile.set_state("capturing", recorder_detail, tone="active")
        elif has_data:
            self.recorder_tile.set_state("ready", recorder_detail, tone="active")
        elif loadout_ready:
            self.recorder_tile.set_state("idle", "Setup is ready. Run the recorder for a first pass.", tone="warning")
        else:
            self.recorder_tile.set_state("blocked", "Polymarket and a strategy module are required first.", tone="locked")
        if scanner_ready and candidate_count > 0:
            self.scanner_tile.set_state("routes found", f"{candidate_count} candidate routes are cached locally.", tone="active")
        elif scanner_ready:
            self.scanner_tile.set_state("ready", "Scanner is armed and waiting for a refresh.", tone="warning")
        elif has_data:
            self.scanner_tile.set_state("standby", "Local books exist, but Scan still needs a refresh.", tone="warning")
        else:
            self.scanner_tile.set_state("waiting", "Recorder data has to land before scanner routes exist.", tone="locked")
        if score_ready:
            self.route_tile.set_state("practice scored", f"{score_snapshot.completed_runs} practice runs have landed in the score ledger.", tone="active")
        elif candidate_count > 0:
            self.route_tile.set_state("route ready", "A candidate is available. Start practice to light the score board.", tone="warning")
        else:
            self.route_tile.set_state("empty", "No top route is staged yet.", tone="locked")
        self.system_log.setPlainText(
            "\n".join(
                [
                    f"[SYS] Profile online: {profile.display_name}",
                    f"[REC] {self.recorder_tile.value_label.text()} :: {self.recorder_tile.detail_label.text()}",
                    f"[SCAN] {self.scanner_tile.value_label.text()} :: {self.scanner_tile.detail_label.text()}",
                    f"[ROUTE] {self.route_tile.value_label.text()} :: {self.route_tile.detail_label.text()}",
                    f"[SAFE] PRACTICE=ACTIVE | LIVE={profile.live_mode.upper()} | LAB={'ON' if profile.lab_enabled else 'OFF'}",
                ]
            )
        )
        self._set_action_button(
            self.start_button,
            enabled=not is_running,
            label="Run recorder",
            reason="Recorder already running." if is_running else "Recorder ready.",
        )
        self._set_action_button(
            self.stop_button,
            enabled=is_running,
            label="Stop",
            reason="Recorder is not running." if not is_running else "Stop the current recorder pass.",
        )
        self._set_action_button(
            self.replay_button,
            enabled=tools_visible and not is_running,
            label="Replay",
            reason="Need one completed recorder pass before replay." if not tools_visible else "Recorder pass must finish first.",
        )
        self._set_action_button(
            self.verify_button,
            enabled=tools_visible and not is_running,
            label="Verify",
            reason="Need one completed recorder pass before verify." if not tools_visible else "Recorder pass must finish first.",
        )
        self._set_action_button(
            self.scan_button,
            enabled=has_data,
            label="Scan routes",
            reason="Recorder data must land before the scanner becomes useful.",
        )
        self._set_action_button(
            self.paper_button,
            enabled=candidate_count > 0,
            label="Start practice",
            reason="Refresh scan first so a viable route exists.",
        )
        self._set_secondary_tools_visibility(
            tools_visible,
            "Replay and Verify are available. Scan routes and Start practice still need usable local data."
            if tools_visible and not has_data
            else (
                "Replay, Verify, Scan routes, and Start practice are unlocked."
                if has_data
                else "Replay, Verify, Scan routes, and Start practice unlock after the first recorder pass."
            ),
        )

    @staticmethod
    def _format_checklist(items: list[tuple[str, str]]) -> str:
        prefix_map = {
            "DONE": "[x]",
            "NEXT": "[>]",
            "WAIT": "[ ]",
            "BLOCKED": "[!]",
        }
        return "\n".join(f"{prefix_map.get(prefix, '[ ]')} {message}" for prefix, message in items)

    @staticmethod
    def _set_action_button(
        button: QPushButton,
        *,
        enabled: bool,
        label: str,
        reason: str,
    ) -> None:
        button.setEnabled(enabled)
        button.setText(label)
        button.setToolTip(reason)

    def _set_secondary_tools_visibility(self, visible: bool, hint: str) -> None:
        self.secondary_actions_widget.setVisible(visible)
        self.secondary_actions_hint.setText(hint)

    def _set_telemetry(self, *, connection_lines: list[str], system_lines: list[str]) -> None:
        lines = [
            f"PROFILE     {self.profile_label.text()}",
            f"GOAL        {self.goal_label.text()}",
            f"RECORDER    {self.engine_label.text()}",
            f"DATA        {self.data_label.text()}",
            f"RISK        {self.risk_label.text()}",
            f"WARNING     {self.warning_label.text()}",
            "",
            "CONNECTORS",
            *[f"- {line}" for line in connection_lines],
            "",
            "SYSTEMS",
            *[f"- {line}" for line in system_lines],
        ]
        self.telemetry_text.setPlainText("\n".join(lines))


class LoadoutTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.header_label = QLabel("Profile setup")
        self.header_label.setObjectName("heroTitle")
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)

        loadout_row = QHBoxLayout()
        loadout_row.setSpacing(10)

        connectors_group = QGroupBox("Connectors")
        connectors_group.setProperty("panelTone", "normal")
        connectors_layout = QVBoxLayout(connectors_group)
        self.polymarket_checkbox = QCheckBox("Polymarket")
        self.kalshi_checkbox = QCheckBox("Kalshi")
        self.coach_checkbox = QCheckBox("Copilot link")
        for checkbox in (self.polymarket_checkbox, self.kalshi_checkbox, self.coach_checkbox):
            connectors_layout.addWidget(checkbox)
        loadout_row.addWidget(connectors_group, 0, Qt.AlignmentFlag.AlignTop)

        modules_group = QGroupBox("Play styles")
        modules_group.setProperty("panelTone", "subtle")
        modules_layout = QVBoxLayout(modules_group)
        self.internal_binary_checkbox = QCheckBox("Internal binary")
        self.cross_venue_checkbox = QCheckBox("Cross-venue")
        self.neg_risk_checkbox = QCheckBox("Neg risk lab")
        self.maker_lab_checkbox = QCheckBox("Maker lab")
        for checkbox in (
            self.internal_binary_checkbox,
            self.cross_venue_checkbox,
            self.neg_risk_checkbox,
            self.maker_lab_checkbox,
        ):
            modules_layout.addWidget(checkbox)
        loadout_row.addWidget(modules_group, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(loadout_row)

        action_row = QHBoxLayout()
        self.save_button = QPushButton("Save setup")
        self.refresh_button = QPushButton("Refresh view")
        self.refresh_button.setProperty("buttonRole", "secondary")
        self.copilot_button = QPushButton("Ask Copilot for a starter bot")
        self.copilot_button.setProperty("buttonRole", "secondary")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.refresh_button)
        action_row.addWidget(self.copilot_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.state_text = QPlainTextEdit()
        self.state_text.setReadOnly(True)
        self.state_text.setProperty("consoleRole", "system")
        self.state_text.setMaximumHeight(132)
        layout.addWidget(self.state_text)

        lower_row = QHBoxLayout()
        lower_row.setSpacing(10)

        bot_bay_group = QGroupBox("Bot slots")
        bot_bay_group.setProperty("panelTone", "primary")
        bot_bay_layout = QVBoxLayout(bot_bay_group)
        self.bot_bay_text = QPlainTextEdit()
        self.bot_bay_text.setReadOnly(True)
        self.bot_bay_text.setProperty("consoleRole", "system")
        self.bot_bay_text.setMaximumHeight(170)
        bot_bay_layout.addWidget(self.bot_bay_text)
        lower_row.addWidget(bot_bay_group, 3)

        registry_group = QGroupBox("Bot library")
        registry_group.setProperty("panelTone", "normal")
        registry_layout = QVBoxLayout(registry_group)
        fork_row = QHBoxLayout()
        self.fork_source_combo = QComboBox()
        self.fork_button = QPushButton("Fork selected bot")
        self.fork_button.setProperty("buttonRole", "secondary")
        fork_row.addWidget(self.fork_source_combo, 1)
        fork_row.addWidget(self.fork_button)
        registry_layout.addLayout(fork_row)
        self.registry_text = QPlainTextEdit()
        self.registry_text.setReadOnly(True)
        self.registry_text.setProperty("consoleRole", "system")
        self.registry_text.setMaximumHeight(170)
        registry_layout.addWidget(self.registry_text)
        lower_row.addWidget(registry_group, 3)

        unlock_group = QGroupBox("Progress gates")
        unlock_group.setProperty("panelTone", "subtle")
        unlock_layout = QVBoxLayout(unlock_group)
        self.unlock_text = QPlainTextEdit()
        self.unlock_text.setReadOnly(True)
        self.unlock_text.setProperty("consoleRole", "system")
        self.unlock_text.setMaximumHeight(170)
        unlock_layout.addWidget(self.unlock_text)
        lower_row.addWidget(unlock_group, 2)

        layout.addLayout(lower_row)
        layout.addStretch(1)

    def update_view(
        self,
        profile: AppProfile | None,
        *,
        loadout: ConnectorLoadout | None,
        connector_states: list[CapabilityState],
        module_states: list[CapabilityState],
        bot_configs: list[BotConfig],
        registry_entries: list[BotRegistryEntry],
        slot_preview: list[BotSlot],
        unlocks: list[UnlockState],
    ) -> None:
        if profile is None or loadout is None:
            self.header_label.setText("Create a profile to set up your first market feed.")
            self.state_text.setPlainText("No setup yet.")
            self.bot_bay_text.setPlainText("No starter bots yet.")
            self.registry_text.setPlainText("No bot library yet.")
            self.unlock_text.setPlainText("No progress gates yet.")
            self.fork_source_combo.clear()
            self.fork_source_combo.setEnabled(False)
            self.fork_button.setEnabled(False)
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
            self.copilot_button.setEnabled(False)
            return
        self.header_label.setText(f"{profile.display_name} setup")
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
        self.copilot_button.setEnabled(True)
        lines = [f"GOAL       {profile.primary_mission}", "", "CONNECTORS"]
        lines.extend(
            f"- {state.label}: {'EQUIPPED' if state.equipped else 'IDLE'} | {'READY' if state.ready else 'BLOCKED'}"
            f" | {state.message}"
            for state in connector_states
        )
        lines.append("")
        lines.append("MODULES")
        lines.extend(
            f"- {state.label}: {'EQUIPPED' if state.equipped else 'IDLE'} | {'READY' if state.ready else 'BLOCKED'}"
            f" | {state.message}"
            for state in module_states
        )
        self.state_text.setPlainText("\n".join(lines))
        bay_lines = ["STARTER BOTS", ""]
        if not slot_preview:
            bay_lines.append("No armed slots yet.")
        for slot in slot_preview:
            bay_lines.append(
                f"{slot.label.upper():<8} {slot.state.upper():<8} {slot.bot_label} :: {slot.detail}"
            )
        if bot_configs:
            bay_lines.extend(
                [
                    "",
                    "CONFIG GATES",
                    *[
                        f"- {config.label}: {config.strategy_family} @ {config.min_net_edge_bps}+ bps"
                        for config in bot_configs
                    ],
                ]
            )
        self.bot_bay_text.setPlainText("\n".join(bay_lines))
        registry_lines = ["BOT LIBRARY", ""]
        self.fork_source_combo.clear()
        if not registry_entries:
            registry_lines.append("No visible bot recipes yet. Turn on a play style to surface starter bots.")
        for entry in registry_entries:
            source_label = "LOCAL FORK" if entry.source_kind == "forked" else "STARTER"
            self.fork_source_combo.addItem(f"{entry.label} [{source_label.lower()}]", entry.recipe_id)
            registry_lines.extend(
                [
                    f"{entry.status.upper():<9} {entry.label}",
                    f"  SOURCE  {source_label}",
                    f"  FAMILY  {entry.family_label}",
                    f"  GATE    {entry.min_net_edge_bps}+ bps",
                    f"  STYLE   {entry.route_preference.replace('_', ' ')}",
                    f"  TARGET  ${entry.target_stake_cents / 100:.2f}",
                    f"  SLOT    {entry.slot_label}",
                    f"  NOTE    {entry.unlock_label}",
                    f"  ABOUT   {entry.description}",
                    "",
                ]
            )
        self.fork_source_combo.setEnabled(self.fork_source_combo.count() > 0)
        self.fork_button.setEnabled(self.fork_source_combo.count() > 0)
        self.registry_text.setPlainText("\n".join(registry_lines).rstrip())
        unlock_lines = ["PROGRESS GATES", ""]
        if not unlocks:
            unlock_lines.append("No unlocks loaded yet.")
        for unlock in unlocks:
            status = "ONLINE" if unlock.unlocked else "LOCKED"
            unlock_lines.append(f"{status:<7} {unlock.label}")
            unlock_lines.append(f"  {unlock.detail}")
        self.unlock_text.setPlainText("\n".join(unlock_lines))


class LearnTab(QWidget):
    def __init__(self, provider_presets: list[ModelProviderConfig] | None = None) -> None:
        super().__init__()
        self._provider_presets = provider_presets or [ModelProviderConfig()]
        self._requested_skill: AgentSkillId | None = None
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        intro_group = QGroupBox("Copilot")
        intro_layout = QVBoxLayout(intro_group)
        self.intro_label = QLabel(
            "Bring your own model if you want extra help. Copilot can explain routes, draft paper bots, and summarize runs, but it cannot trade."
        )
        self.intro_label.setWordWrap(True)
        intro_layout.addWidget(self.intro_label)
        self.status_label = QLabel("Status: local-first mode")
        self.status_label.setWordWrap(True)
        self.context_label = QLabel("Context: no active profile")
        self.context_label.setWordWrap(True)
        intro_layout.addWidget(self.status_label)
        intro_layout.addWidget(self.context_label)
        layout.addWidget(intro_group)

        provider_group = QGroupBox("Bring your own model")
        provider_layout = QFormLayout(provider_group)
        self.provider_combo = QComboBox()
        for preset in self._provider_presets:
            self.provider_combo.addItem(preset.provider_label, preset.provider_id)
        self.model_edit = QLineEdit()
        self.base_url_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.model_edit.setPlaceholderText("Model name")
        self.base_url_edit.setPlaceholderText("Provider base URL")
        self.api_key_edit.setPlaceholderText("Stored in the OS keychain only")
        provider_layout.addRow("Provider", self.provider_combo)
        provider_layout.addRow("Model", self.model_edit)
        provider_layout.addRow("Base URL", self.base_url_edit)
        provider_layout.addRow("API key", self.api_key_edit)
        provider_action_row = QHBoxLayout()
        self.test_provider_button = QPushButton("Test connection")
        self.save_provider_button = QPushButton("Save Copilot")
        self.save_provider_button.setProperty("buttonRole", "secondary")
        provider_action_row.addWidget(self.test_provider_button)
        provider_action_row.addWidget(self.save_provider_button)
        provider_action_row.addStretch(1)
        provider_layout.addRow("", self._wrap_layout(provider_action_row))
        self.provider_combo.currentIndexChanged.connect(self._apply_selected_preset)
        layout.addWidget(provider_group)

        quick_group = QGroupBox("Quick prompts")
        quick_layout = QHBoxLayout(quick_group)
        self.explain_route_button = QPushButton("Explain this route")
        self.draft_bot_button = QPushButton("Build me a safer starter bot")
        self.summarize_button = QPushButton("Summarize my last practice run")
        self.fix_loadout_button = QPushButton("Fix my setup")
        self.lock_button = QPushButton("Why is live locked?")
        for button in (
            self.explain_route_button,
            self.draft_bot_button,
            self.summarize_button,
            self.fix_loadout_button,
            self.lock_button,
        ):
            button.setProperty("buttonRole", "secondary")
            quick_layout.addWidget(button)
        quick_layout.addStretch(1)
        layout.addWidget(quick_group)

        coach_group = QGroupBox("Ask Copilot")
        coach_layout = QVBoxLayout(coach_group)
        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setPlaceholderText(
            "Explain this route.\nBuild me a safer starter bot.\nWhy is live locked?"
        )
        self.ask_button = QPushButton("Ask Copilot")
        self.response_text = QPlainTextEdit()
        self.response_text.setReadOnly(True)
        self.draft_text = QPlainTextEdit()
        self.draft_text.setReadOnly(True)
        draft_action_row = QHBoxLayout()
        self.apply_draft_button = QPushButton("Apply draft")
        self.reject_draft_button = QPushButton("Reject draft")
        self.reject_draft_button.setProperty("buttonRole", "secondary")
        draft_action_row.addWidget(self.apply_draft_button)
        draft_action_row.addWidget(self.reject_draft_button)
        draft_action_row.addStretch(1)
        coach_layout.addWidget(self.prompt_edit)
        coach_layout.addWidget(self.ask_button)
        coach_layout.addWidget(self.response_text)
        coach_layout.addWidget(self.draft_text)
        coach_layout.addLayout(draft_action_row)
        layout.addWidget(coach_group)
        layout.addStretch(1)

        self._apply_selected_preset()
        self.clear_draft()

    @staticmethod
    def _wrap_layout(layout: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _apply_selected_preset(self) -> None:
        preset = self._selected_preset()
        self.model_edit.setText(preset.model_name)
        self.base_url_edit.setText(preset.base_url)
        api_required = preset.api_key_required
        self.api_key_edit.setEnabled(api_required)
        if not api_required:
            self.api_key_edit.clear()
            self.api_key_edit.setPlaceholderText("No API key needed for local models")
        else:
            self.api_key_edit.setPlaceholderText("Stored in the OS keychain only")

    def queue_prompt(self, prompt: str, skill_id: AgentSkillId) -> None:
        self.prompt_edit.setPlainText(prompt)
        self._requested_skill = skill_id

    def requested_skill(self) -> AgentSkillId | None:
        return self._requested_skill

    def clear_requested_skill(self) -> None:
        self._requested_skill = None

    def _selected_preset(self) -> ModelProviderConfig:
        provider_id = self.provider_combo.currentData()
        for preset in self._provider_presets:
            if preset.provider_id == provider_id:
                return preset
        return self._provider_presets[0]

    def provider_config(self) -> ModelProviderConfig:
        preset = self._selected_preset()
        return preset.model_copy(
            update={
                "model_name": self.model_edit.text().strip(),
                "base_url": self.base_url_edit.text().strip(),
            }
        )

    def provider_api_key(self) -> str:
        return self.api_key_edit.text().strip()

    def load_provider_state(
        self,
        profile: AppProfile | None,
        config: ModelProviderConfig,
        api_key: str,
    ) -> None:
        index = self.provider_combo.findData(config.provider_id)
        if index >= 0:
            self.provider_combo.blockSignals(True)
            self.provider_combo.setCurrentIndex(index)
            self.provider_combo.blockSignals(False)
        self._apply_selected_preset()
        self.model_edit.setText(config.model_name)
        self.base_url_edit.setText(config.base_url)
        self.api_key_edit.setText(api_key)
        if profile is None:
            self.context_label.setText("Context: no active profile")
        else:
            self.context_label.setText(f"Context: {profile.display_name} | {profile.primary_mission}")

    def update_status(
        self,
        *,
        profile: AppProfile | None,
        health: ProviderHealth,
        selected_candidate: OpportunityCandidate | None,
        portfolio_summary: PortfolioSummary | None,
    ) -> None:
        if health.provider_id == "none":
            self.status_label.setText("Status: local-first mode | no model configured")
        else:
            self.status_label.setText(
                f"Status: {health.provider_label} | {health.status.replace('_', ' ')} | {health.message}"
            )
        route_label = selected_candidate.summary if selected_candidate is not None else "no staged route"
        summary_label = (
            f"{portfolio_summary.completed_runs} completed runs"
            if portfolio_summary is not None and portfolio_summary.total_runs
            else "no paper history yet"
        )
        if profile is None:
            self.context_label.setText("Context: no active profile")
        else:
            self.context_label.setText(
                f"Context: {profile.display_name} | route: {route_label} | score: {summary_label}"
            )

    def clear_draft(self) -> None:
        self.draft_text.setPlainText("No draft yet. Ask Copilot to explain or draft something.")
        self.apply_draft_button.setEnabled(False)
        self.reject_draft_button.setEnabled(False)

    def set_response(self, session: AssistantSession) -> None:
        sources = ", ".join(session.sources) if session.sources else "local profile state"
        health_note = session.provider_health.message if session.provider_health.message else "Local-first mode"
        self.response_text.setPlainText(
            f"{session.response_text or (session.messages[-1].content if session.messages else '')}\n\nSources: {sources}\nProvider: {health_note}"
        )
        if session.draft is None:
            self.clear_draft()
            return
        action_lines = [f"- {action.title}" for action in session.draft.actions]
        self.draft_text.setPlainText(
            "\n".join(
                [
                    session.draft.title,
                    "",
                    session.draft.summary,
                    "",
                    f"Why: {session.draft.reason}",
                    "",
                    "Affected fields:",
                    *[f"- {field}" for field in session.draft.affected_fields],
                    "",
                    "Actions:",
                    *action_lines,
                ]
            )
        )
        self.apply_draft_button.setEnabled(True)
        self.reject_draft_button.setEnabled(True)


class ScannerTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.header_label = QLabel(
            "Scanner reads local books, stages routes for practice, and explains whether each route survives cost deductions."
        )
        self.header_label.setObjectName("heroTitle")
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)

        focus_group = QGroupBox("Scanner focus")
        focus_group.setProperty("panelTone", "primary")
        focus_layout = QVBoxLayout(focus_group)
        self.visual_label = QLabel(
            "A radial scan keeps the tab centered on one machine-like visual instead of drifting into dashboard clutter."
        )
        self.visual_label.setWordWrap(True)
        self.visual_label.setObjectName("heroText")
        self.focus_display = ArcadeScannerWidget()
        self.metrics_text = QPlainTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setProperty("consoleRole", "system")
        self.metrics_text.setMaximumHeight(82)
        self.route_board_text = QPlainTextEdit()
        self.route_board_text.setReadOnly(True)
        self.route_board_text.setProperty("consoleRole", "system")
        self.route_board_text.setMaximumHeight(112)
        focus_layout.addWidget(self.visual_label)
        focus_layout.addWidget(self.focus_display)
        focus_layout.addWidget(self.metrics_text)
        focus_layout.addWidget(self.route_board_text)
        layout.addWidget(focus_group)

        actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh scan")
        self.explain_button = QPushButton("Explain this candidate")
        self.explain_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Start selected practice")
        self.live_preview_button = QPushButton("Preview live lock")
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.explain_button)
        actions.addWidget(self.paper_button)
        actions.addWidget(self.live_preview_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        content_row = QHBoxLayout()
        content_row.setSpacing(10)
        candidates_group = QGroupBox("Signal routes")
        candidates_group.setProperty("panelTone", "subtle")
        candidates_layout = QVBoxLayout(candidates_group)
        self.candidate_list = QListWidget()
        self.candidate_list.setMaximumWidth(360)
        candidates_layout.addWidget(self.candidate_list)

        details_group = QGroupBox("Route explanation")
        details_group.setProperty("panelTone", "normal")
        details_layout = QVBoxLayout(details_group)
        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setProperty("consoleRole", "system")
        details_layout.addWidget(self.details_text)
        content_row.addWidget(candidates_group)
        content_row.addWidget(details_group, stretch=1)
        layout.addLayout(content_row)

        self.focus_display.set_snapshot(
            scan_state="standby",
            signals_found=0,
            routes_ready=0,
            top_edge_bps=0,
            top_quality=0,
            top_label="Waiting for first route",
        )
        self.metrics_text.setPlainText(
            "STATE      standby\n"
            "SIGNALS    0\n"
            "ROUTES     0\n"
            "TOP RETURN +0 bps\n"
            "QUALITY    000"
        )
        self.route_board_text.setPlainText(
            "ROUTE BOARD\n\n"
            "No staged routes yet.\n"
            "Recorder data must land before the scan can stage anything useful."
        )

    def update_candidates(self, candidates: list[OpportunityCandidate]) -> None:
        self.candidate_list.clear()
        for candidate in candidates:
            tone = "READY" if candidate.net_edge_bps > 0 else "HOLD "
            item = QListWidgetItem(
                f"[{tone}] {candidate.strategy_label} | {candidate.net_edge_bps:+d} bps | Q{candidate.opportunity_quality_score:03d}"
            )
            item.setData(32, candidate.id)
            self.candidate_list.addItem(item)
        if candidates:
            top_candidate = max(candidates, key=lambda candidate: candidate.net_edge_bps)
            scan_state = "active" if top_candidate.net_edge_bps > 0 else "locked"
            self.focus_display.set_snapshot(
                scan_state=scan_state,
                signals_found=len(candidates),
                routes_ready=sum(1 for candidate in candidates if candidate.net_edge_bps > 0),
                top_edge_bps=top_candidate.net_edge_bps,
                top_quality=top_candidate.opportunity_quality_score,
                top_label=top_candidate.strategy_label,
            )
            self.metrics_text.setPlainText(
                "\n".join(
                    [
                        f"STATE      {scan_state}",
                        f"SIGNALS    {len(candidates)}",
                        f"ROUTES     {sum(1 for candidate in candidates if candidate.net_edge_bps > 0)}",
                        f"TOP RETURN {top_candidate.net_edge_bps:+d} bps",
                        f"QUALITY    {top_candidate.opportunity_quality_score:03d}",
                        f"FOCUS      {top_candidate.strategy_label}",
                    ]
                )
            )
            board_lines = ["ROUTE BOARD", ""]
            for candidate in sorted(candidates, key=lambda item: (item.net_edge_bps, item.opportunity_quality_score), reverse=True)[:5]:
                route_state = "READY" if candidate.net_edge_bps > 0 else "HOLD"
                board_lines.append(
                    f"{route_state:<5} {candidate.strategy_label[:16]:<16} {candidate.net_edge_bps:+4d} bps  Q{candidate.opportunity_quality_score:03d}"
                )
                board_lines.append(f"      {candidate.summary}")
            self.route_board_text.setPlainText("\n".join(board_lines))
        if not candidates:
            self.focus_display.set_snapshot(
                scan_state="standby",
                signals_found=0,
                routes_ready=0,
                top_edge_bps=0,
                top_quality=0,
                top_label="Waiting for first route",
            )
            self.metrics_text.setPlainText(
                "STATE      standby\n"
                "SIGNALS    0\n"
                "ROUTES     0\n"
                "TOP RETURN +0 bps\n"
                "QUALITY    000"
            )
            self.route_board_text.setPlainText(
                "ROUTE BOARD\n\n"
                "No staged routes yet.\n"
                "1. Record a local sample.\n"
                "2. Refresh Scanner.\n"
                "3. Wait for a route that still clears costs."
            )
            self.details_text.setPlainText(
                "No scanner candidates yet.\n\n"
                "The fastest path is:\n"
                "1. Record one clean local sample.\n"
                "2. Refresh scan.\n"
                "3. Practice the first route that still clears costs."
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
        route_state = "READY TO RUN" if candidate.net_edge_bps > 0 else "HOLD / SKIP"
        self.details_text.setPlainText(
            "\n".join(
                [
                    "ROUTE READOUT",
                    "",
                    f"Route: {candidate.strategy_label}",
                    f"State: {route_state}",
                    f"Machine status: {candidate.status}",
                    f"Gross return: {candidate.gross_edge_bps} bps",
                    f"Net return: {candidate.net_edge_bps} bps",
                    f"Quality score: {candidate.opportunity_quality_score}",
                    f"Venues: {', '.join(candidate.venues)}",
                    f"Practice stake: ${candidate.recommended_stake_cents / 100:.2f}",
                    (
                        "Next move: start a practice run and bank the result into Score."
                        if candidate.net_edge_bps > 0
                        else "Next move: hold this route and keep scanning for a cleaner return."
                    ),
                    "",
                    "WHY IT APPEARED",
                    candidate.explanation.summary,
                    "",
                    "WHAT MATCHED",
                    *[f"- {item}" for item in matched_contracts],
                    "",
                    "ASSUMPTIONS",
                    *[f"- {item}" for item in assumptions],
                    "",
                    "COSTS AND DEDUCTIONS",
                    *deductions,
                ]
            )
        )


class ArbitrageTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.header_label = QLabel(
            "Guaranteed routes found by reading stored local market books.\n"
            "A buy-all-outcomes route works when the sum of all asks is below $1.\n"
            "A sell-all-outcomes route works when the sum of all bids exceeds $1."
        )
        self.header_label.setObjectName("heroTitle")
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Min return (e.g. 0.01):"))
        self.min_edge_input = QLineEdit()
        self.min_edge_input.setPlaceholderText("0")
        self.min_edge_input.setMaximumWidth(120)
        filter_row.addWidget(self.min_edge_input)
        self.refresh_button = QPushButton("Refresh routes")
        filter_row.addWidget(self.refresh_button)
        filter_row.addStretch(1)
        layout.addLayout(filter_row)

        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        opps_group = QGroupBox("Guaranteed routes")
        opps_group.setProperty("panelTone", "subtle")
        opps_layout = QVBoxLayout(opps_group)
        self.opportunity_list = QListWidget()
        self.opportunity_list.setMaximumWidth(380)
        opps_layout.addWidget(self.opportunity_list)

        details_group = QGroupBox("Route detail")
        details_group.setProperty("panelTone", "normal")
        details_layout = QVBoxLayout(details_group)
        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setProperty("consoleRole", "system")
        details_layout.addWidget(self.details_text)

        content_row.addWidget(opps_group)
        content_row.addWidget(details_group, stretch=1)
        layout.addLayout(content_row)

        self.details_text.setPlainText(
            "No data yet.\n\nRecord local market books first, then click 'Refresh routes'."
        )

    def update_opportunities(self, opportunities: list[ArbitrageOpportunity]) -> None:
        self.opportunity_list.clear()
        for i, opp in enumerate(opportunities):
            profit_pct = float(opp.guaranteed_profit) * 100
            strategy_short = "BUY" if opp.strategy == "buy_all_outcomes" else "SELL"
            label = f"[{strategy_short}] {opp.market[:32]}… | +{profit_pct:.2f}%"
            item = QListWidgetItem(label)
            item.setData(32, i)
            self.opportunity_list.addItem(item)
        if not opportunities:
            self.details_text.setPlainText(
                "No guaranteed route found with the current min-return filter.\n\n"
                "Try lowering the min return to '0' and refreshing, or record more local data."
            )

    def set_detail(self, opportunity: ArbitrageOpportunity | None) -> None:
        if opportunity is None:
            self.details_text.setPlainText("Select an opportunity to inspect its legs.")
            return
        profit_pct = float(opportunity.guaranteed_profit) * 100
        strategy_label = (
            "Buy all outcomes (sum of asks < $1)"
            if opportunity.strategy == "buy_all_outcomes"
            else "Sell all outcomes (sum of bids > $1)"
        )
        lines = [
            f"Market: {opportunity.market}",
            f"Strategy: {strategy_label}",
            f"Timestamp: {opportunity.timestamp}",
            f"Total price: ${float(opportunity.total_price):.4f}",
            f"Guaranteed profit: +{profit_pct:.4f}%  (${float(opportunity.guaranteed_profit):.4f} per $1 resolved)",
            f"Outcomes in basket: {opportunity.outcome_count}",
            "",
            "Legs:",
        ]
        for leg in opportunity.legs:
            outcome_str = f" ({leg.outcome})" if leg.outcome else ""
            lines.append(
                f"  {leg.asset_id}{outcome_str}"
                f"  bid={leg.best_bid}  ask={leg.best_ask}"
            )
        lines += [
            "",
            "Next step: practice this route in the Practice tab before any live use.",
        ]
        self.details_text.setPlainText("\n".join(lines))


class PaperBotsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel("Practice feed")
        self.header_label.setWordWrap(True)
        self.header_label.setObjectName("heroTitle")
        layout.addWidget(self.header_label)
        actions = QHBoxLayout()
        self.run_top_button = QPushButton("Start practice")
        self.refresh_button = QPushButton("Refresh feed")
        actions.addWidget(self.run_top_button)
        actions.addWidget(self.refresh_button)
        layout.addLayout(actions)

        upper_row = QHBoxLayout()
        upper_row.setSpacing(10)
        self.bot_slots_text = QPlainTextEdit()
        self.bot_slots_text.setReadOnly(True)
        self.bot_slots_text.setProperty("consoleRole", "system")
        self.bot_slots_text.setMaximumHeight(180)
        self.session_summary_text = QPlainTextEdit()
        self.session_summary_text.setReadOnly(True)
        self.session_summary_text.setProperty("consoleRole", "system")
        self.session_summary_text.setMaximumHeight(180)
        self.decision_trace_text = QPlainTextEdit()
        self.decision_trace_text.setReadOnly(True)
        self.decision_trace_text.setProperty("consoleRole", "system")
        self.decision_trace_text.setMaximumHeight(180)
        upper_row.addWidget(self.bot_slots_text, 1)
        upper_row.addWidget(self.session_summary_text, 1)
        upper_row.addWidget(self.decision_trace_text, 1)
        layout.addLayout(upper_row)

        self.event_feed = QListWidget()
        self.runs_list = QListWidget()
        layout.addWidget(self.event_feed, 3)
        layout.addWidget(self.runs_list, 2)

    def update_runs(
        self,
        runs: list[PaperRunResult],
        session: PaperBotSession | None = None,
        *,
        decision_trace: str = "",
        benchmark_audits: list[BenchmarkAudit] | None = None,
    ) -> None:
        self.runs_list.clear()
        for run in reversed(runs[-20:]):
            self.runs_list.addItem(
                f"{run.executed_at.isoformat()} | {run.status} | {run.strategy_ids[0] if run.strategy_ids else 'paper'} | ${run.realized_pnl_cents / 100:.2f}"
            )
        if not runs:
            self.runs_list.addItem("No practice runs yet. Record -> scan -> start practice.")
        self.set_last_run(
            runs[-1] if runs else None,
            session=session,
            decision_trace=decision_trace,
            benchmark_audits=benchmark_audits or [],
        )

    def set_last_run(
        self,
        run: PaperRunResult | None,
        *,
        session: PaperBotSession | None = None,
        decision_trace: str = "",
        benchmark_audits: list[BenchmarkAudit] | None = None,
    ) -> None:
        audits = benchmark_audits or []
        if session is None:
            self.bot_slots_text.setPlainText(
                "BOT SLOTS\n\n"
                "No practice run yet.\n"
                "Record a local sample, then start a practice run."
            )
            self.session_summary_text.setPlainText(
                "PRACTICE SUMMARY\n\n"
                "No practice run has banked score yet."
            )
            self.decision_trace_text.setPlainText(
                decision_trace
                or "RUN TRACE\n\nNo decision trace yet.\nStart a practice run to inspect bot decisions."
            )
            self.event_feed.clear()
        else:
            self.bot_slots_text.setPlainText(
                "\n".join(
                    [
                        "BOT SLOT STATES",
                        "",
                        *[
                            f"{slot.label.upper():<8} {slot.state.upper():<8} {slot.bot_label} :: ${slot.realized_pnl_cents / 100:.2f} :: {slot.detail}"
                            for slot in session.bot_slots
                        ],
                    ]
                )
            )
            self.session_summary_text.setPlainText(
                "\n".join(
                    [
                        "PRACTICE SUMMARY",
                        "",
                        f"Run ID: {session.session_id}",
                        f"State: {session.state}",
                        f"Practice PnL: ${session.realized_pnl_cents / 100:.2f}",
                        f"Score delta: {session.score_delta}",
                        f"Grade: {session.grade.grade}",
                        f"Combo: {session.grade.combo_count}",
                        f"Note: {session.grade.note}",
                    ]
                )
            )
            self.event_feed.clear()
            for event in session.events[-24:]:
                self.event_feed.addItem(
                    f"{event.occurred_at.isoformat()} | {event.title} | {event.detail}"
                )
            self.decision_trace_text.setPlainText(decision_trace)
        if run is None:
            return
        self.session_summary_text.appendPlainText(
            "\n".join(
                [
                    "",
                    "LAST BANKED RUN",
                    f"Run ID: {run.run_id}",
                    f"Status: {run.status}",
                    f"Expected return: {run.expected_edge_bps} bps",
                    f"Realized return: {run.realized_edge_bps} bps",
                    f"Fill ratio: {run.execution.fill_ratio:.2f}",
                    f"Deployed capital: ${run.deployed_capital_cents / 100:.2f}",
                    f"Realized practice PnL: ${run.realized_pnl_cents / 100:.2f}",
                    f"Opportunity quality: {run.opportunity_quality_score}",
                    f"Notes: {run.notes}",
                ]
            )
        )
        if audits:
            self.session_summary_text.appendPlainText(
                "\n".join(
                    [
                        "",
                        "BENCHMARK AUDIT",
                        *[
                            (
                                f"{audit.market_slug} | {audit.verdict} | "
                                f"{audit.symbol or 'unlinked'} | move {audit.underlying_move_bps} bps | "
                                f"return delta {audit.edge_vs_benchmark_bps} bps"
                            )
                            for audit in audits
                        ],
                    ]
                )
            )


class ScoreTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary_label = QLabel("Practice Score waiting for first route | Live Score locked")
        self.summary_label.setObjectName("heroTitle")
        self.summary_label.setWordWrap(True)
        self.mode_label = QLabel(
            "Practice score is the main progression system in Superior. Live score stays locked and empty."
        )
        self.mode_label.setWordWrap(True)
        actions = QHBoxLayout()
        self.summarize_button = QPushButton("Summarize with Copilot")
        self.summarize_button.setProperty("buttonRole", "secondary")
        actions.addWidget(self.summarize_button)
        actions.addStretch(1)
        self.portfolio_text = QPlainTextEdit()
        self.portfolio_text.setReadOnly(True)
        self.detail_text = QPlainTextEdit()
        self.detail_text.setReadOnly(True)
        self.ledger_text = QPlainTextEdit()
        self.ledger_text.setReadOnly(True)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.mode_label)
        layout.addLayout(actions)
        layout.addWidget(self.portfolio_text)
        layout.addWidget(self.detail_text)
        layout.addWidget(self.ledger_text)
        layout.addStretch(1)

    def update_summary(
        self,
        snapshot: ScoreSnapshot,
        ledger_entries: list[ScoreLedgerEntry],
        runs: list[PaperRunResult],
        portfolio_snapshot: PortfolioSnapshot,
        sessions: list[PaperBotSession],
        benchmark_audits: list[BenchmarkAudit] | None = None,
        *,
        lab_enabled: bool = False,
    ) -> None:
        audits = benchmark_audits or []
        if not runs:
            self.summary_label.setText("Practice Score waiting for first route | Live Score locked")
            self.portfolio_text.setPlainText(
                "PORTFOLIO SCORE\n\n"
                "No practice runs banked yet.\n"
                "Start with one local recorder pass, then arm a starter bot."
            )
            self.detail_text.setPlainText(
                "Practice score is the main loop in Superior v1.\n\n"
                "1. Record a local sample.\n"
                "2. Stage routes in Scanner.\n"
                "3. Start a practice run.\n"
                "4. Come back here for the first score update."
            )
            self.ledger_text.setPlainText(
                "No ledger entries yet.\n\n"
                "Your first practice run will create stake, realized-PnL, and session-grade history here."
            )
            if lab_enabled:
                self.ledger_text.appendPlainText(
                    "\n\nBENCHMARK AUDIT\n\nNo benchmark coverage yet. Save a Lab mapping if you want external reference checks."
                )
            return
        self.summary_label.setText(
            f"Practice Score ${snapshot.paper_realized_pnl_cents / 100:.2f} | "
            f"Portfolio {snapshot.portfolio_score} | Slots {snapshot.available_bot_slots}"
        )
        self.portfolio_text.setPlainText(
            "\n".join(
                [
                    "PORTFOLIO SCORE",
                    "",
                    f"Portfolio score: {portfolio_snapshot.portfolio_score}",
                    f"Mastery rating: {portfolio_snapshot.mastery_score}",
                    f"Available bot slots: {portfolio_snapshot.available_bot_slots}",
                    f"Sessions completed: {portfolio_snapshot.sessions_completed}",
                    f"Current streak: {portfolio_snapshot.current_streak}",
                    f"Last session grade: {portfolio_snapshot.last_session_grade}",
                    f"Next unlock: {snapshot.next_unlock_label}",
                ]
            )
        )
        lines = [
                    f"Total practice runs: {snapshot.total_runs}",
            f"Completed runs: {snapshot.completed_runs}",
            f"Hit rate: {snapshot.hit_rate:.1f}%",
                    f"Average expected return: {snapshot.average_expected_edge_bps} bps",
                    f"Average realized return: {snapshot.average_realized_edge_bps} bps",
            f"Current streak: {snapshot.current_streak}",
            f"Opportunity quality: {snapshot.opportunity_quality_score}",
            f"Available bot slots: {snapshot.available_bot_slots}",
            "Live score: locked and intentionally separate from paper progression.",
            "",
            "Recent session grades:",
        ]
        lines.extend(f"- {session.grade.grade} | {session.state} | ${session.realized_pnl_cents / 100:.2f}" for session in reversed(sessions[-5:]))
        lines.extend(["", "Curve preview:"])
        lines.extend(
            f"- {point.label} | score {point.cumulative_score} | paper ${point.cumulative_pnl_cents / 100:.2f}"
            for point in portfolio_snapshot.curve_points[-5:]
        )
        lines.extend(["", "Unlock track:"])
        lines.extend(
            f"- {'ONLINE' if unlock.unlocked else 'LOCKED'} | {unlock.label} | {unlock.detail}"
            for unlock in portfolio_snapshot.unlocks
        )
        if lab_enabled:
            lines.extend(["", "Benchmark audit:"])
            if audits:
                lines.extend(
                    f"- {audit.verdict} | {audit.market_slug} | {audit.symbol or 'unlinked'} | "
                    f"move {audit.underlying_move_bps} bps | delta {audit.edge_vs_benchmark_bps} bps"
                    for audit in audits[:5]
                )
            else:
                lines.append("- No benchmark-linked sessions yet.")
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
            f"Practice gate passed: {'yes' if live_status.paper_gate_passed else 'no'}",
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
        self.benchmark_status_label = QLabel("Benchmark audit is offline.")
        self.benchmark_status_label.setWordWrap(True)
        benchmark_actions = QHBoxLayout()
        self.save_benchmark_key_button = QPushButton("Save benchmark key")
        self.save_benchmark_key_button.setProperty("buttonRole", "secondary")
        self.refresh_benchmark_button = QPushButton("Refresh benchmark")
        self.refresh_benchmark_button.setProperty("buttonRole", "secondary")
        benchmark_actions.addWidget(self.save_benchmark_key_button)
        benchmark_actions.addWidget(self.refresh_benchmark_button)
        mapping_group = QGroupBox("Benchmark mapping")
        mapping_form = QFormLayout(mapping_group)
        self.market_slug_combo = QComboBox()
        self.market_slug_combo.setEditable(True)
        self.symbol_edit = QLineEdit()
        self.symbol_edit.setPlaceholderText("SPY, BTC-USD, QQQ")
        self.instrument_type_combo = QComboBox()
        for item in ("stock", "etf", "crypto", "index", "macro", "unknown"):
            self.instrument_type_combo.addItem(item.title(), item)
        self.interval_combo = QComboBox()
        self.interval_combo.addItem("1m", "1m")
        self.interval_combo.addItem("1d", "1d")
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional note about why this mapping is safe.")
        mapping_form.addRow("Market slug", self.market_slug_combo)
        mapping_form.addRow("Symbol", self.symbol_edit)
        mapping_form.addRow("Instrument", self.instrument_type_combo)
        mapping_form.addRow("Interval", self.interval_combo)
        mapping_form.addRow("Notes", self.notes_edit)
        self.save_mapping_button = QPushButton("Save mapping")
        self.save_mapping_button.setProperty("buttonRole", "secondary")
        mapping_form.addRow("", self.save_mapping_button)
        self.modules_text = QPlainTextEdit()
        self.modules_text.setReadOnly(True)
        self.benchmark_text = QPlainTextEdit()
        self.benchmark_text.setReadOnly(True)
        layout.addWidget(self.status_label)
        layout.addWidget(self.enable_checkbox)
        layout.addWidget(self.save_button)
        layout.addWidget(self.benchmark_status_label)
        layout.addLayout(benchmark_actions)
        layout.addWidget(mapping_group)
        layout.addWidget(self.modules_text)
        layout.addWidget(self.benchmark_text)
        layout.addStretch(1)

    def update_view(
        self,
        profile: AppProfile | None,
        modules: list[StrategyModule],
        *,
        benchmark_ready: bool = False,
        benchmark_links: list[str] | None = None,
        suggested_market_slugs: list[str] | None = None,
        benchmark_audits: list[BenchmarkAudit] | None = None,
    ) -> None:
        links = benchmark_links or []
        audits = benchmark_audits or []
        suggestions = suggested_market_slugs or []
        if profile is None:
            self.status_label.setText("Lab is off.")
            self.modules_text.setPlainText("Choose a profile to inspect Lab modules.")
            self.benchmark_status_label.setText("Choose a profile to manage benchmark audit.")
            self.benchmark_text.setPlainText("No benchmark profile loaded.")
            return
        self.enable_checkbox.setChecked(profile.lab_enabled)
        self.status_label.setText("Lab is on." if profile.lab_enabled else "Lab is off.")
        self.market_slug_combo.clear()
        for slug in suggestions:
            self.market_slug_combo.addItem(slug, slug)
        self.benchmark_status_label.setText(
            "Benchmark audit ready. External data stays audit-only."
            if benchmark_ready
            else "Benchmark audit offline. Save a rotated key or use env override for sync."
        )
        lines = [
            "High-risk and experimental strategies stay paper-only in v1.",
            "",
        ]
        for module in modules:
            if module.tier != "lab":
                continue
            lines.append(f"{module.label}: {module.description}")
        self.modules_text.setPlainText("\n".join(lines))
        benchmark_lines = ["BENCHMARK LAB", ""]
        if not links:
            benchmark_lines.append("No benchmark links saved yet.")
        else:
            benchmark_lines.extend(links)
        benchmark_lines.extend(["", "Recent audits:"])
        if audits:
            benchmark_lines.extend(
                f"- {audit.verdict} | {audit.market_slug} | {audit.symbol or 'unlinked'} | "
                f"move {audit.underlying_move_bps} bps | delta {audit.edge_vs_benchmark_bps} bps"
                for audit in audits[:6]
            )
        else:
            benchmark_lines.append("- No benchmark audits yet.")
        self.benchmark_text.setPlainText("\n".join(benchmark_lines))


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
        release_form.addRow("Runtime", QLabel("Desktop app for recorder, scanner, practice runs, and diagnostics"))
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
        arbitrage_service: ArbitrageService | None = None,
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
        self._bot_recipe_store = BotRecipeStore()
        self._bot_config_service = BotConfigService(self._bot_recipe_store)
        self._bot_registry_service = BotRegistryService(self._bot_config_service)
        self._session_store = SessionEventStore(paper_store)
        self._unlock_track_service = UnlockTrackService()
        self._progression_service = ProgressionService()
        self._decision_trace_formatter = DecisionTraceFormatter()
        self._portfolio_engine = PortfolioEngine(
            paper_store,
            self._bot_config_service,
            self._unlock_track_service,
        )
        self._paper_simulation_engine = PaperSimulationEngine(
            paper_store=paper_store,
            paper_execution_engine=paper_execution_engine,
            bot_config_service=self._bot_config_service,
            session_store=self._session_store,
        )
        self._experimental_live_service = experimental_live_service
        self._live_execution_engine = live_execution_engine
        self._unlock_service = unlock_service
        self._assistant_service = assistant_service
        self._copilot_presets = self._assistant_service.provider_presets()
        self._arb_service = arbitrage_service or ArbitrageService()
        self._benchmark_api_key_env_override = resolve_benchmark_api_key()
        self._profiles: list[AppProfile] = []
        self._latest_candidates: list[OpportunityCandidate] = []
        self._latest_arb_opportunities: list[ArbitrageOpportunity] = []
        self._last_paper_run: PaperRunResult | None = None
        self._last_session: PaperBotSession | None = None
        self._previous_state = "idle"
        self._home_primary_action_mode = "recorder"
        self._pending_copilot_draft: AgentDraft | None = None
        self._loaded_copilot_profile_id: str | None = None

        self.setWindowTitle("Superior")
        self.resize(1260, 880)

        self.home_tab = HangarHomeTab()
        self.loadout_tab = LoadoutTab()
        self.learn_tab = LearnTab(self._copilot_presets)
        self.scanner_tab = ScannerTab()
        self.arb_tab = ArbitrageTab()
        self.paper_bots_tab = PaperBotsTab()
        self.score_tab = ScoreTab()
        self.live_unlock_tab = LiveUnlockTab()
        self.lab_tab = LabTab()
        self.diagnostics_tab = DiagnosticsTab()
        self.about_tab = AboutTab(paths)

        self.shell = DesktopShell()
        self.profile_selector = self.shell.header.profile_bar.profile_selector
        self.profile_selector.currentIndexChanged.connect(self._on_profile_changed)
        self.setup_button = self.shell.header.profile_bar.setup_button
        self.setup_button.clicked.connect(self._open_setup_wizard)

        self.tabs = self.shell.nav
        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.loadout_tab, "Profile")
        self.tabs.addTab(self.scanner_tab, "Scanner")
        self.tabs.addTab(self.arb_tab, "Routes")
        self.tabs.addTab(self.paper_bots_tab, "Practice")
        self.tabs.addTab(self.score_tab, "Score")
        self.tabs.addTab(self.diagnostics_tab, "Diagnostics")
        self.tabs.addTab(self.learn_tab, "Copilot")
        self.tabs.addTab(self.live_unlock_tab, "Live")
        self.tabs.addTab(self.about_tab, "About")
        self.setCentralWidget(self.shell)
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
        self.home_tab.start_button.clicked.connect(self._activate_home_primary_action)
        self.home_tab.stop_button.clicked.connect(self._stop_run)
        self.home_tab.replay_button.clicked.connect(lambda: self._run_preset("replay-latest"))
        self.home_tab.verify_button.clicked.connect(lambda: self._run_preset("verify-latest"))
        self.home_tab.scan_button.clicked.connect(self._refresh_scanner)
        self.home_tab.paper_button.clicked.connect(self._start_paper_session)

        self.loadout_tab.save_button.clicked.connect(self._save_loadout)
        self.loadout_tab.refresh_button.clicked.connect(self._refresh_all_views)
        self.loadout_tab.fork_button.clicked.connect(self._fork_selected_recipe)
        self.loadout_tab.copilot_button.clicked.connect(
            lambda: self._prime_copilot("Build me a safer starter bot.", "draft_starter_bot")
        )

        self.learn_tab.ask_button.clicked.connect(self._ask_copilot)
        self.learn_tab.test_provider_button.clicked.connect(self._test_copilot_connection)
        self.learn_tab.save_provider_button.clicked.connect(self._save_copilot_settings)
        self.learn_tab.apply_draft_button.clicked.connect(self._apply_copilot_draft)
        self.learn_tab.reject_draft_button.clicked.connect(self._reject_copilot_draft)
        self.learn_tab.explain_route_button.clicked.connect(
            lambda: self._prime_copilot("Explain this route.", "explain_route")
        )
        self.learn_tab.draft_bot_button.clicked.connect(
            lambda: self._prime_copilot("Build me a safer starter bot.", "draft_starter_bot")
        )
        self.learn_tab.summarize_button.clicked.connect(
            lambda: self._prime_copilot("Summarize my last practice run.", "summarize_last_session")
        )
        self.learn_tab.fix_loadout_button.clicked.connect(
            lambda: self._prime_copilot("Fix my setup.", "adjust_bot_settings")
        )
        self.learn_tab.lock_button.clicked.connect(
            lambda: self._prime_copilot("Why is live locked?", "explain_lock")
        )

        self.scanner_tab.refresh_button.clicked.connect(self._refresh_scanner)
        self.scanner_tab.explain_button.clicked.connect(
            lambda: self._prime_copilot("Explain this route.", "explain_route")
        )
        self.scanner_tab.paper_button.clicked.connect(self._start_selected_session)
        self.scanner_tab.live_preview_button.clicked.connect(self._preview_live_lock)
        self.scanner_tab.candidate_list.currentItemChanged.connect(self._on_candidate_changed)

        self.arb_tab.refresh_button.clicked.connect(self._refresh_arbitrage)
        self.arb_tab.opportunity_list.currentItemChanged.connect(self._on_arb_opportunity_changed)

        self.paper_bots_tab.run_top_button.clicked.connect(self._start_paper_session)
        self.paper_bots_tab.refresh_button.clicked.connect(self._refresh_portfolio_views)
        self.score_tab.summarize_button.clicked.connect(
            lambda: self._prime_copilot("Summarize my last practice run.", "summarize_last_session")
        )

        self.live_unlock_tab.save_button.clicked.connect(self._save_unlock_preferences)
        self.live_unlock_tab.refresh_button.clicked.connect(self._refresh_all_views)
        self.live_unlock_tab.shadow_button.clicked.connect(lambda: self._set_live_mode("shadow"))
        self.live_unlock_tab.micro_button.clicked.connect(lambda: self._set_live_mode("micro"))
        self.live_unlock_tab.experimental_button.clicked.connect(lambda: self._set_live_mode("experimental"))
        self.live_unlock_tab.reset_button.clicked.connect(lambda: self._set_live_mode("locked"))

        self.lab_tab.save_button.clicked.connect(self._save_lab_setting)
        self.lab_tab.save_benchmark_key_button.clicked.connect(self._save_benchmark_key)
        self.lab_tab.refresh_benchmark_button.clicked.connect(self._refresh_all_views)
        self.lab_tab.save_mapping_button.clicked.connect(self._save_benchmark_mapping)

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
        else:
            self._loaded_copilot_profile_id = None

    def _refresh_status_only(self) -> None:
        profile = self._current_profile()
        status = self._controller.status(profile)
        connections = self._venue_connections(profile)
        credential_statuses = self._credential_statuses(profile)
        score_snapshot = self._score_service.snapshot(profile)
        portfolio_snapshot = self._portfolio_engine.snapshot(profile)
        paper_summary = self._paper_store.summary(profile) if profile is not None else None
        unlocks = self._unlock_track_service.unlocks(profile, score_snapshot) if profile is not None else []
        bot_configs = self._bot_config_service.configs(profile, score_snapshot) if profile is not None else []
        registry_entries = (
            self._bot_registry_service.entries(profile, score_snapshot, unlocks) if profile is not None else []
        )
        slot_preview = self._bot_config_service.slot_preview(profile, score_snapshot) if profile is not None else []
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
            candidate_count=len(self._latest_candidates),
        )
        self._sync_shell_state(profile, status, len(self._latest_candidates))
        self.live_unlock_tab.update_view(profile, checklist, live_status)
        diagnostics_text = self._diagnostics.diagnostics_text(
            profile=profile,
            status=status,
            credential_statuses=credential_statuses,
        )
        self.diagnostics_tab.text.setPlainText(diagnostics_text)
        profile_id = profile.id if profile is not None else None
        provider_config = self._copilot_provider_config(profile)
        provider_api_key = self._copilot_api_key(profile)
        if self._loaded_copilot_profile_id != profile_id:
            self._load_copilot_state(profile)
        provider_health = self._assistant_service.provider_health(provider_config, provider_api_key)
        self.learn_tab.update_status(
            profile=profile,
            health=provider_health,
            selected_candidate=self._selected_candidate(),
            portfolio_summary=paper_summary,
        )
        if profile is not None:
            self.loadout_tab.update_view(
                profile,
                loadout=self._loadout_service.build_loadout(profile),
                connector_states=self._loadout_service.connector_states(profile, connections, credential_statuses),
                module_states=self._loadout_service.module_states(profile, self._opportunity_engine.strategy_modules()),
                bot_configs=bot_configs,
                registry_entries=registry_entries,
                slot_preview=slot_preview,
                unlocks=unlocks,
            )
        else:
            self.loadout_tab.update_view(
                None,
                loadout=None,
                connector_states=[],
                module_states=[],
                bot_configs=[],
                registry_entries=[],
                slot_preview=[],
                unlocks=[],
            )
        self._sync_home_primary_action(profile, status, score_snapshot)
        if self._previous_state == "running" and status.state in {"completed", "failed"}:
            self._tray.showMessage("Superior", status.last_message, self._tray.icon(), 5000)
        self._previous_state = status.state

    def _refresh_all_views(self) -> None:
        self._refresh_scanner()
        self._refresh_arbitrage()
        self._refresh_portfolio_views()
        profile = self._current_profile()
        benchmark_links: list[str] = []
        benchmark_audits: list[BenchmarkAudit] = []
        if profile is not None:
            benchmark_store = self._benchmark_store(profile)
            benchmark_links = [
                f"- {link.market_slug} -> {link.symbol} [{link.interval_preference}]"
                for link in benchmark_store.list_links(profile.id)
            ]
            benchmark_audits = self._benchmark_audit_service(profile).recent_audits(profile.id, limit=6)
        self.lab_tab.update_view(
            profile,
            self._opportunity_engine.strategy_modules(),
            benchmark_ready=self._benchmark_ready(profile),
            benchmark_links=benchmark_links,
            suggested_market_slugs=self._suggested_market_slugs(profile),
            benchmark_audits=benchmark_audits,
        )
        self._sync_lab_tab_visibility(profile)

    def _refresh_scanner(self) -> None:
        profile = self._current_profile()
        self._latest_candidates = self._opportunity_engine.scan(profile) if profile is not None else []
        self.scanner_tab.update_candidates(self._latest_candidates)
        self.scanner_tab.set_details(self._selected_candidate())
        self._refresh_status_only()

    def _refresh_arbitrage(self) -> None:
        profile = self._current_profile()
        min_edge = self.arb_tab.min_edge_input.text().strip() or "0"
        try:
            self._latest_arb_opportunities = (
                self._arb_service.find_opportunities(profile, min_edge=min_edge)
                if profile is not None
                else []
            )
        except Exception:
            _log.exception("ArbitrageService.find_opportunities failed")
            self._latest_arb_opportunities = []
        self.arb_tab.update_opportunities(self._latest_arb_opportunities)
        selected = self._latest_arb_opportunities[0] if self._latest_arb_opportunities else None
        self.arb_tab.set_detail(selected)

    def _on_arb_opportunity_changed(self) -> None:
        current_item = self.arb_tab.opportunity_list.currentItem()
        if current_item is None:
            self.arb_tab.set_detail(None)
            return
        index = current_item.data(32)
        opportunity = (
            self._latest_arb_opportunities[index]
            if isinstance(index, int) and 0 <= index < len(self._latest_arb_opportunities)
            else None
        )
        self.arb_tab.set_detail(opportunity)

    def _refresh_portfolio_views(self) -> None:
        profile = self._current_profile()
        if profile is None:
            self.paper_bots_tab.update_runs([], None)
            self.score_tab.update_summary(ScoreSnapshot(), [], [], PortfolioSnapshot(), [], [], lab_enabled=False)
            return
        runs = self._paper_store.list_runs(profile)
        sessions = self._session_store.list_sessions(profile)
        score_snapshot = self._score_service.snapshot(profile)
        portfolio_snapshot = self._portfolio_engine.snapshot(profile)
        ledger_entries = self._score_service.ledger(profile, limit=10)
        last_session = self._last_session or (sessions[-1] if sessions else None)
        benchmark_audits = (
            self._benchmark_audit_service(profile).recent_audits(profile.id, limit=10)
            if profile.lab_enabled
            else []
        )
        session_audits = (
            self._benchmark_audit_service(profile).audits_for_session(profile.id, last_session.session_id)
            if profile.lab_enabled and last_session is not None
            else []
        )
        self.paper_bots_tab.update_runs(
            runs,
            last_session,
            decision_trace=self._decision_trace_formatter.render(last_session),
            benchmark_audits=session_audits,
        )
        self.score_tab.update_summary(
            score_snapshot,
            ledger_entries,
            runs,
            portfolio_snapshot,
            sessions,
            benchmark_audits,
            lab_enabled=profile.lab_enabled,
        )

    def _venue_connections(self, profile: AppProfile | None) -> list[VenueConnection]:
        if profile is None:
            return []
        return [adapter.connection(profile, self._credential_vault) for adapter in self._venue_adapters]

    def _credential_statuses(self, profile: AppProfile | None) -> list[CredentialStatus]:
        if profile is None:
            return []
        return self._credential_vault.statuses_for_profile(profile.id)

    def _benchmark_store(self, profile: AppProfile) -> BenchmarkStore:
        return BenchmarkStore(profile.data_dir / "market_data.duckdb")

    def _benchmark_link_service(self, profile: AppProfile) -> BenchmarkLinkService:
        return BenchmarkLinkService(self._benchmark_store(profile))

    def _benchmark_audit_service(self, profile: AppProfile) -> BenchmarkAuditService:
        return BenchmarkAuditService(self._benchmark_store(profile))

    def _benchmark_ready(self, profile: AppProfile | None) -> bool:
        if profile is None:
            return False
        return resolve_benchmark_api_key(vault=self._credential_vault, profile_id=profile.id) is not None

    def _suggested_market_slugs(self, profile: AppProfile | None) -> list[str]:
        if profile is None:
            return []
        slugs = {candidate.market_slug for candidate in self._latest_candidates}
        for run in self._paper_store.list_runs(profile)[-12:]:
            slugs.update(position.market_slug for position in run.positions)
        return sorted(slug for slug in slugs if slug)

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
            self._refresh_status_only()
            return
        self.scanner_tab.set_details(self._selected_candidate())
        self._refresh_status_only()

    def _prime_copilot(self, prompt: str, skill_id: AgentSkillId) -> None:
        self.tabs.setCurrentWidget(self.learn_tab)
        self.learn_tab.queue_prompt(prompt, skill_id)
        self.learn_tab.prompt_edit.setFocus()

    def _copilot_provider_config(self, profile: AppProfile | None) -> ModelProviderConfig:
        preset = next(
            (
                item
                for item in self._copilot_presets
                if item.provider_id == (profile.copilot_provider_id if profile is not None else "none")
            ),
            self._copilot_presets[0],
        )
        if profile is None:
            return preset.model_copy(deep=True)
        return preset.model_copy(
            update={
                "model_name": profile.copilot_model_name or preset.model_name,
                "base_url": profile.copilot_base_url or preset.base_url,
            }
        )

    def _copilot_api_key(self, profile: AppProfile | None) -> str:
        if profile is None:
            return ""
        return self._credential_vault.load(profile.id, "coach").get("api_key", "")

    def _load_copilot_state(self, profile: AppProfile | None) -> None:
        self.learn_tab.load_provider_state(
            profile,
            self._copilot_provider_config(profile),
            self._copilot_api_key(profile),
        )
        self._loaded_copilot_profile_id = profile.id if profile is not None else None
        self._pending_copilot_draft = None
        self.learn_tab.clear_draft()

    def _test_copilot_connection(self) -> None:
        profile = self._current_profile()
        health = self._assistant_service.provider_health(
            self.learn_tab.provider_config(),
            self.learn_tab.provider_api_key(),
        )
        self.learn_tab.update_status(
            profile=profile,
            health=health,
            selected_candidate=self._selected_candidate(),
            portfolio_summary=self._paper_store.summary(profile) if profile is not None else None,
        )
        self.statusBar().showMessage(f"Copilot: {health.message}", 5000)

    def _save_copilot_settings(self) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Choose a profile", "Choose a profile before saving Copilot settings.")
            return
        config = self.learn_tab.provider_config()
        api_key = self.learn_tab.provider_api_key()
        equipped_connectors: list[str] = [
            connector for connector in profile.equipped_connectors if connector != "coach"
        ]
        if config.provider_id != "none":
            equipped_connectors.append("coach")
        updated = profile.model_copy(
            update={
                "ai_coach_enabled": config.provider_id != "none",
                "equipped_connectors": equipped_connectors,
                "copilot_provider_id": config.provider_id,
                "copilot_model_name": config.model_name,
                "copilot_base_url": config.base_url,
            }
        )
        self._profile_store.save_profile(updated)
        if api_key:
            self._credential_vault.save(
                updated.id,
                "coach",
                {
                    "provider_name": config.provider_label,
                    "model_name": config.model_name,
                    "api_key": api_key,
                },
            )
        else:
            self._credential_vault.delete(updated.id, "coach")
        self._loaded_copilot_profile_id = None
        self._refresh_profiles(updated.id)
        self._refresh_status_only()
        self.statusBar().showMessage("Copilot settings saved locally.", 5000)

    def _apply_copilot_draft(self) -> None:
        profile = self._current_profile()
        draft = self._pending_copilot_draft
        if profile is None or draft is None:
            QMessageBox.information(self, "No draft", "Ask Copilot for a draft before trying to apply one.")
            return
        updated_profile = profile
        applied_actions: list[str] = []
        for action in draft.actions:
            if action.action_type == "save_bot_recipe":
                updated_recipe = self._apply_bot_recipe_draft(updated_profile, action)
                applied_actions.append(updated_recipe.label)
                continue
            if action.action_type == "update_loadout":
                updated_profile = self._apply_loadout_draft(updated_profile, action)
                applied_actions.append(action.title)
        if updated_profile.id != profile.id or updated_profile != profile:
            self._profile_store.save_profile(updated_profile)
            self._refresh_profiles(updated_profile.id)
        self._pending_copilot_draft = None
        self.learn_tab.clear_draft()
        self._refresh_all_views()
        applied_summary = ", ".join(applied_actions) if applied_actions else "No changes were applied."
        self.statusBar().showMessage(f"Copilot applied: {applied_summary}", 5000)

    def _reject_copilot_draft(self) -> None:
        self._pending_copilot_draft = None
        self.learn_tab.clear_draft()
        self.statusBar().showMessage("Copilot draft cleared.", 4000)

    def _apply_bot_recipe_draft(self, profile: AppProfile, action: DraftAction) -> BotRecipe:
        changes = action.changes
        if action.target_id:
            recipe = self._bot_config_service.fork_recipe(
                profile,
                action.target_id,
                new_label=changes.get("label") or None,
            )
            recipe = recipe.model_copy(
                update={
                    "label": changes.get("label", recipe.label),
                    "description": changes.get("description", recipe.description),
                    "strategy_family": changes.get("strategy_family", recipe.strategy_family),
                    "min_net_edge_bps": self._draft_int(changes.get("min_net_edge_bps"), recipe.min_net_edge_bps),
                    "target_stake_cents": self._draft_int(changes.get("target_stake_cents"), recipe.target_stake_cents),
                    "max_assignments": self._draft_int(changes.get("max_assignments"), recipe.max_assignments),
                    "route_preference": changes.get("route_preference", recipe.route_preference),
                    "lab_only": self._draft_bool(changes.get("lab_only"), recipe.lab_only),
                    "enabled": self._draft_bool(changes.get("enabled"), recipe.enabled),
                }
            )
            return self._bot_recipe_store.save_recipe(profile, recipe)
        recipe = BotRecipe(
            recipe_id="",
            profile_id=profile.id,
            label=changes.get("label", "Copilot Draft"),
            description=changes.get("description", "Copilot-created paper recipe."),
            strategy_family=changes.get("strategy_family", "internal-binary"),
            min_net_edge_bps=self._draft_int(changes.get("min_net_edge_bps"), 25),
            target_stake_cents=self._draft_int(changes.get("target_stake_cents"), 1_200),
            max_assignments=self._draft_int(changes.get("max_assignments"), 1),
            route_preference=changes.get("route_preference", "highest_edge"),
            lab_only=self._draft_bool(changes.get("lab_only"), False),
            enabled=self._draft_bool(changes.get("enabled"), True),
            source_kind="custom",
        )
        return self._bot_recipe_store.save_recipe(profile, recipe)

    def _apply_loadout_draft(self, profile: AppProfile, action: DraftAction) -> AppProfile:
        changes = action.changes
        connectors = self._draft_list(changes.get("equipped_connectors"), profile.equipped_connectors)
        modules = self._draft_list(changes.get("equipped_modules"), profile.equipped_modules)
        ai_coach_enabled = "coach" in connectors
        return profile.model_copy(
            update={
                "equipped_connectors": connectors,
                "equipped_modules": modules,
                "ai_coach_enabled": ai_coach_enabled,
            }
        )

    @staticmethod
    def _draft_int(raw_value: str | None, fallback: int) -> int:
        if raw_value is None or not raw_value.strip():
            return fallback
        try:
            return int(raw_value)
        except ValueError:
            return fallback

    @staticmethod
    def _draft_bool(raw_value: str | None, fallback: bool) -> bool:
        if raw_value is None or not raw_value.strip():
            return fallback
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _draft_list(raw_value: str | None, fallback: Sequence[str]) -> list[str]:
        if raw_value is None or not raw_value.strip():
            return list(fallback)
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    def _open_setup_wizard(self) -> None:
        wizard = SetupWizard(
            profile_store=self._profile_store,
            credential_vault=self._credential_vault,
            startup_manager=self._startup_manager,
            preset_labels=[(preset.id, preset.label) for preset in self._controller.presets()],
            parent=self,
        )
        wizard.setWindowModality(Qt.WindowModality.WindowModal)
        wizard.raise_()
        wizard.activateWindow()
        if wizard.exec() == SetupWizard.DialogCode.Accepted:
            self._sync_startup_manager()
            self._refresh_profiles(wizard.created_profile_id)
            self.tabs.setCurrentWidget(self.home_tab)
            self._refresh_all_views()
            self.raise_()
            self.activateWindow()
            profile = self._current_profile()
            profile_name = profile.display_name if profile is not None else "Profile"
            self.statusBar().showMessage(
            f"{profile_name} is ready. Run recorder to start the first practice loop.",
                6000,
            )

    def _on_profile_changed(self) -> None:
        self._refresh_all_views()

    def _start_default_preset(self) -> None:
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Create a profile", "Create a profile before starting the recorder.")
            return
        self._run_preset(profile.default_preset)

    def _activate_home_primary_action(self) -> None:
        profile = self._current_profile()
        if profile is None:
            self._start_default_preset()
            return
        status = self._controller.status(profile)
        market_db_exists = (profile.data_dir / "market_data.duckdb").exists()
        has_data = market_db_exists or (
            status.summary is not None
            and (status.summary.raw_messages > 0 or status.summary.book_snapshots > 0)
        )
        if has_data and bool(self._latest_candidates) and status.state != "running":
            self._start_paper_session()
            return
        self._start_default_preset()

    def _sync_home_primary_action(
        self,
        profile: AppProfile | None,
        status: EngineStatus,
        score_snapshot: ScoreSnapshot,
    ) -> None:
        if profile is None:
            self._home_primary_action_mode = "recorder"
            return
        market_db_exists = (profile.data_dir / "market_data.duckdb").exists()
        has_data = market_db_exists or (
            status.summary is not None
            and (status.summary.raw_messages > 0 or status.summary.book_snapshots > 0)
        )
        is_running = status.state == "running"
        session_ready = has_data and bool(self._latest_candidates)
        self._home_primary_action_mode = "session" if session_ready and not is_running else "recorder"
        if self._home_primary_action_mode == "session":
            self.home_tab.start_button.setText("Start practice")
            self.home_tab.primary_action_hint.setText(
                "The app is primed. Start a practice run to bank the first score."
            )
        elif has_data:
            self.home_tab.start_button.setText("Run recorder")
            self.home_tab.primary_action_hint.setText(
                "Local books are ready. Refresh Scan until a clean route stages for the first practice run."
            )
        else:
            self.home_tab.start_button.setText("Run recorder")
            self.home_tab.primary_action_hint.setText(
                "Run recorder is the only action that matters until the first local market sample lands."
            )
        self.home_tab.set_secondary_actions_visible(
            has_data or bool(self._latest_candidates) or score_snapshot.completed_runs > 0 or status.state in {"completed", "failed"}
        )
        self.home_tab.scan_button.setText("Scan routes" if has_data else "Scan routes [locked]")
        self.home_tab.paper_button.setText("Start practice" if session_ready else "Start practice [locked]")

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
            QMessageBox.warning(self, "Equip a connector", "Equip at least one venue connector before saving setup.")
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
            QMessageBox.warning(self, "Equip a module", "Equip at least one play style before saving setup.")
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
            updated.primary_mission = "Record your first local sample, arm the starter bot, and bank your first score."
        self._profile_store.save_profile(updated)
        self._refresh_profiles(updated.id)
        self._refresh_all_views()
        self.statusBar().showMessage("Setup saved.", 4000)

    def _fork_selected_recipe(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        recipe_id = self.loadout_tab.fork_source_combo.currentData()
        if not isinstance(recipe_id, str) or not recipe_id:
            QMessageBox.information(self, "Choose a bot", "Choose a visible bot recipe before forking it locally.")
            return
        try:
            recipe = self._bot_config_service.fork_recipe(profile, recipe_id)
        except KeyError:
            QMessageBox.warning(self, "Bot not found", "The selected bot recipe is no longer available.")
            return
        self._refresh_all_views()
        self.statusBar().showMessage(f"Added {recipe.label} to the local bot library.", 5000)

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
        self._start_paper_session()

    def _paper_selected_opportunity(self) -> None:
        self._start_selected_session()

    def _start_selected_session(self) -> None:
        profile = self._current_profile()
        candidate = self._selected_candidate()
        if profile is None or candidate is None:
            QMessageBox.information(self, "Choose a candidate", "Pick a scanner result before starting practice on it.")
            return
        self._start_paper_session(preferred_candidates=[candidate])

    def _start_paper_session(self, _checked: bool = False, preferred_candidates: list[OpportunityCandidate] | None = None) -> None:
        del _checked
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Choose a profile", "Create or choose a profile before starting a practice run.")
            return
        if preferred_candidates is None:
            candidates = [candidate for candidate in self._latest_candidates if candidate.net_edge_bps > 0]
        else:
            candidates = [candidate for candidate in preferred_candidates if candidate.net_edge_bps > 0]
        if not candidates:
            self._refresh_scanner()
            candidates = [candidate for candidate in self._latest_candidates if candidate.net_edge_bps > 0]
        if not candidates:
            QMessageBox.information(
                self,
                "No staged routes",
                "No current route clears the bot gates yet. Record more local books or refresh Scanner.",
            )
            return
        score_snapshot = self._score_service.snapshot(profile)
        session = self._paper_simulation_engine.run_session(profile, candidates, score_snapshot=score_snapshot)
        self._last_session = session
        runs = self._paper_store.list_runs(profile)
        if profile.lab_enabled:
            session_runs = [run for run in runs if run.run_id in session.run_ids]
            self._benchmark_audit_service(profile).audit_session(profile.id, session, session_runs)
        if runs:
            self._last_paper_run = runs[-1]
        active_profile = profile
        if not profile.first_run_completed:
            active_profile = profile.model_copy(
                update={
                    "first_run_completed": True,
                    "primary_mission": "Keep the loop steady: record, stage routes, start practice runs, and grow score deliberately.",
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
                    "primary_mission": "Practice gate passed. Keep score pressure steady before touching shadow-live previews.",
                }
            )
            self._profile_store.save_profile(active_profile)
            self._refresh_profiles(active_profile.id)
        self._refresh_portfolio_views()
        self._refresh_status_only()
        self.statusBar().showMessage(
            f"Practice run banked ${session.realized_pnl_cents / 100:.2f} and {session.score_delta} score.",
            5000,
        )

    def _execute_paper_candidate(self, profile: AppProfile, candidate: OpportunityCandidate) -> None:
        self._last_paper_run = self._paper_execution_engine.paper_trade(profile, candidate)
        if profile.lab_enabled and self._last_paper_run is not None:
            self._benchmark_audit_service(profile).audit_latest_run(profile.id, self._last_paper_run)
        active_profile = profile
        if not profile.first_run_completed:
            active_profile = profile.model_copy(
                update={
                    "first_run_completed": True,
                    "primary_mission": "Check Score, then repeat the record, scan, and practice loop with discipline.",
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
                    "primary_mission": "Practice gate passed. Keep score honest, then decide whether to stage shadow live.",
                }
            )
            self._profile_store.save_profile(active_profile)
            self._refresh_profiles(active_profile.id)
        self._refresh_portfolio_views()
        self._refresh_status_only()
        self.statusBar().showMessage("Practice run recorded.", 4000)

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

    def _ask_copilot(self) -> None:
        profile = self._current_profile()
        question = self.learn_tab.prompt_edit.toPlainText().strip()
        if not question:
            QMessageBox.information(self, "Ask Copilot", "Enter a question for Copilot first.")
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
        score_snapshot = self._score_service.snapshot(profile)
        unlocks = self._unlock_track_service.unlocks(profile, score_snapshot) if profile is not None else []
        registry_entries = (
            self._bot_registry_service.entries(profile, score_snapshot, unlocks) if profile is not None else []
        )
        provider_config = self.learn_tab.provider_config()
        provider_api_key = self.learn_tab.provider_api_key()
        session = self._assistant_service.answer(
            question=question,
            skill_id=self.learn_tab.requested_skill(),
            profile=profile,
            candidates=self._latest_candidates,
            selected_candidate=self._selected_candidate(),
            registry_entries=registry_entries,
            checklist=checklist,
            portfolio_summary=summary,
            diagnostics_summary=self.diagnostics_tab.text.toPlainText(),
            provider_config=provider_config,
            provider_api_key=provider_api_key,
        )
        self._pending_copilot_draft = session.draft
        self.learn_tab.set_response(session)
        self.learn_tab.clear_requested_skill()

    def _ask_coach(self) -> None:
        self._ask_copilot()

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
            "locked": "Profile returned to the fully locked practice-first posture.",
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

    def _save_benchmark_key(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        current_value = self._credential_vault.load(profile.id, "financial_benchmark").get("api_key", "")
        api_key, accepted = QInputDialog.getText(
            self,
            "Benchmark key",
            "Paste the rotated financial benchmark API key.",
            QLineEdit.EchoMode.Password,
            current_value,
        )
        if not accepted:
            return
        result = self._credential_vault.save(
            profile.id,
            "financial_benchmark",
            {"provider_name": "Financial Datasets", "api_key": api_key},
        )
        if not result.ok:
            QMessageBox.warning(self, "Benchmark key", result.message)
            return
        self._refresh_all_views()
        self.statusBar().showMessage("Benchmark key stored locally in the OS keychain.", 5000)

    def _save_benchmark_mapping(self) -> None:
        profile = self._current_profile()
        if profile is None:
            return
        market_slug = self.lab_tab.market_slug_combo.currentText().strip()
        symbol = self.lab_tab.symbol_edit.text().strip().upper()
        if not market_slug or not symbol:
            QMessageBox.information(self, "Benchmark mapping", "Choose a market slug and a benchmark symbol first.")
            return
        self._benchmark_link_service(profile).save_manual_link(
            profile_id=profile.id,
            market_slug=market_slug,
            symbol=symbol,
            instrument_type=cast(BenchmarkInstrumentType, self.lab_tab.instrument_type_combo.currentData()),
            interval_preference=cast(BenchmarkInterval, self.lab_tab.interval_combo.currentData()),
            notes=self.lab_tab.notes_edit.text(),
        )
        self._refresh_all_views()
        self.statusBar().showMessage(f"Saved benchmark link {market_slug} -> {symbol}.", 5000)

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
            self.tabs.insertTab(4, self.lab_tab, "Lab")
        if not should_show and tab_index >= 0:
            self.tabs.removeTab(tab_index)

    def _sync_startup_manager(self) -> None:
        if not self._startup_manager.supported():
            return
        should_enable = any(profile.auto_start for profile in self._profile_store.list_profiles())
        self._startup_manager.set_enabled(should_enable)

    def _sync_shell_state(self, profile: AppProfile | None, status: EngineStatus, candidate_count: int) -> None:
        if profile is None:
            self.shell.header.set_machine_state(
                cart_value="No profile",
                cart_tone="warning",
                data_value="Idle",
                data_tone="idle",
                safe_value="Locked",
                safe_tone="locked",
                lab_value="Off",
                lab_tone="idle",
                hint="Set up or import a profile, then run the recorder.",
            )
            self.shell.overlay_host.show_state(
                "First launch",
                "Set up or import a profile, then run the recorder to begin the practice-first loop.",
                "warning",
            )
            return
        has_data = status.summary is not None and (status.summary.raw_messages > 0 or status.summary.book_snapshots > 0)
        data_value = "Sync"
        data_tone = "warning"
        hint = "Run recorder, scan routes, keep practice first."
        if status.state == "failed":
            data_value = "Fault"
            data_tone = "error"
            hint = "Review diagnostics before retrying recorder boot."
        elif status.state == "running":
            data_value = "Live"
            data_tone = "active"
            hint = "Recorder is capturing local books now."
        elif candidate_count > 0:
            data_value = "Route"
            data_tone = "success"
            hint = "A route is staged. Start a practice run."
        elif has_data:
            data_value = "Buffered"
            data_tone = "success"
            hint = "Local sample ready. Refresh scanner and stage a route."
        self.shell.header.set_machine_state(
            cart_value=profile.display_name[:16],
            cart_tone="active",
            data_value=data_value,
            data_tone=data_tone,
            safe_value="Locked" if profile.live_mode == "locked" else profile.live_mode,
            safe_tone="locked" if profile.live_mode == "locked" else "warning",
            lab_value="On" if profile.lab_enabled else "Off",
            lab_tone="warning" if profile.lab_enabled else "idle",
            hint=hint,
        )
        if status.state == "failed":
            self.shell.overlay_host.show_state(
                "Recorder error",
                status.last_error or status.last_message,
                "error",
            )
            return
        if status.state == "running":
            self.shell.overlay_host.show_state(
                "Recorder running",
                "Capturing local Polymarket books. Wait for counts, then refresh scan.",
                "active",
            )
            return
        if candidate_count > 0:
            self.shell.overlay_host.show_state(
                "Practice ready",
                "A staged route is ready. Start a practice run before thinking about live controls.",
                "active",
            )
            return
        if has_data and not profile.first_run_completed:
            self.shell.overlay_host.show_state(
                "Scanner waiting",
                "Local data is ready. Refresh the scanner and stage the first bot route.",
                "warning",
            )
            return
        self.shell.overlay_host.clear()

    @staticmethod
    def _open_url(url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    @staticmethod
    def _open_local(path: Path) -> None:
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
