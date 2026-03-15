from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from market_data_recorder_desktop.app_types import (
    AppProfile,
    CapabilityState,
    ChecklistItem,
    EngineStatus,
    HangarViewModel,
    LiveUnlockChecklist,
    MachineStatus,
    ScoreSnapshot,
    SemanticStateColor,
    VenueConnection,
)
from .primitives import SignalBadge, StateCard, StatCell


class MissionControlHeader(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.title_label = QLabel("Hangar mission control")
        self.title_label.setObjectName("heroTitle")
        self.next_step_label = QLabel("Boot recorder to build the first local sample.")
        self.next_step_label.setObjectName("heroText")
        self.next_step_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        self.paper_state_badge = SignalBadge("Paper mode")
        self.live_state_badge = SignalBadge("Live gate")
        self.lab_state_badge = SignalBadge("Lab")
        badge_row.addWidget(self.paper_state_badge)
        badge_row.addWidget(self.live_state_badge)
        badge_row.addWidget(self.lab_state_badge)
        badge_row.addStretch(1)
        layout.addLayout(badge_row)
        layout.addWidget(self.next_step_label)

        mission_group = QGroupBox("Mission strip")
        mission_group.setProperty("panelTone", "primary")
        mission_layout = QHBoxLayout(mission_group)
        mission_layout.setSpacing(16)
        self.mission_label = QLabel("Equip Polymarket, record a sample, inspect a route.")
        self.mission_label.setObjectName("heroText")
        self.mission_label.setWordWrap(True)
        self.score_label = QLabel("Paper score waiting for first run")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.score_label.setObjectName("heroText")
        self.score_label.setWordWrap(True)
        mission_layout.addWidget(self.mission_label, 1)
        mission_layout.addWidget(self.score_label, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(mission_group)


class ChecklistPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("First pass checklist")
        self.setProperty("panelTone", "subtle")
        layout = QVBoxLayout(self)
        self.setup_progress_label = QLabel("Recorder-first setup")
        self.setup_progress_label.setObjectName("heroText")
        self.setup_steps_label = QLabel()
        self.setup_steps_label.setWordWrap(True)
        self.setup_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.open_setup_button = QPushButton("Open guided setup")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("View trust docs")
        self.view_docs_button.setProperty("buttonRole", "ghost")
        button_row = QHBoxLayout()
        button_row.addWidget(self.open_setup_button)
        button_row.addWidget(self.view_docs_button)
        button_row.addStretch(1)
        layout.addWidget(self.setup_progress_label)
        layout.addWidget(self.setup_steps_label)
        layout.addLayout(button_row)


class ProgressPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Golden path")
        self.setProperty("panelTone", "subtle")
        layout = QVBoxLayout(self)
        self.loop_label = QLabel("Milestones: 0/4 complete")
        self.loop_label.setObjectName("heroText")
        self.loop_meter = QProgressBar()
        self.loop_meter.setRange(0, 4)
        self.loop_meter.setValue(0)
        self.loop_meter.setTextVisible(False)
        self.loop_meter.setFixedHeight(12)
        self.loop_steps_label = QLabel()
        self.loop_steps_label.setWordWrap(True)
        self.loop_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.loop_label)
        layout.addWidget(self.loop_meter)
        layout.addWidget(self.loop_steps_label)


class ActionBar(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Next action")
        self.setProperty("panelTone", "normal")
        layout = QVBoxLayout(self)
        self.primary_hint_label = QLabel(
            "Boot recorder is the only action that matters until the first local market sample lands."
        )
        self.primary_hint_label.setObjectName("heroText")
        self.primary_hint_label.setWordWrap(True)
        layout.addWidget(self.primary_hint_label)

        primary_row = QHBoxLayout()
        self.start_button = QPushButton("Boot recorder")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("buttonRole", "secondary")
        primary_row.addWidget(self.start_button)
        primary_row.addWidget(self.stop_button)
        primary_row.addStretch(1)
        layout.addLayout(primary_row)

        self.secondary_actions_widget = QWidget()
        secondary_row = QHBoxLayout(self.secondary_actions_widget)
        secondary_row.setContentsMargins(0, 0, 0, 0)
        secondary_row.setSpacing(8)
        self.replay_button = QPushButton("Replay")
        self.replay_button.setProperty("buttonRole", "secondary")
        self.verify_button = QPushButton("Verify")
        self.verify_button.setProperty("buttonRole", "secondary")
        self.scan_button = QPushButton("Scan edge")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Paper route")
        self.paper_button.setProperty("buttonRole", "secondary")
        for button in (self.replay_button, self.verify_button, self.scan_button, self.paper_button):
            secondary_row.addWidget(button)
        secondary_row.addStretch(1)
        self.secondary_actions_widget.hide()
        layout.addWidget(self.secondary_actions_widget)


class SystemConsole(QGroupBox):
    def __init__(self) -> None:
        super().__init__("System console")
        self.setProperty("panelTone", "normal")
        layout = QVBoxLayout(self)
        tile_row = QHBoxLayout()
        tile_row.setSpacing(8)
        self.recorder_tile = StateCard("Recorder")
        self.scanner_tile = StateCard("Scanner")
        self.route_tile = StateCard("Route")
        tile_row.addWidget(self.recorder_tile)
        tile_row.addWidget(self.scanner_tile)
        tile_row.addWidget(self.route_tile)
        layout.addLayout(tile_row)
        self.system_log = QPlainTextEdit()
        self.system_log.setReadOnly(True)
        self.system_log.setProperty("consoleRole", "system")
        self.system_log.setMaximumHeight(132)
        layout.addWidget(self.system_log)

    def apply_machine_statuses(self, statuses: list[MachineStatus]) -> None:
        cards = [self.recorder_tile, self.scanner_tile, self.route_tile]
        for card, status in zip(cards, statuses, strict=False):
            card.set_state(status.value, status.detail, tone=status.tone)


class TelemetryPanelGroup(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Telemetry")
        self.setProperty("panelTone", "ghost")
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        labels = ("Brand", "Profile", "Goal", "Recorder", "Data", "Risk preset", "Latest warning")
        self._cells: dict[str, StatCell] = {}
        for index, label in enumerate(labels):
            cell = StatCell(label)
            self._cells[label] = cell
            grid.addWidget(cell, index // 2, index % 2)
        layout.addLayout(grid)
        self.capability_text = QPlainTextEdit()
        self.capability_text.setReadOnly(True)
        self.capability_text.setProperty("consoleRole", "system")
        self.capability_text.setMaximumHeight(110)
        self.connections_text = QPlainTextEdit()
        self.connections_text.setReadOnly(True)
        self.connections_text.setProperty("consoleRole", "system")
        self.connections_text.setMaximumHeight(90)
        layout.addWidget(self.capability_text)
        layout.addWidget(self.connections_text)
        self.brand_label = self._cells["Brand"].value_label
        self.profile_label = self._cells["Profile"].value_label
        self.goal_label = self._cells["Goal"].value_label
        self.engine_label = self._cells["Recorder"].value_label
        self.data_label = self._cells["Data"].value_label
        self.risk_label = self._cells["Risk preset"].value_label
        self.warning_label = self._cells["Latest warning"].value_label

    def set_telemetry(self, stats: list[tuple[str, str, str, SemanticStateColor]]) -> None:
        for label, value, detail, tone in stats:
            if label in self._cells:
                self._cells[label].set_value(value, detail=detail, tone=tone)


class HomeTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        self.header = MissionControlHeader()
        self.action_bar = ActionBar()
        self.console = SystemConsole()
        self.checklist_panel = ChecklistPanel()
        self.progress_panel = ProgressPanel()
        self.telemetry_panel = TelemetryPanelGroup()

        self.safe_state_label = self.header.title_label
        self.next_step_label = self.header.next_step_label
        self.paper_state_badge = self.header.paper_state_badge
        self.live_state_badge = self.header.live_state_badge
        self.lab_state_badge = self.header.lab_state_badge
        self.mission_label = self.header.mission_label
        self.score_label = self.header.score_label

        self.primary_action_hint = self.action_bar.primary_hint_label
        self.start_button = self.action_bar.start_button
        self.stop_button = self.action_bar.stop_button
        self.secondary_actions_widget = self.action_bar.secondary_actions_widget
        self.replay_button = self.action_bar.replay_button
        self.verify_button = self.action_bar.verify_button
        self.scan_button = self.action_bar.scan_button
        self.paper_button = self.action_bar.paper_button

        self.recorder_tile = self.console.recorder_tile
        self.scanner_tile = self.console.scanner_tile
        self.route_tile = self.console.route_tile
        self.system_log = self.console.system_log

        self.setup_progress_label = self.checklist_panel.setup_progress_label
        self.setup_steps_label = self.checklist_panel.setup_steps_label
        self.open_setup_button = self.checklist_panel.open_setup_button
        self.view_docs_button = self.checklist_panel.view_docs_button

        self.loop_label = self.progress_panel.loop_label
        self.loop_steps_label = self.progress_panel.loop_steps_label

        self.brand_label = self.telemetry_panel.brand_label
        self.profile_label = self.telemetry_panel.profile_label
        self.goal_label = self.telemetry_panel.goal_label
        self.engine_label = self.telemetry_panel.engine_label
        self.data_label = self.telemetry_panel.data_label
        self.risk_label = self.telemetry_panel.risk_label
        self.warning_label = self.telemetry_panel.warning_label
        self.capability_text = self.telemetry_panel.capability_text
        self.connections_text = self.telemetry_panel.connections_text

        layout.addWidget(self.header)
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self.action_bar, 4)
        top_row.addWidget(self.console, 7)
        layout.addLayout(top_row)

        lower_row = QHBoxLayout()
        lower_row.setSpacing(12)
        lower_row.addWidget(self.checklist_panel, 4)
        lower_row.addWidget(self.progress_panel, 4)
        lower_row.addWidget(self.telemetry_panel, 5)
        layout.addLayout(lower_row)
        layout.addStretch(1)

    def apply_model(self, model: HangarViewModel) -> None:
        self.safe_state_label.setText(model.title)
        self.next_step_label.setText(model.next_step)
        badge_map = {
            "Paper mode": self.paper_state_badge,
            "Live gate": self.live_state_badge,
            "Lab": self.lab_state_badge,
        }
        for tile in model.status_tiles:
            badge = badge_map.get(tile.label)
            if badge is not None:
                badge.set_state(tile.value, tone=tile.tone)
        self.mission_label.setText(model.mission)
        self.score_label.setText(model.paper_score)
        self.primary_action_hint.setText(model.primary_action_hint)
        self.setup_progress_label.setText(model.checklist_title)
        self.setup_steps_label.setText(self._render_checklist(model.checklist))
        self.loop_label.setText(model.milestone_title)
        complete_count = sum(1 for item in model.milestones if item.complete)
        self.progress_panel.loop_meter.setValue(complete_count)
        self.loop_steps_label.setText(self._render_checklist(model.milestones))
        self.console.apply_machine_statuses(model.machine_statuses)
        self.system_log.setPlainText("\n".join(model.system_log))
        telemetry_rows = [(item.label, item.value, item.detail, item.tone) for item in model.telemetry_stats]
        self.telemetry_panel.set_telemetry(telemetry_rows)
        self.capability_text.setPlainText(self._render_status_rows(model.capability_rows))
        self.connections_text.setPlainText(self._render_status_rows(model.connector_rows))

    def set_secondary_actions_visible(self, visible: bool) -> None:
        self.secondary_actions_widget.setVisible(visible)

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
            model = HangarViewModel(
                next_step="Create a guided profile, equip Polymarket, and boot the recorder.",
                status_tiles=[
                    {"label": "Paper mode", "value": "active", "tone": "active"},
                    {"label": "Live gate", "value": "locked", "tone": "locked"},
                    {"label": "Lab", "value": "offline", "tone": "idle"},
                ],
                mission="Equip Polymarket, record a local sample, then arm the starter bot bay.",
                paper_score="Paper score waiting for first run",
                primary_action_hint="Boot recorder stays framed as the next move until the first local sample lands.",
                checklist_title="Setup checklist",
                checklist=[
                    ChecklistItem(id="profile", label="Create first profile.", current=True),
                    ChecklistItem(id="recorder", label="Boot recorder.", detail="Recorder stays blocked until a profile exists."),
                    ChecklistItem(
                        id="scan",
                        label="Start first session.",
                        detail="A session needs recorder data and at least one staged route.",
                    ),
                ],
                milestone_title="Golden path - 0/4 complete",
                milestones=[
                    ChecklistItem(id="loadout", label="Equip loadout", detail="Create a guided profile with Polymarket equipped."),
                    ChecklistItem(id="record", label="Record local sample", detail="Recorder remains idle until the profile exists."),
                    ChecklistItem(id="inspect", label="Stage session routes", detail="Scanner routes need a local sample first."),
                    ChecklistItem(id="score", label="Bank paper score", detail="Paper score lights up after the first session lands."),
                ],
                machine_statuses=[
                    MachineStatus(id="recorder", label="Recorder", value="blocked", detail="Create a profile to unlock recorder boot.", tone="locked"),
                    MachineStatus(id="scanner", label="Scanner", value="waiting", detail="Scanner is idle until local books exist.", tone="idle"),
                    MachineStatus(id="route", label="Bot bay", value="empty", detail="No bot can stage before scanner output exists.", tone="idle"),
                ],
                system_log=[
                    "[BOOT] No active profile loaded.",
                    "[REC] Recorder blocked until a profile exists.",
                    "[SCAN] Waiting for the first local sample.",
                    "[BOT] Paper score remains dark until the first session lands.",
                ],
                telemetry_stats=[
                    {"label": "Brand", "value": "Superior", "detail": "", "tone": "active"},
                    {"label": "Profile", "value": "No profile", "detail": "", "tone": "warning"},
                    {"label": "Goal", "value": "Guided setup", "detail": "", "tone": "warning"},
                    {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": "idle"},
                    {"label": "Data", "value": "No database", "detail": "", "tone": "idle"},
                    {"label": "Risk preset", "value": "Starter", "detail": "", "tone": "idle"},
                    {"label": "Latest warning", "value": "No warnings", "detail": "", "tone": "idle"},
                ],
                capability_rows=[
                    {"id": "recorder", "label": "Recorder", "value": "blocked", "detail": "Needs a profile and Polymarket.", "tone": "locked"},
                    {"id": "scanner", "label": "Scanner", "value": "blocked", "detail": "Needs recorder data.", "tone": "locked"},
                    {"id": "paper score", "label": "Paper score", "value": "blocked", "detail": "Needs first paper session.", "tone": "locked"},
                    {"id": "live gate", "label": "Live gate", "value": "locked", "detail": "Out of scope until paper progress exists.", "tone": "locked"},
                ],
                connector_rows=[
                    {"id": "polymarket", "label": "Polymarket", "value": "disabled", "detail": "Not equipped yet.", "tone": "warning"},
                    {"id": "kalshi", "label": "Kalshi", "value": "disabled", "detail": "Optional later.", "tone": "idle"},
                    {"id": "coach", "label": "Coach link", "value": "disabled", "detail": "Optional later.", "tone": "idle"},
                ],
            )
            self.apply_model(model)
            self.open_setup_button.setText("Create first profile")
            self._set_action_button(self.start_button, enabled=False, active_text="Boot recorder", inactive_text="Boot recorder [blocked]")
            self._set_action_button(self.stop_button, enabled=False, active_text="Stop", inactive_text="Stop [idle]")
            self._set_action_button(self.replay_button, enabled=False, active_text="Replay", inactive_text="Replay [locked]")
            self._set_action_button(self.verify_button, enabled=False, active_text="Verify", inactive_text="Verify [locked]")
            self._set_action_button(self.scan_button, enabled=False, active_text="Scan edge", inactive_text="Scan edge [locked]")
            self._set_action_button(self.paper_button, enabled=False, active_text="Paper route", inactive_text="Paper route [locked]")
            self.set_secondary_actions_visible(False)
            return

        summary = status.summary
        has_store = summary is not None
        has_data = False
        if summary is not None:
            has_data = summary.raw_messages > 0 or summary.book_snapshots > 0
        is_running = status.state == "running"
        scanner_ready = any(state.capability_id == "scanner" and state.ready for state in capability_states)
        has_data = has_data or scanner_ready or candidate_count > 0
        loadout_ready = "polymarket" in profile.equipped_connectors and bool(profile.equipped_modules)
        score_ready = score_snapshot.total_runs > 0
        if not loadout_ready:
            next_step = "Save a loadout with Polymarket and at least one strategy module."
        elif is_running:
            next_step = "Let the recorder finish a clean local sample, then refresh the scanner."
        elif not has_data:
            next_step = "Boot recorder so Superior can build the first local book sample."
        elif candidate_count > 0 and not score_ready:
            next_step = "Start a paper session so the starter bot can bank the first score."
        elif not score_ready:
            next_step = "Refresh Scanner until at least one route stages for the bot bay."
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            next_step = "Keep scoring in paper mode, or stage shadow live only when the checklist is clean."
        else:
            next_step = "Keep the recorder healthy and repeat the record, scan, and paper loop."

        checklist_items = [
            ChecklistItem(
                id="boot",
                label="Boot recorder.",
                detail="Build the first local sample from Polymarket books.",
                complete=has_data or is_running,
                current=loadout_ready and not (has_data or is_running),
            ),
            ChecklistItem(
                id="wait",
                label="Wait for raw message and book counts.",
                detail="Counts appear in telemetry once the recorder produces data.",
                complete=has_data,
                current=is_running,
            ),
            ChecklistItem(
                id="scan",
                label="Start a paper session.",
                detail="Arm the starter bot once scanner routes stage cleanly.",
                complete=scanner_ready,
                current=has_data and not scanner_ready,
            ),
        ]
        milestone_specs = [
            ("loadout", "Equip loadout", loadout_ready, "Polymarket and one strategy module are equipped."),
            ("record", "Record local sample", has_data, "Recorder has local data to work from."),
            ("inspect", "Stage session routes", scanner_ready, "Scanner can price explainable routes."),
            ("score", "Bank paper score", score_ready, "Paper ledger has at least one completed session."),
        ]
        first_current = False
        milestones: list[ChecklistItem] = []
        complete_count = 0
        for item_id, label, complete, detail in milestone_specs:
            if complete:
                complete_count += 1
            current = False
            if not complete and not first_current:
                current = True
                first_current = True
            milestones.append(
                ChecklistItem(id=item_id, label=label, detail=detail, complete=complete, current=current)
            )

        machine_statuses = [
            MachineStatus(
                id="recorder",
                label="Recorder",
                value="capturing" if is_running else ("ready" if has_data else ("idle" if loadout_ready else "blocked")),
                detail=(
                    f"{status.summary.raw_messages} messages / {status.summary.book_snapshots} books captured."
                    if status.summary is not None
                    else "No local data yet."
                ),
                tone="active" if is_running or has_data else ("warning" if loadout_ready else "locked"),
            ),
            MachineStatus(
                id="scanner",
                label="Scanner",
                value="routes found" if candidate_count > 0 else ("ready" if scanner_ready else ("standby" if has_data else "waiting")),
                detail=(
                    f"{candidate_count} candidate routes are cached locally."
                    if candidate_count > 0
                    else ("Refresh scan after recorder data lands." if has_data else "Waiting for recorder data.")
                ),
                tone="active" if candidate_count > 0 else ("warning" if has_data else "locked"),
            ),
            MachineStatus(
                id="route",
                label="Bot bay",
                value="paper scored" if score_ready else ("staged" if candidate_count > 0 else "empty"),
                detail=(
                    f"{score_snapshot.completed_runs} paper runs have landed in Score."
                    if score_ready
                    else ("A route is staged. Start a session before live thinking." if candidate_count > 0 else "No route staged yet.")
                ),
                tone="success" if score_ready else ("warning" if candidate_count > 0 else "locked"),
            ),
        ]

        model = HangarViewModel(
            next_step=next_step,
            status_tiles=[
                {"label": "Paper mode", "value": "active", "tone": "active"},
                {
                    "label": "Live gate",
                    "value": "locked" if profile.live_mode == "locked" else profile.live_mode,
                    "tone": "locked" if profile.live_mode == "locked" else "warning",
                },
                {
                    "label": "Lab",
                    "value": "offline" if not profile.lab_enabled else "online",
                    "tone": "idle" if not profile.lab_enabled else "warning",
                },
            ],
            mission=profile.primary_mission,
            paper_score=(
                f"Paper score ${score_snapshot.paper_realized_pnl_cents / 100:.2f} - "
                f"Portfolio {score_snapshot.portfolio_score} · Slots {score_snapshot.available_bot_slots}"
                if score_ready
                else "Paper score waiting for first run"
            ),
            primary_action_hint="Primary action stays obvious until recorder data and staged routes exist for the bot bay.",
            checklist_title="First pass checklist",
            checklist=checklist_items,
            milestone_title=f"Golden path - {complete_count}/4 complete",
            milestones=milestones,
            machine_statuses=machine_statuses,
            system_log=[
                f"[SYS] Profile online: {profile.display_name}",
                f"[REC] {machine_statuses[0].value.upper()} :: {machine_statuses[0].detail}",
                f"[SCAN] {machine_statuses[1].value.upper()} :: {machine_statuses[1].detail}",
                f"[BOT] {machine_statuses[2].value.upper()} :: {machine_statuses[2].detail}",
                f"[SAFE] PAPER=ACTIVE | LIVE={profile.live_mode.upper()} | LAB={'ON' if profile.lab_enabled else 'OFF'}",
            ],
            telemetry_stats=[
                {"label": "Brand", "value": profile.brand_name, "detail": "", "tone": "active"},
                {"label": "Profile", "value": profile.display_name, "detail": "", "tone": "active"},
                {"label": "Goal", "value": profile.primary_goal.replace('_', ' ').title(), "detail": "", "tone": "idle"},
                {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": machine_statuses[0].tone},
                {
                    "label": "Data",
                    "value": (
                        f"{status.summary.raw_messages} raw / {status.summary.book_snapshots} books"
                        if status.summary is not None
                        else "No database"
                    ),
                    "detail": "",
                    "tone": "warning" if has_data else "idle",
                },
                {"label": "Risk preset", "value": profile.risk_policy_id.title(), "detail": "", "tone": "idle"},
                {
                    "label": "Latest warning",
                    "value": status.summary.latest_warning if status.summary and status.summary.latest_warning else "No warnings",
                    "detail": "",
                    "tone": "warning" if status.summary and status.summary.latest_warning else "idle",
                },
            ],
            capability_rows=[
                {
                    "id": state.capability_id,
                    "label": state.label,
                    "value": "ready" if state.ready else "blocked",
                    "detail": state.message,
                    "tone": "active" if state.ready else "locked",
                }
                for state in capability_states
            ],
            connector_rows=[
                {
                    "id": connection.venue_id,
                    "label": connection.venue_label,
                    "value": connection.mode,
                    "detail": connection.message,
                    "tone": ("active" if connection.mode in {"paper", "configured", "live_ready"} else "idle"),
                }
                for connection in connections
            ],
        )
        self.apply_model(model)
        self.open_setup_button.setText("Edit setup")
        primary_text = "Start session" if candidate_count > 0 and has_data and not is_running else "Boot recorder"
        self._set_action_button(
            self.start_button,
            enabled=not is_running,
            active_text=primary_text,
            inactive_text=f"{primary_text} [busy]",
        )
        self._set_action_button(self.stop_button, enabled=is_running, active_text="Stop", inactive_text="Stop [idle]")
        self._set_action_button(self.replay_button, enabled=has_store and not is_running, active_text="Replay", inactive_text="Replay [locked]")
        self._set_action_button(self.verify_button, enabled=has_store and not is_running, active_text="Verify", inactive_text="Verify [locked]")
        self._set_action_button(self.scan_button, enabled=has_data and not is_running, active_text="Scan routes", inactive_text="Scan routes [locked]")
        self._set_action_button(self.paper_button, enabled=candidate_count > 0, active_text="Start session", inactive_text="Start session [locked]")
        self.set_secondary_actions_visible(
            has_data or candidate_count > 0 or score_ready or status.state in {"completed", "failed"}
        )

    @staticmethod
    def _set_action_button(button: QPushButton, *, enabled: bool, active_text: str, inactive_text: str) -> None:
        button.setEnabled(enabled)
        button.setText(active_text if enabled else inactive_text)

    @staticmethod
    def _render_checklist(items: list[ChecklistItem]) -> str:
        lines: list[str] = []
        for item in items:
            if item.complete:
                marker = "[x]"
            elif item.current:
                marker = "[>]"
            elif item.blocked:
                marker = "[!]"
            else:
                marker = "[ ]"
            lines.append(f"{marker} {item.label}")
            if item.detail:
                lines.append(f"    {item.detail}")
        return "\n".join(lines)

    @staticmethod
    def _render_status_rows(items: list) -> str:
        return "\n".join(
            f"{item.label.upper():<13} {item.value.upper():<10} {item.detail}".rstrip()
            for item in items
        )
