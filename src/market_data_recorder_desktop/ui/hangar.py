from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
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
from .primitives import (
    BootTicker,
    CommandFooter,
    InsetConsolePanel,
    MeterBar,
    PixelPanel,
    RiskBadge,
    StatCell,
    StatusModule,
    TelemetryLamp,
)


class MissionDeck(PixelPanel):
    def __init__(self) -> None:
        super().__init__("HOME", "FIRST RUN", tone="active")
        self.title_label = QLabel("Home")
        self.title_label.setObjectName("heroTitle")
        self.next_step_label = QLabel("Run recorder to build the first local sample.")
        self.next_step_label.setObjectName("heroText")
        self.next_step_label.setWordWrap(True)

        lamps_row = QHBoxLayout()
        lamps_row.setSpacing(8)
        self.paper_state_badge = TelemetryLamp("PRACTICE")
        self.live_state_badge = TelemetryLamp("GATE")
        self.lab_state_badge = TelemetryLamp("LAB")
        lamps_row.addWidget(self.paper_state_badge)
        lamps_row.addWidget(self.live_state_badge)
        lamps_row.addWidget(self.lab_state_badge)
        lamps_row.addStretch(1)

        mission_strip = QWidget()
        mission_strip_layout = QHBoxLayout(mission_strip)
        mission_strip_layout.setContentsMargins(0, 0, 0, 0)
        mission_strip_layout.setSpacing(8)
        self.mission_label = QLabel("Keep Polymarket on, take one sample, then try one practice run.")
        self.mission_label.setObjectName("heroText")
        self.mission_label.setWordWrap(True)
        self.score_label = QLabel("Practice score: waiting")
        self.score_label.setObjectName("heroText")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.score_label.setWordWrap(True)
        mission_strip_layout.addWidget(self.mission_label, 1)
        mission_strip_layout.addWidget(self.score_label, 0)

        self.body_layout.addWidget(self.title_label)
        self.body_layout.addLayout(lamps_row)
        self.body_layout.addWidget(self.next_step_label)
        self.body_layout.addWidget(mission_strip)


class ObjectivePanel(PixelPanel):
    def __init__(self) -> None:
        super().__init__("SETUP", "CHECKLIST", tone="warning")
        self.setup_progress_label = QLabel("First run")
        self.setup_progress_label.setProperty("sectionLabel", True)
        self.setup_steps_label = QLabel()
        self.setup_steps_label.setWordWrap(True)
        self.setup_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.open_setup_button = QPushButton("Set up profile")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("Setup guide")
        self.view_docs_button.setProperty("buttonRole", "ghost")
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.open_setup_button)
        button_row.addWidget(self.view_docs_button)
        button_row.addStretch(1)
        self.body_layout.addWidget(self.setup_progress_label)
        self.body_layout.addWidget(self.setup_steps_label)
        self.body_layout.addLayout(button_row)


class ActionPanel(PixelPanel):
    def __init__(self) -> None:
        super().__init__("ACTION", "RUN", tone="active")
        self.primary_action_hint = QLabel("Run recorder is the only active command until a sample lands.")
        self.primary_action_hint.setObjectName("heroText")
        self.primary_action_hint.setWordWrap(True)
        self.risk_badge = RiskBadge()
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addWidget(self.primary_action_hint, 1)
        top_row.addWidget(self.risk_badge, 0, Qt.AlignmentFlag.AlignTop)

        primary_row = QHBoxLayout()
        primary_row.setSpacing(8)
        self.start_button = QPushButton("Run recorder")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("buttonRole", "secondary")
        primary_row.addWidget(self.start_button, 1)
        primary_row.addWidget(self.stop_button, 1)

        self.secondary_actions_widget = QWidget()
        secondary_row = QGridLayout(self.secondary_actions_widget)
        secondary_row.setContentsMargins(0, 0, 0, 0)
        secondary_row.setHorizontalSpacing(8)
        secondary_row.setVerticalSpacing(8)
        self.replay_button = QPushButton("Replay")
        self.replay_button.setProperty("buttonRole", "ghost")
        self.verify_button = QPushButton("Verify")
        self.verify_button.setProperty("buttonRole", "ghost")
        self.scan_button = QPushButton("Scan routes")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("Start practice")
        self.paper_button.setProperty("buttonRole", "secondary")
        secondary_row.addWidget(self.replay_button, 0, 0)
        secondary_row.addWidget(self.verify_button, 0, 1)
        secondary_row.addWidget(self.scan_button, 1, 0)
        secondary_row.addWidget(self.paper_button, 1, 1)
        self.secondary_actions_widget.hide()

        self.body_layout.addLayout(top_row)
        self.body_layout.addLayout(primary_row)
        self.body_layout.addWidget(self.secondary_actions_widget)


class StatusPanel(PixelPanel):
    def __init__(self) -> None:
        super().__init__("SYSTEM", "STATUS", tone="idle")
        tile_row = QHBoxLayout()
        tile_row.setSpacing(8)
        self.recorder_tile = StatusModule("Recorder")
        self.scanner_tile = StatusModule("Scanner")
        self.route_tile = StatusModule("Route")
        tile_row.addWidget(self.recorder_tile)
        tile_row.addWidget(self.scanner_tile)
        tile_row.addWidget(self.route_tile)
        self.body_layout.addLayout(tile_row)


class ProgressPanel(PixelPanel):
    def __init__(self) -> None:
        super().__init__("PROGRESS", "MILESTONES", tone="success")
        self.loop_label = QLabel("CLEAR 0/4")
        self.loop_label.setObjectName("heroText")
        self.loop_meter = MeterBar()
        self.loop_steps_label = QLabel()
        self.loop_steps_label.setWordWrap(True)
        self.loop_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.body_layout.addWidget(self.loop_label)
        self.body_layout.addWidget(self.loop_meter)
        self.body_layout.addWidget(self.loop_steps_label)


class TelemetryPanelGroup(PixelPanel):
    def __init__(self) -> None:
        super().__init__("DETAILS", "STATE", tone="idle")
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        labels = ("APP", "PROFILE", "GOAL", "RECORDER", "DATA", "RISK", "WARNING")
        self._cells: dict[str, StatCell] = {}
        for index, label in enumerate(labels):
            cell = StatCell(label)
            self._cells[label] = cell
            grid.addWidget(cell, index // 2, index % 2)
        self.capability_text = InsetConsolePanel()
        self.capability_text.setMaximumHeight(112)
        self.connections_text = InsetConsolePanel()
        self.connections_text.setMaximumHeight(96)
        self.body_layout.addLayout(grid)
        self.body_layout.addWidget(self.capability_text)
        self.body_layout.addWidget(self.connections_text)
        self.brand_label = self._cells["APP"].value_label
        self.profile_label = self._cells["PROFILE"].value_label
        self.goal_label = self._cells["GOAL"].value_label
        self.engine_label = self._cells["RECORDER"].value_label
        self.data_label = self._cells["DATA"].value_label
        self.risk_label = self._cells["RISK"].value_label
        self.warning_label = self._cells["WARNING"].value_label

    def set_telemetry(self, stats: list[tuple[str, str, str, SemanticStateColor]]) -> None:
        key_map = {
            "Brand": "APP",
            "Profile": "PROFILE",
            "Goal": "GOAL",
            "Recorder": "RECORDER",
            "Data": "DATA",
            "Risk preset": "RISK",
            "Latest warning": "WARNING",
        }
        for label, value, detail, tone in stats:
            mapped = key_map.get(label)
            if mapped and mapped in self._cells:
                self._cells[mapped].set_value(value, detail=detail, tone=tone)


class ConsoleFooter(PixelPanel):
    def __init__(self) -> None:
        super().__init__("LOG", "RECENT EVENTS", tone="active")
        self.boot_ticker = BootTicker()
        self.system_log = InsetConsolePanel()
        self.system_log.setMaximumHeight(136)
        self.command_footer = CommandFooter(
            [
                ("ESC", "BACK"),
                ("SETUP", "PROFILE"),
                ("R", "RUN"),
                ("S", "SCAN"),
                ("D", "DIAG"),
            ]
        )
        self.body_layout.addWidget(self.boot_ticker)
        self.body_layout.addWidget(self.system_log)
        self.body_layout.addWidget(self.command_footer)


class HomeTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        self.header = MissionDeck()
        self.objective_panel = ObjectivePanel()
        self.action_bar = ActionPanel()
        self.status_panel = StatusPanel()
        self.progress_panel = ProgressPanel()
        self.telemetry_panel = TelemetryPanelGroup()
        self.console_footer = ConsoleFooter()

        self.safe_state_label = self.header.title_label
        self.next_step_label = self.header.next_step_label
        self.paper_state_badge = self.header.paper_state_badge
        self.live_state_badge = self.header.live_state_badge
        self.lab_state_badge = self.header.lab_state_badge
        self.mission_label = self.header.mission_label
        self.score_label = self.header.score_label

        self.setup_progress_label = self.objective_panel.setup_progress_label
        self.setup_steps_label = self.objective_panel.setup_steps_label
        self.open_setup_button = self.objective_panel.open_setup_button
        self.view_docs_button = self.objective_panel.view_docs_button

        self.primary_action_hint = self.action_bar.primary_action_hint
        self.start_button = self.action_bar.start_button
        self.stop_button = self.action_bar.stop_button
        self.secondary_actions_widget = self.action_bar.secondary_actions_widget
        self.replay_button = self.action_bar.replay_button
        self.verify_button = self.action_bar.verify_button
        self.scan_button = self.action_bar.scan_button
        self.paper_button = self.action_bar.paper_button

        self.recorder_tile = self.status_panel.recorder_tile
        self.scanner_tile = self.status_panel.scanner_tile
        self.route_tile = self.status_panel.route_tile
        self.system_log = self.console_footer.system_log
        self.boot_ticker = self.console_footer.boot_ticker

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

        mission_field = QHBoxLayout()
        mission_field.setSpacing(16)

        self.left_column = QWidget()
        left_col = QVBoxLayout(self.left_column)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(16)
        left_col.addWidget(self.objective_panel)
        left_col.addWidget(self.progress_panel)

        self.middle_column = QWidget()
        middle_col = QVBoxLayout(self.middle_column)
        middle_col.setContentsMargins(0, 0, 0, 0)
        middle_col.setSpacing(16)
        middle_col.addWidget(self.action_bar)

        self.right_column = QWidget()
        right_col = QVBoxLayout(self.right_column)
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(16)
        right_col.addWidget(self.status_panel)
        right_col.addWidget(self.telemetry_panel)

        mission_field.addWidget(self.left_column, 4)
        mission_field.addWidget(self.middle_column, 4)
        mission_field.addWidget(self.right_column, 5)
        layout.addLayout(mission_field)
        layout.addWidget(self.console_footer)
        layout.addStretch(1)

    def apply_model(self, model: HangarViewModel) -> None:
        self.safe_state_label.setText(model.title)
        self.next_step_label.setText(model.next_step)
        badge_map = {
            "Practice mode": self.paper_state_badge,
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
        self.recorder_tile.set_state(
            model.machine_statuses[0].value,
            model.machine_statuses[0].detail,
            tone=model.machine_statuses[0].tone,
        )
        self.scanner_tile.set_state(
            model.machine_statuses[1].value,
            model.machine_statuses[1].detail,
            tone=model.machine_statuses[1].tone,
        )
        self.route_tile.set_state(
            model.machine_statuses[2].value,
            model.machine_statuses[2].detail,
            tone=model.machine_statuses[2].tone,
        )
        self.system_log.setPlainText("\n".join(model.system_log))
        self.boot_ticker.set_messages(model.system_log)
        telemetry_rows = [(item.label, item.value, item.detail, item.tone) for item in model.telemetry_stats]
        self.telemetry_panel.set_telemetry(telemetry_rows)
        self.capability_text.setPlainText(self._render_status_rows(model.capability_rows))
        self.connections_text.setPlainText(self._render_status_rows(model.connector_rows))

    def set_secondary_actions_visible(self, visible: bool) -> None:
        self.secondary_actions_widget.setVisible(visible)

    def set_surface_mode(self, *, has_profile: bool, has_data: bool, score_ready: bool) -> None:
        self.progress_panel.setVisible(has_profile)
        self.right_column.setVisible(has_profile)
        self.telemetry_panel.setVisible(has_profile and (has_data or score_ready))

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
        del checklist
        if profile is None:
            model = HangarViewModel(
                title="Home",
                next_step="Set up or import a profile, keep Polymarket on, then run the recorder.",
                status_tiles=[
                    {"label": "Practice mode", "value": "active", "tone": "active"},
                    {"label": "Live gate", "value": "locked", "tone": "locked"},
                    {"label": "Lab", "value": "offline", "tone": "idle"},
                ],
                mission="Create a profile, take one local sample, then start one practice run.",
                paper_score="Practice score: waiting",
                primary_action_hint="Set up a profile first. Run recorder unlocks after the profile is saved.",
                checklist_title="First run",
                checklist=[
                    ChecklistItem(id="profile", label="Set up profile.", current=True),
                    ChecklistItem(id="recorder", label="Run recorder.", detail="Recorder stays locked until a profile exists."),
                    ChecklistItem(id="scan", label="Start first practice run.", detail="A run needs local data and one staged route."),
                ],
                milestone_title="Milestones 0/4",
                milestones=[
                    ChecklistItem(id="loadout", label="Save setup", detail="Create a profile with Polymarket armed."),
                    ChecklistItem(id="record", label="Take sample", detail="Recorder stays idle until a profile exists."),
                    ChecklistItem(id="inspect", label="Stage route", detail="Scan needs local sample first."),
                    ChecklistItem(id="score", label="Bank score", detail="Score lights up after the first practice run."),
                ],
                machine_statuses=[
                    MachineStatus(id="recorder", label="REC", value="blocked", detail="Profile required.", tone="locked"),
                    MachineStatus(id="scanner", label="SCAN", value="waiting", detail="Local books not ready.", tone="idle"),
                    MachineStatus(id="route", label="ROUTE", value="empty", detail="No route staged.", tone="idle"),
                ],
                system_log=[
                    "[SYS] No profile selected.",
                    "[REC] Recorder locked until a profile exists.",
                    "[SCAN] Waiting for first local sample.",
                    "[ROUTE] Score stays dark until the first practice run.",
                ],
                telemetry_stats=[
                    {"label": "Brand", "value": "Superior", "detail": "", "tone": "active"},
                    {"label": "Profile", "value": "No profile", "detail": "", "tone": "warning"},
                    {"label": "Goal", "value": "First run", "detail": "", "tone": "warning"},
                    {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": "idle"},
                    {"label": "Data", "value": "No DB", "detail": "", "tone": "idle"},
                    {"label": "Risk preset", "value": "Starter", "detail": "", "tone": "idle"},
                    {"label": "Latest warning", "value": "None", "detail": "", "tone": "idle"},
                ],
                capability_rows=[
                    {"id": "recorder", "label": "REC", "value": "blocked", "detail": "Needs profile.", "tone": "locked"},
                    {"id": "scanner", "label": "SCAN", "value": "blocked", "detail": "Needs local sample.", "tone": "locked"},
                    {"id": "paper score", "label": "SCORE", "value": "blocked", "detail": "Needs first practice run.", "tone": "locked"},
                    {"id": "live gate", "label": "GATE", "value": "locked", "detail": "Practice-first only.", "tone": "locked"},
                ],
                connector_rows=[
                    {"id": "polymarket", "label": "POLYMARKET", "value": "disabled", "detail": "Not armed.", "tone": "warning"},
                    {"id": "kalshi", "label": "KALSHI", "value": "disabled", "detail": "Optional feed.", "tone": "idle"},
                    {"id": "coach", "label": "COACH", "value": "disabled", "detail": "Optional link.", "tone": "idle"},
                ],
            )
            self.apply_model(model)
            self.set_surface_mode(has_profile=False, has_data=False, score_ready=False)
            self.open_setup_button.setText("Set up profile")
            self.view_docs_button.setText("Setup guide")
            self.action_bar.risk_badge.set_state("Locked", "locked")
            self._set_action_button(self.start_button, enabled=False, active_text="Run recorder", inactive_text="Run recorder [locked]")
            self._set_action_button(self.stop_button, enabled=False, active_text="Stop", inactive_text="Stop [idle]")
            self._set_action_button(self.replay_button, enabled=False, active_text="Replay", inactive_text="Replay [locked]")
            self._set_action_button(self.verify_button, enabled=False, active_text="Verify", inactive_text="Verify [locked]")
            self._set_action_button(self.scan_button, enabled=False, active_text="Scan routes", inactive_text="Scan routes [locked]")
            self._set_action_button(self.paper_button, enabled=False, active_text="Start practice", inactive_text="Practice [locked]")
            self.set_secondary_actions_visible(False)
            return

        summary = status.summary
        has_store = summary is not None
        has_data = summary is not None and (summary.raw_messages > 0 or summary.book_snapshots > 0)
        is_running = status.state == "running"
        scanner_ready = any(state.capability_id == "scanner" and state.ready for state in capability_states)
        has_data = has_data or scanner_ready or candidate_count > 0
        loadout_ready = "polymarket" in profile.equipped_connectors and bool(profile.equipped_modules)
        score_ready = score_snapshot.total_runs > 0
        if not loadout_ready:
            next_step = "Turn on Polymarket and one play style."
        elif is_running:
            next_step = "Wait for sample counts. Do not interrupt capture."
        elif not has_data:
            next_step = "Run recorder to take the first sample."
        elif candidate_count > 0 and not score_ready:
            next_step = "Start a practice run and bank the first score."
        elif not score_ready:
            next_step = "Refresh Scan until one route stages."
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            next_step = "Keep banking practice score. Live stays locked."
        else:
            next_step = "Keep the loop steady: sample, scan, practice, score."

        checklist_items = [
            ChecklistItem(
                id="boot",
                label="Run recorder.",
                detail="Take the first local book sample.",
                complete=has_data or is_running,
                current=loadout_ready and not (has_data or is_running),
            ),
            ChecklistItem(
                id="wait",
                label="Wait for sample counts.",
                detail="Watch message and book totals.",
                complete=has_data,
                current=is_running,
            ),
            ChecklistItem(
                id="scan",
                label="Start practice run.",
                detail="Arm the starter bot when one route stages.",
                complete=scanner_ready,
                current=has_data and not scanner_ready,
            ),
        ]
        milestone_specs = [
            ("loadout", "Save setup", loadout_ready, "Polymarket and one play style are armed."),
            ("record", "Take sample", has_data, "Recorder has local data."),
            ("inspect", "Stage route", scanner_ready, "Scan has an explainable route."),
            ("score", "Bank score", score_ready, "Practice ledger has one completed run."),
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
            milestones.append(ChecklistItem(id=item_id, label=label, detail=detail, complete=complete, current=current))

        machine_statuses = [
            MachineStatus(
                id="recorder",
                label="REC",
                value="capturing" if is_running else ("ready" if has_data else ("idle" if loadout_ready else "blocked")),
                detail=(
                    f"{status.summary.raw_messages} MSG / {status.summary.book_snapshots} BOOKS"
                    if status.summary is not None
                    else "No sample yet."
                ),
                tone="active" if is_running or has_data else ("warning" if loadout_ready else "locked"),
            ),
            MachineStatus(
                id="scanner",
                label="SCAN",
                value="routes found" if candidate_count > 0 else ("ready" if scanner_ready else ("standby" if has_data else "waiting")),
                detail=(
                    f"{candidate_count} routes cached."
                    if candidate_count > 0
                    else ("Run Scan after the sample lands." if has_data else "Waiting for recorder.")
                ),
                tone="active" if candidate_count > 0 else ("warning" if has_data else "locked"),
            ),
            MachineStatus(
                id="route",
                label="ROUTE",
                value="banked" if score_ready else ("staged" if candidate_count > 0 else "empty"),
                detail=(
                    f"{score_snapshot.completed_runs} runs banked."
                    if score_ready
                    else ("One route is staged. Start the practice run." if candidate_count > 0 else "No route staged.")
                ),
                tone="success" if score_ready else ("warning" if candidate_count > 0 else "locked"),
            ),
        ]

        model = HangarViewModel(
            title="Home",
            next_step=next_step,
            status_tiles=[
                    {"label": "Practice mode", "value": "active", "tone": "active"},
                {"label": "Live gate", "value": "locked" if profile.live_mode == "locked" else profile.live_mode, "tone": "locked" if profile.live_mode == "locked" else "warning"},
                {"label": "Lab", "value": "offline" if not profile.lab_enabled else "online", "tone": "idle" if not profile.lab_enabled else "warning"},
            ],
            mission=profile.primary_mission,
            paper_score=(
                f"Practice ${score_snapshot.paper_realized_pnl_cents / 100:.2f} / Score {score_snapshot.portfolio_score} / Slots {score_snapshot.available_bot_slots}"
                if score_ready
                else "Practice score: waiting"
            ),
            primary_action_hint="Keep the action bar focused until sample data and a staged route exist.",
            checklist_title="First run",
            checklist=checklist_items,
            milestone_title=f"Milestones {complete_count}/4",
            milestones=milestones,
            machine_statuses=machine_statuses,
            system_log=[
                f"[SYS] {profile.display_name} online.",
                f"[REC] {machine_statuses[0].value.upper()} :: {machine_statuses[0].detail}",
                f"[SCAN] {machine_statuses[1].value.upper()} :: {machine_statuses[1].detail}",
                f"[ROUTE] {machine_statuses[2].value.upper()} :: {machine_statuses[2].detail}",
                f"[SAFE] PRACTICE=ACTIVE | GATE={profile.live_mode.upper()} | LAB={'ON' if profile.lab_enabled else 'OFF'}",
            ],
            telemetry_stats=[
                {"label": "Brand", "value": profile.brand_name, "detail": "", "tone": "active"},
                {"label": "Profile", "value": profile.display_name, "detail": "", "tone": "active"},
                    {"label": "Goal", "value": profile.primary_goal.replace("_", " "), "detail": "", "tone": "idle"},
                {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": machine_statuses[0].tone},
                    {"label": "Data", "value": (f"{status.summary.raw_messages} raw / {status.summary.book_snapshots} books" if status.summary is not None else "No DB"), "detail": "", "tone": "warning" if has_data else "idle"},
                {"label": "Risk preset", "value": profile.risk_policy_id, "detail": "", "tone": "idle"},
                    {"label": "Latest warning", "value": status.summary.latest_warning if status.summary and status.summary.latest_warning else "None", "detail": "", "tone": "warning" if status.summary and status.summary.latest_warning else "idle"},
            ],
            capability_rows=[
                {"id": state.capability_id, "label": state.label, "value": "ready" if state.ready else "blocked", "detail": state.message, "tone": "active" if state.ready else "locked"}
                for state in capability_states
            ],
            connector_rows=[
                {"id": connection.venue_id, "label": connection.venue_label, "value": connection.mode, "detail": connection.message, "tone": ("active" if connection.mode in {"paper", "configured", "live_ready"} else "idle")}
                for connection in connections
            ],
        )
        self.apply_model(model)
        self.set_surface_mode(has_profile=True, has_data=has_data, score_ready=score_ready)
        self.open_setup_button.setText("Edit profile")
        self.view_docs_button.setText("Setup guide")
        self.action_bar.risk_badge.set_state("Paper", "active")
        primary_text = "Start practice" if candidate_count > 0 and has_data and not is_running else "Run recorder"
        self._set_action_button(self.start_button, enabled=not is_running, active_text=primary_text, inactive_text=f"{primary_text} [busy]")
        self._set_action_button(self.stop_button, enabled=is_running, active_text="Stop", inactive_text="Stop [idle]")
        self._set_action_button(self.replay_button, enabled=has_store and not is_running, active_text="Replay sample", inactive_text="Replay sample [locked]")
        self._set_action_button(self.verify_button, enabled=has_store and not is_running, active_text="Verify sample", inactive_text="Verify sample [locked]")
        self._set_action_button(self.scan_button, enabled=has_data and not is_running, active_text="Scan routes", inactive_text="Scan routes [locked]")
        self._set_action_button(self.paper_button, enabled=candidate_count > 0, active_text="Start practice", inactive_text="Practice [locked]")
        self.set_secondary_actions_visible(has_data or candidate_count > 0 or score_ready or status.state in {"completed", "failed"})

    @staticmethod
    def _set_action_button(button: QPushButton, *, enabled: bool, active_text: str, inactive_text: str) -> None:
        button.setEnabled(enabled)
        button.setText(active_text if enabled else inactive_text)

    @staticmethod
    def _render_checklist(items: list[ChecklistItem]) -> str:
        lines: list[str] = []
        for item in items:
            if item.complete:
                marker = "[OK]"
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
            f"{item.label:<13} {item.value:<10} {item.detail}".rstrip()
            for item in items
        )
