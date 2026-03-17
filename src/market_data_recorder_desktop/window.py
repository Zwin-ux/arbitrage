from __future__ import annotations

import logging
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
    AppProfile,
    AssistantSession,
    BenchmarkAudit,
    BenchmarkInterval,
    BenchmarkInstrumentType,
    BotConfig,
    BotRegistryEntry,
    BotSlot,
    CapabilityState,
    ConnectorLoadout,
    CredentialStatus,
    EngineStatus,
    ExperimentalLiveStatus,
    LiveUnlockChecklist,
    OpportunityCandidate,
    PaperBotEvent,
    PaperBotSession,
    PaperRunResult,
    PortfolioSnapshot,
    PortfolioSummary,
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
        self.next_step_label = QLabel("Create a profile, equip Polymarket, then boot the recorder.")
        self.next_step_label.setWordWrap(True)
        layout.addWidget(self.safe_state_label)

        signal_row = QHBoxLayout()
        signal_row.setSpacing(8)
        self.paper_state_badge = _LegacySignalBadge("Paper mode")
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
        self.score_label = QLabel("Paper score: waiting")
        self.score_label.setObjectName("heroText")
        self.score_label.setWordWrap(True)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        mission_layout.addWidget(self.mission_label, 1)
        mission_layout.addWidget(self.score_label, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(mission_group)

        action_group = QGroupBox("Primary action")
        action_group.setProperty("panelTone", "normal")
        action_layout = QVBoxLayout(action_group)
        self.primary_action_hint = QLabel("Boot recorder is the main action. The rest unlocks after the first sample lands.")
        self.primary_action_hint.setObjectName("heroText")
        self.primary_action_hint.setWordWrap(True)
        action_layout.addWidget(self.primary_action_hint)

        primary_action_row = QHBoxLayout()
        primary_action_row.setSpacing(10)
        self.start_button = QPushButton("Boot recorder")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("buttonRole", "secondary")
        primary_action_row.addWidget(self.start_button)
        primary_action_row.addWidget(self.stop_button)
        primary_action_row.addStretch(1)
        action_layout.addLayout(primary_action_row)

        self.secondary_actions_hint = QLabel("Replay, Verify, Scan edge, and Paper route unlock after a recorder pass.")
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
        self.scan_button = QPushButton("Scan edge")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Paper route")
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
        self.setup_progress_label = QLabel("Setup checklist")
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
        self.open_setup_button = QPushButton("Open guided setup")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("View trust docs")
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
            self.goal_label.setText("Create your first loadout")
            self.engine_label.setText(status.state.title())
            self.data_label.setText("No database yet")
            self.risk_label.setText("No risk policy")
            self.warning_label.setText("No warnings")
            self.safe_state_label.setText("System status")
            self.paper_state_badge.set_state("active", tone="active")
            self.live_state_badge.set_state("locked", tone="locked")
            self.lab_state_badge.set_state("offline", tone="idle")
            self.next_step_label.setText("Create a profile, equip Polymarket, then boot the recorder.")
            self.mission_label.setText("Equip -> Record -> Inspect")
            self.score_label.setText("Paper score: waiting")
            self.primary_action_hint.setText("Create a profile first. Boot recorder becomes available after a loadout exists.")
            self.setup_progress_label.setText("Setup checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Create first profile."),
                        ("WAIT", "Equip Polymarket and one strategy module."),
                        ("WAIT", "Boot recorder after the loadout is saved."),
                    ]
                )
            )
            self.loop_label.setText("Milestones: 0/4 complete")
            self.loop_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Equip loadout."),
                        ("WAIT", "Record local sample."),
                        ("WAIT", "Inspect scanner route."),
                        ("WAIT", "Land first paper run."),
                    ]
                )
            )
            self.open_setup_button.setText("Create first profile")
            self.secondary_actions_hint.setText(
                "Replay, Verify, Scan edge, and Paper route unlock after the first recorder pass."
            )
            self._set_telemetry(
                connection_lines=["No active venue connections."],
                system_lines=[
                    "Recorder: blocked until a loadout exists.",
                    "Scanner: waiting for recorder data.",
                    "Paper route: waiting for a viable route.",
                ],
            )
            self.recorder_tile.set_state("blocked", "Equip a loadout before recorder boot is available.", tone="locked")
            self.scanner_tile.set_state("waiting", "Scanner unlocks after local book capture starts.", tone="idle")
            self.route_tile.set_state("empty", "No route can be priced until scanner data exists.", tone="idle")
            self.system_log.setPlainText(
                "\n".join(
                    [
                        "[SYS] No active profile loaded.",
                        "[REC] Recorder offline until a Polymarket loadout exists.",
                        "[SCAN] Waiting for first local book sample.",
                        "[ROUTE] Paper route stays dark until the first clean scan lands.",
                    ]
                )
            )
            self._set_action_button(
                self.start_button,
                enabled=False,
                label="Boot recorder",
                reason="Create a guided profile first.",
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
                label="Scan edge",
                reason="Recorder data must land first.",
            )
            self._set_action_button(
                self.paper_button,
                enabled=False,
                label="Paper route",
                reason="Scanner needs a route first.",
            )
            self._set_secondary_tools_visibility(
                False,
                "Replay, Verify, Scan edge, and Paper route unlock after the first recorder pass.",
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
            self.next_step_label.setText("Save a loadout with Polymarket and one strategy module.")
            self.primary_action_hint.setText("Loadout is incomplete. Save it before trying to boot the recorder.")
        elif is_running:
            self.next_step_label.setText("Recorder is running. Let one clean sample finish before scanning.")
            self.primary_action_hint.setText("Boot recorder is active. Stop only if you need to abort this pass.")
        elif not has_data:
            self.next_step_label.setText("Boot recorder so Superior has local books to inspect.")
            self.primary_action_hint.setText("Boot recorder first. Secondary tools stay hidden until local data exists.")
        elif not score_ready:
            self.next_step_label.setText("Scan one route and paper it to light up the score board.")
            self.primary_action_hint.setText("Recorder is ready. Use the unlocked tools below to inspect and test routes.")
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            self.next_step_label.setText(
                "Keep scoring in paper mode or stage shadow live if you want a dry run."
            )
            self.primary_action_hint.setText("Recorder is stable. Use the unlocked tools to keep paper performance honest.")
        elif checklist is not None and checklist.outstanding:
            self.next_step_label.setText("Keep the paper loop healthy. Live-gate items are optional.")
            self.primary_action_hint.setText("Recorder is stable. Use replay, verify, and scan to inspect weak spots.")
        else:
            self.next_step_label.setText("Keep recorder data healthy and grow paper score with discipline.")
            self.primary_action_hint.setText("Recorder is stable. Keep using the unlocked tools to inspect routes and verify data.")
        self.brand_label.setText(profile.brand_name)
        self.profile_label.setText(profile.display_name)
        self.goal_label.setText(profile.primary_goal.replace("_", " ").title())
        self.engine_label.setText(f"{status.state.title()} - {status.last_message}")
        self.risk_label.setText(profile.risk_policy_id.title())
        self.mission_label.setText(profile.primary_mission)
        if score_snapshot.total_runs:
            self.score_label.setText(
                f"Paper score ${score_snapshot.paper_realized_pnl_cents / 100:.2f} | "
                f"Runs {score_snapshot.completed_runs} | Hit rate {score_snapshot.hit_rate:.1f}%"
            )
        else:
            self.score_label.setText("Paper score: waiting")
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
                "Equip loadout",
                loadout_ready,
                "Polymarket and one strategy module are equipped."
                if loadout_ready
                else "Equip Polymarket and one strategy module.",
            ),
            (
                "Record local sample",
                has_data,
                "Local recorder data is ready for the scanner."
                if has_data
                else "Boot recorder and wait for books.",
            ),
            (
                "Inspect scanner route",
                scanner_ready,
                "Scanner explanations are ready."
                if scanner_ready
                else "Recorder data has to land first.",
            ),
            (
                "Earn paper score",
                score_ready,
                "Paper score is live."
                if score_ready
                else "Run one paper route.",
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
        self.open_setup_button.setText("Edit setup")
        if profile.live_unlocked:
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Recorder, scanner, and paper score are in place."),
                        ("NEXT", "Revisit loadout only when changing scope."),
                        ("WAIT", "Keep live execution optional."),
                    ]
                )
            )
        elif is_running:
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Recorder is running."),
                        ("NEXT", "Wait for message and book counts."),
                        ("WAIT", "Refresh scan when the pass completes."),
                        ("WAIT", "Paper the top route after scan."),
                    ]
                )
            )
        elif not has_data:
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("NEXT", "Boot recorder."),
                        ("WAIT", "Wait for message and book counts."),
                        ("WAIT", "Scan edge, then paper one route."),
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
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                f"{outstanding}\n[ ] Keep using paper mode while these stay open."
            )
        elif profile.live_mode == "shadow":
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Shadow live is staged with real orders still off."),
                        ("NEXT", "Keep scanning and papering so score stays honest."),
                        ("WAIT", "Use Scanner preview before thinking about micro-live."),
                        ("WAIT", "Only arm micro-live after diagnostics stay clean."),
                    ]
                )
            )
        elif profile.live_mode in {"micro", "experimental"}:
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Experimental live is armed."),
                        ("NEXT", "Use Scanner preview before each candidate."),
                        ("WAIT", "Keep loadout scope narrow."),
                        ("WAIT", "Reset to locked if diagnostics degrade."),
                    ]
                )
            )
        else:
            self.setup_progress_label.setText("Checklist")
            self.setup_steps_label.setText(
                self._format_checklist(
                    [
                        ("DONE", "Local recorder data is ready."),
                        ("NEXT", "Scan edge for the newest candidates."),
                        ("WAIT", "Paper the top opportunity."),
                        ("WAIT", "Edit loadout only when scope changes."),
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
            self.recorder_tile.set_state("idle", "Loadout is armed. Boot the recorder for a first pass.", tone="warning")
        else:
            self.recorder_tile.set_state("blocked", "Polymarket and a strategy module are required first.", tone="locked")
        if scanner_ready and candidate_count > 0:
            self.scanner_tile.set_state("routes found", f"{candidate_count} candidate routes are cached locally.", tone="active")
        elif scanner_ready:
            self.scanner_tile.set_state("ready", "Scanner is armed and waiting for a refresh.", tone="warning")
        elif has_data:
            self.scanner_tile.set_state("standby", "Local books exist, but the scanner still needs a refresh.", tone="warning")
        else:
            self.scanner_tile.set_state("waiting", "Recorder data has to land before scanner routes exist.", tone="locked")
        if score_ready:
            self.route_tile.set_state("paper scored", f"{score_snapshot.completed_runs} paper runs have landed in the score ledger.", tone="active")
        elif candidate_count > 0:
            self.route_tile.set_state("route ready", "A candidate is available. Paper it to light the score board.", tone="warning")
        else:
            self.route_tile.set_state("empty", "No top route is staged yet.", tone="locked")
        self.system_log.setPlainText(
            "\n".join(
                [
                    f"[SYS] Profile online: {profile.display_name}",
                    f"[REC] {self.recorder_tile.value_label.text()} :: {self.recorder_tile.detail_label.text()}",
                    f"[SCAN] {self.scanner_tile.value_label.text()} :: {self.scanner_tile.detail_label.text()}",
                    f"[ROUTE] {self.route_tile.value_label.text()} :: {self.route_tile.detail_label.text()}",
                    f"[SAFE] PAPER=ACTIVE | LIVE={profile.live_mode.upper()} | LAB={'ON' if profile.lab_enabled else 'OFF'}",
                ]
            )
        )
        self._set_action_button(
            self.start_button,
            enabled=not is_running,
            label="Boot recorder",
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
            label="Scan edge",
            reason="Recorder data must land before the scanner becomes useful.",
        )
        self._set_action_button(
            self.paper_button,
            enabled=candidate_count > 0,
            label="Paper route",
            reason="Refresh scan first so a viable route exists.",
        )
        self._set_secondary_tools_visibility(
            tools_visible,
            "Replay and Verify are available. Scan edge and Paper route still need usable local data."
            if tools_visible and not has_data
            else (
                "Replay, Verify, Scan edge, and Paper route are unlocked."
                if has_data
                else "Replay, Verify, Scan edge, and Paper route unlock after the first recorder pass."
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
        self.header_label = QLabel("Bot Bay")
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
        self.coach_checkbox = QCheckBox("Coach link")
        for checkbox in (self.polymarket_checkbox, self.kalshi_checkbox, self.coach_checkbox):
            connectors_layout.addWidget(checkbox)
        loadout_row.addWidget(connectors_group, 0, Qt.AlignmentFlag.AlignTop)

        modules_group = QGroupBox("Modules")
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
        self.save_button = QPushButton("Save loadout")
        self.refresh_button = QPushButton("Refresh status")
        self.refresh_button.setProperty("buttonRole", "secondary")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.refresh_button)
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

        registry_group = QGroupBox("Bot garage")
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

        unlock_group = QGroupBox("Unlock track")
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
            self.header_label.setText("Create a profile to equip your first connector.")
            self.state_text.setPlainText("No loadout yet.")
            self.bot_bay_text.setPlainText("No bot slots yet.")
            self.registry_text.setPlainText("No starter registry yet.")
            self.unlock_text.setPlainText("No unlock track yet.")
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
            return
        self.header_label.setText(f"{profile.display_name} bot bay")
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
        lines = [f"MISSION    {profile.primary_mission}", "", "CONNECTORS"]
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
        bay_lines = [
            "SCORE ATTACK BOT BAY",
            "",
        ]
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
        registry_lines = ["BOT GARAGE", ""]
        self.fork_source_combo.clear()
        if not registry_entries:
            registry_lines.append("No visible bot recipes yet. Equip a module to surface starter bots.")
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
        unlock_lines = ["UNLOCK TRACK", ""]
        if not unlocks:
            unlock_lines.append("No unlocks loaded yet.")
        for unlock in unlocks:
            status = "ONLINE" if unlock.unlocked else "LOCKED"
            unlock_lines.append(f"{status:<7} {unlock.label}")
            unlock_lines.append(f"  {unlock.detail}")
        self.unlock_text.setPlainText("\n".join(unlock_lines))


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
        layout.setSpacing(10)
        self.header_label = QLabel(
            "Scanner reads local books, stages routes for the bot bay, and explains whether each route survives cost deductions."
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
        self.paper_button = QPushButton("Start selected session")
        self.live_preview_button = QPushButton("Preview live lock")
        actions.addWidget(self.refresh_button)
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
            "TOP EDGE   +0 bps\n"
            "QUALITY    000"
        )
        self.route_board_text.setPlainText(
            "TACTICAL BOARD\n\n"
            "No staged routes yet.\n"
            "Recorder data must land before the radar can stage anything truthful."
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
                        f"TOP EDGE   {top_candidate.net_edge_bps:+d} bps",
                        f"QUALITY    {top_candidate.opportunity_quality_score:03d}",
                        f"FOCUS      {top_candidate.strategy_label}",
                    ]
                )
            )
            board_lines = ["TACTICAL BOARD", ""]
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
                "TOP EDGE   +0 bps\n"
                "QUALITY    000"
            )
            self.route_board_text.setPlainText(
                "TACTICAL BOARD\n\n"
                "No staged routes yet.\n"
                "1. Record a local sample.\n"
                "2. Refresh Scanner.\n"
                "3. Wait for a route that survives net-edge deductions."
            )
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
        route_state = "READY TO PAPER" if candidate.net_edge_bps > 0 else "HOLD / SKIP"
        self.details_text.setPlainText(
            "\n".join(
                [
                    "TACTICAL READOUT",
                    "",
                    f"Route: {candidate.strategy_label}",
                    f"State: {route_state}",
                    f"Machine status: {candidate.status}",
                    f"Gross edge: {candidate.gross_edge_bps} bps",
                    f"Net edge: {candidate.net_edge_bps} bps",
                    f"Quality score: {candidate.opportunity_quality_score}",
                    f"Venues: {', '.join(candidate.venues)}",
                    f"Paper stake: ${candidate.recommended_stake_cents / 100:.2f}",
                    (
                        "Next move: start a paper session and bank the result into Score."
                        if candidate.net_edge_bps > 0
                        else "Next move: hold this route and keep the radar scanning for a cleaner edge."
                    ),
                    "",
                    "WHY THE RADAR FLAGGED IT",
                    candidate.explanation.summary,
                    "",
                    "WHAT MATCHED",
                    *[f"- {item}" for item in matched_contracts],
                    "",
                    "ASSUMPTIONS STILL IN PLAY",
                    *[f"- {item}" for item in assumptions],
                    "",
                    "DEDUCTIONS FROM GROSS EDGE",
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
            "Guaranteed arbitrage opportunities found by reading stored local market books.\n"
            "A buy-all-outcomes route profits when the sum of all asks is below $1.\n"
            "A sell-all-outcomes route profits when the sum of all bids exceeds $1."
        )
        self.header_label.setObjectName("heroTitle")
        self.header_label.setWordWrap(True)
        layout.addWidget(self.header_label)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Min edge (e.g. 0.01):"))
        self.min_edge_input = QLineEdit()
        self.min_edge_input.setPlaceholderText("0")
        self.min_edge_input.setMaximumWidth(120)
        filter_row.addWidget(self.min_edge_input)
        self.refresh_button = QPushButton("Refresh arbitrage")
        filter_row.addWidget(self.refresh_button)
        filter_row.addStretch(1)
        layout.addLayout(filter_row)

        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        opps_group = QGroupBox("Arbitrage opportunities")
        opps_group.setProperty("panelTone", "subtle")
        opps_layout = QVBoxLayout(opps_group)
        self.opportunity_list = QListWidget()
        self.opportunity_list.setMaximumWidth(380)
        opps_layout.addWidget(self.opportunity_list)

        details_group = QGroupBox("Opportunity detail")
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
            "No data yet.\n\nRecord local market books first, then click 'Refresh arbitrage'."
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
                "No guaranteed arbitrage found with the current min-edge filter.\n\n"
                "Try lowering the min edge to '0' and refreshing, or record more local data."
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
            "Next step: paper this route in the Paper Runs tab to validate fills before any live use.",
        ]
        self.details_text.setPlainText("\n".join(lines))


class PaperBotsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel("Session feed")
        self.header_label.setWordWrap(True)
        self.header_label.setObjectName("heroTitle")
        layout.addWidget(self.header_label)
        actions = QHBoxLayout()
        self.run_top_button = QPushButton("Start session")
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
            self.runs_list.addItem("No paper runs yet. Record -> scan -> start session.")
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
                "No active session yet.\n"
                "Record a local sample, then start a paper session."
            )
            self.session_summary_text.setPlainText(
                "SESSION SUMMARY\n\n"
                "No session has banked score yet."
            )
            self.decision_trace_text.setPlainText(
                decision_trace
                or "TACTICAL TRACE\n\nNo decision trace yet.\nStart a paper session to inspect bot decisions."
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
                        "SESSION SUMMARY",
                        "",
                        f"Session ID: {session.session_id}",
                        f"State: {session.state}",
                        f"Paper PnL: ${session.realized_pnl_cents / 100:.2f}",
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
                                f"edge delta {audit.edge_vs_benchmark_bps} bps"
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
        self.summary_label = QLabel("Paper Score waiting for first route | Live Score locked")
        self.summary_label.setObjectName("heroTitle")
        self.summary_label.setWordWrap(True)
        self.mode_label = QLabel(
            "Paper score is the main progression system in Superior. Live score stays locked and empty."
        )
        self.mode_label.setWordWrap(True)
        self.portfolio_text = QPlainTextEdit()
        self.portfolio_text.setReadOnly(True)
        self.detail_text = QPlainTextEdit()
        self.detail_text.setReadOnly(True)
        self.ledger_text = QPlainTextEdit()
        self.ledger_text.setReadOnly(True)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.mode_label)
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
            self.summary_label.setText("Paper Score waiting for first route | Live Score locked")
            self.portfolio_text.setPlainText(
                "PORTFOLIO SCORE\n\n"
                "No paper sessions banked yet.\n"
                "Start with one local recorder pass, then arm a starter bot."
            )
            self.detail_text.setPlainText(
                "Paper score is the main loop in Superior v1.\n\n"
                "1. Record a local sample.\n"
                "2. Stage routes in Scanner.\n"
                "3. Start a paper session.\n"
                "4. Come back here for the first score update."
            )
            self.ledger_text.setPlainText(
                "No ledger entries yet.\n\n"
                "Your first paper session will create stake, realized-PnL, and session-grade history here."
            )
            if lab_enabled:
                self.ledger_text.appendPlainText(
                    "\n\nBENCHMARK AUDIT\n\nNo benchmark coverage yet. Save a Lab mapping if you want external reference checks."
                )
            return
        self.summary_label.setText(
            f"Paper Score ${snapshot.paper_realized_pnl_cents / 100:.2f} | "
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
            f"Total paper runs: {snapshot.total_runs}",
            f"Completed runs: {snapshot.completed_runs}",
            f"Hit rate: {snapshot.hit_rate:.1f}%",
            f"Average expected edge: {snapshot.average_expected_edge_bps} bps",
            f"Average realized edge: {snapshot.average_realized_edge_bps} bps",
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
        self._arb_service = arbitrage_service or ArbitrageService()
        self._benchmark_api_key_env_override = resolve_benchmark_api_key()
        self._profiles: list[AppProfile] = []
        self._latest_candidates: list[OpportunityCandidate] = []
        self._latest_arb_opportunities: list[ArbitrageOpportunity] = []
        self._last_paper_run: PaperRunResult | None = None
        self._last_session: PaperBotSession | None = None
        self._previous_state = "idle"
        self._home_primary_action_mode = "recorder"

        self.setWindowTitle("Superior")
        self.resize(1260, 880)

        self.home_tab = HangarHomeTab()
        self.loadout_tab = LoadoutTab()
        self.learn_tab = LearnTab()
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
        self.tabs.addTab(self.home_tab, "Hangar")
        self.tabs.addTab(self.loadout_tab, "Loadout")
        self.tabs.addTab(self.scanner_tab, "Scanner")
        self.tabs.addTab(self.arb_tab, "Arbitrage")
        self.tabs.addTab(self.paper_bots_tab, "Paper Runs")
        self.tabs.addTab(self.score_tab, "Score")
        self.tabs.addTab(self.diagnostics_tab, "Diagnostics")
        self.tabs.addTab(self.learn_tab, "Learn")
        self.tabs.addTab(self.live_unlock_tab, "Live Gate")
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

        self.learn_tab.ask_button.clicked.connect(self._ask_coach)

        self.scanner_tab.refresh_button.clicked.connect(self._refresh_scanner)
        self.scanner_tab.paper_button.clicked.connect(self._start_selected_session)
        self.scanner_tab.live_preview_button.clicked.connect(self._preview_live_lock)
        self.scanner_tab.candidate_list.currentItemChanged.connect(self._on_candidate_changed)

        self.arb_tab.refresh_button.clicked.connect(self._refresh_arbitrage)
        self.arb_tab.opportunity_list.currentItemChanged.connect(self._on_arb_opportunity_changed)

        self.paper_bots_tab.run_top_button.clicked.connect(self._start_paper_session)
        self.paper_bots_tab.refresh_button.clicked.connect(self._refresh_portfolio_views)

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

    def _refresh_status_only(self) -> None:
        profile = self._current_profile()
        status = self._controller.status(profile)
        connections = self._venue_connections(profile)
        credential_statuses = self._credential_statuses(profile)
        score_snapshot = self._score_service.snapshot(profile)
        portfolio_snapshot = self._portfolio_engine.snapshot(profile)
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
                f"{profile_name} is ready. Boot recorder to start the first paper-safe loop.",
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
            self.home_tab.start_button.setText("Start session")
            self.home_tab.primary_action_hint.setText(
                "The machine is primed. Start a paper session to arm the bot bay and bank score."
            )
        elif has_data:
            self.home_tab.start_button.setText("Boot recorder")
            self.home_tab.primary_action_hint.setText(
                "Local books are ready. Refresh scanner until a clean route stages for the first bot slot."
            )
        else:
            self.home_tab.start_button.setText("Boot recorder")
            self.home_tab.primary_action_hint.setText(
                "Boot recorder is the only action that matters until the first local market sample lands."
            )
        self.home_tab.set_secondary_actions_visible(
            has_data or bool(self._latest_candidates) or score_snapshot.completed_runs > 0 or status.state in {"completed", "failed"}
        )
        self.home_tab.scan_button.setText("Scan routes" if has_data else "Scan routes [locked]")
        self.home_tab.paper_button.setText("Start session" if session_ready else "Start session [locked]")

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
            updated.primary_mission = "Record your first local sample, arm the starter bot, and bank your first score."
        self._profile_store.save_profile(updated)
        self._refresh_profiles(updated.id)
        self._refresh_all_views()
        self.statusBar().showMessage("Loadout saved.", 4000)

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
        self.statusBar().showMessage(f"Forked {recipe.label} into the local bot garage.", 5000)

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
            QMessageBox.information(self, "Choose a candidate", "Pick a scanner result before paper-testing it.")
            return
        self._start_paper_session(preferred_candidates=[candidate])

    def _start_paper_session(self, _checked: bool = False, preferred_candidates: list[OpportunityCandidate] | None = None) -> None:
        del _checked
        profile = self._current_profile()
        if profile is None:
            QMessageBox.information(self, "Choose a profile", "Create or choose a profile before starting a session.")
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
                    "primary_mission": "Keep the machine honest: record, stage routes, start sessions, and grow paper score deliberately.",
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
                    "primary_mission": "Paper gate passed. Keep score pressure steady before touching shadow-live previews.",
                }
            )
            self._profile_store.save_profile(active_profile)
            self._refresh_profiles(active_profile.id)
        self._refresh_portfolio_views()
        self._refresh_status_only()
        self.statusBar().showMessage(
            f"Paper session banked ${session.realized_pnl_cents / 100:.2f} and {session.score_delta} score.",
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
                cart_value="No cart",
                cart_tone="warning",
                data_value="Idle",
                data_tone="idle",
                safe_value="Paper",
                safe_tone="active",
                lab_value="Off",
                lab_tone="idle",
                hint="Create a profile, then boot recorder.",
            )
            self.shell.overlay_host.show_state(
                "First launch",
                "Create a guided profile, then boot recorder to begin the paper-first loop.",
                "warning",
            )
            return
        has_data = status.summary is not None and (status.summary.raw_messages > 0 or status.summary.book_snapshots > 0)
        data_value = "Sync"
        data_tone = "warning"
        hint = "Boot recorder, scan routes, keep paper first."
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
            hint = "A route is staged. Start a paper session."
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
                "Session ready",
                "A staged route is ready. Start a paper session before thinking about live controls.",
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
