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
        super().__init__("SECTOR A1", "MISSION FIELD", tone="active")
        self.title_label = QLabel("HANGAR // MISSION CONTROL")
        self.title_label.setObjectName("heroTitle")
        self.next_step_label = QLabel("BOOT RECORDER TO BUILD THE FIRST LOCAL SAMPLE.")
        self.next_step_label.setObjectName("heroText")
        self.next_step_label.setWordWrap(True)

        lamps_row = QHBoxLayout()
        lamps_row.setSpacing(8)
        self.paper_state_badge = TelemetryLamp("PAPER")
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
        self.mission_label = QLabel("ARM POLYMARKET. TAKE SAMPLE. STAGE ONE RUN.")
        self.mission_label.setObjectName("heroText")
        self.mission_label.setWordWrap(True)
        self.score_label = QLabel("PAPER SCORE // WAITING")
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
        super().__init__("PHASE 01", "OBJECTIVES", tone="warning")
        self.setup_progress_label = QLabel("BOOT LIST")
        self.setup_progress_label.setProperty("sectionLabel", True)
        self.setup_steps_label = QLabel()
        self.setup_steps_label.setWordWrap(True)
        self.setup_steps_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.open_setup_button = QPushButton("BOOT PHASES")
        self.open_setup_button.setProperty("buttonRole", "secondary")
        self.view_docs_button = QPushButton("DOCS")
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
        super().__init__("SLOT 02", "COMMAND DECK", tone="active")
        self.primary_action_hint = QLabel("BOOT IS THE ONLY LIVE COMMAND UNTIL A SAMPLE LANDS.")
        self.primary_action_hint.setObjectName("heroText")
        self.primary_action_hint.setWordWrap(True)
        self.risk_badge = RiskBadge()
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addWidget(self.primary_action_hint, 1)
        top_row.addWidget(self.risk_badge, 0, Qt.AlignmentFlag.AlignTop)

        primary_row = QHBoxLayout()
        primary_row.setSpacing(8)
        self.start_button = QPushButton("BOOT RECORDER")
        self.stop_button = QPushButton("STOP")
        self.stop_button.setProperty("buttonRole", "secondary")
        primary_row.addWidget(self.start_button, 1)
        primary_row.addWidget(self.stop_button, 1)

        self.secondary_actions_widget = QWidget()
        secondary_row = QGridLayout(self.secondary_actions_widget)
        secondary_row.setContentsMargins(0, 0, 0, 0)
        secondary_row.setHorizontalSpacing(8)
        secondary_row.setVerticalSpacing(8)
        self.replay_button = QPushButton("REPLAY")
        self.replay_button.setProperty("buttonRole", "ghost")
        self.verify_button = QPushButton("VERIFY")
        self.verify_button.setProperty("buttonRole", "ghost")
        self.scan_button = QPushButton("SCAN")
        self.scan_button.setProperty("buttonRole", "secondary")
        self.paper_button = QPushButton("START RUN")
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
        super().__init__("BUS A0", "SYSTEM ZONE", tone="idle")
        tile_row = QHBoxLayout()
        tile_row.setSpacing(8)
        self.recorder_tile = StatusModule("REC")
        self.scanner_tile = StatusModule("SCAN")
        self.route_tile = StatusModule("ARB")
        tile_row.addWidget(self.recorder_tile)
        tile_row.addWidget(self.scanner_tile)
        tile_row.addWidget(self.route_tile)
        self.body_layout.addLayout(tile_row)


class ProgressPanel(PixelPanel):
    def __init__(self) -> None:
        super().__init__("TRACK 03", "SCORE PATH", tone="success")
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
        super().__init__("BUS B2", "TELEMETRY", tone="idle")
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        labels = ("BRAND", "PROFILE", "MISSION", "RECORDER", "DATA", "RISK", "WARN")
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
        self.brand_label = self._cells["BRAND"].value_label
        self.profile_label = self._cells["PROFILE"].value_label
        self.goal_label = self._cells["MISSION"].value_label
        self.engine_label = self._cells["RECORDER"].value_label
        self.data_label = self._cells["DATA"].value_label
        self.risk_label = self._cells["RISK"].value_label
        self.warning_label = self._cells["WARN"].value_label

    def set_telemetry(self, stats: list[tuple[str, str, str, SemanticStateColor]]) -> None:
        key_map = {
            "Brand": "BRAND",
            "Profile": "PROFILE",
            "Goal": "MISSION",
            "Recorder": "RECORDER",
            "Data": "DATA",
            "Risk preset": "RISK",
            "Latest warning": "WARN",
        }
        for label, value, detail, tone in stats:
            mapped = key_map.get(label)
            if mapped and mapped in self._cells:
                self._cells[mapped].set_value(value, detail=detail, tone=tone)


class ConsoleFooter(PixelPanel):
    def __init__(self) -> None:
        super().__init__("CONSOLE", "SYSTEM FEED", tone="active")
        self.boot_ticker = BootTicker()
        self.system_log = InsetConsolePanel()
        self.system_log.setMaximumHeight(136)
        self.command_footer = CommandFooter(
            [
                ("B", "BACK"),
                ("A", "BOOT"),
                ("X", "SCAN"),
                ("START", "RUN"),
                ("SELECT", "DIAG"),
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
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        left_col.addWidget(self.objective_panel)
        left_col.addWidget(self.progress_panel)

        middle_col = QVBoxLayout()
        middle_col.setSpacing(16)
        middle_col.addWidget(self.action_bar)

        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        right_col.addWidget(self.status_panel)
        right_col.addWidget(self.telemetry_panel)

        mission_field.addLayout(left_col, 4)
        mission_field.addLayout(middle_col, 4)
        mission_field.addLayout(right_col, 5)
        layout.addLayout(mission_field)
        layout.addWidget(self.console_footer)
        layout.addStretch(1)

    def apply_model(self, model: HangarViewModel) -> None:
        self.safe_state_label.setText(model.title.upper())
        self.next_step_label.setText(model.next_step.upper())
        badge_map = {
            "Paper mode": self.paper_state_badge,
            "Live gate": self.live_state_badge,
            "Lab": self.lab_state_badge,
        }
        for tile in model.status_tiles:
            badge = badge_map.get(tile.label)
            if badge is not None:
                badge.set_state(tile.value, tone=tile.tone)
        self.mission_label.setText(model.mission.upper())
        self.score_label.setText(model.paper_score.upper())
        self.primary_action_hint.setText(model.primary_action_hint.upper())
        self.setup_progress_label.setText(model.checklist_title.upper())
        self.setup_steps_label.setText(self._render_checklist(model.checklist))
        self.loop_label.setText(model.milestone_title.upper())
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
                title="NO CART INSERTED",
                next_step="CREATE A PROFILE. ARM POLYMARKET. BOOT RECORDER.",
                status_tiles=[
                    {"label": "Paper mode", "value": "active", "tone": "active"},
                    {"label": "Live gate", "value": "locked", "tone": "locked"},
                    {"label": "Lab", "value": "offline", "tone": "idle"},
                ],
                mission="INSERT A PROFILE CART, THEN TAKE THE FIRST SAMPLE.",
                paper_score="PAPER SCORE // WAITING",
                primary_action_hint="BOOT STAYS DARK UNTIL A PROFILE CART EXISTS.",
                checklist_title="BOOT LIST",
                checklist=[
                    ChecklistItem(id="profile", label="CREATE PROFILE CART.", current=True),
                    ChecklistItem(id="recorder", label="BOOT RECORDER.", detail="RECORDER STAYS LOCKED UNTIL A CART EXISTS."),
                    ChecklistItem(id="scan", label="START FIRST RUN.", detail="A RUN NEEDS LOCAL DATA AND ONE STAGED ROUTE."),
                ],
                milestone_title="CLEAR TRACK 0/4",
                milestones=[
                    ChecklistItem(id="loadout", label="ARM LOADOUT", detail="CREATE A PROFILE WITH POLYMARKET ARMED."),
                    ChecklistItem(id="record", label="TAKE SAMPLE", detail="RECORDER STAYS IDLE UNTIL A CART EXISTS."),
                    ChecklistItem(id="inspect", label="STAGE ROUTE", detail="RADAR NEEDS LOCAL SAMPLE FIRST."),
                    ChecklistItem(id="score", label="BANK SCORE", detail="SCORE LIGHTS UP AFTER THE FIRST RUN."),
                ],
                machine_statuses=[
                    MachineStatus(id="recorder", label="REC", value="blocked", detail="PROFILE CART REQUIRED.", tone="locked"),
                    MachineStatus(id="scanner", label="SCAN", value="waiting", detail="LOCAL BOOKS NOT READY.", tone="idle"),
                    MachineStatus(id="route", label="ARB", value="empty", detail="NO BOT SLOT STAGED.", tone="idle"),
                ],
                system_log=[
                    "[BOOT] NO CART INSERTED.",
                    "[REC] RECORDER LOCKED UNTIL PROFILE CART EXISTS.",
                    "[SCAN] WAITING FOR FIRST LOCAL SAMPLE.",
                    "[ARB] SCORE BUS IS DARK UNTIL FIRST RUN.",
                ],
                telemetry_stats=[
                    {"label": "Brand", "value": "SUPERIOR", "detail": "", "tone": "active"},
                    {"label": "Profile", "value": "NO CART", "detail": "", "tone": "warning"},
                    {"label": "Goal", "value": "BOOT PHASE", "detail": "", "tone": "warning"},
                    {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": "idle"},
                    {"label": "Data", "value": "NO DB", "detail": "", "tone": "idle"},
                    {"label": "Risk preset", "value": "STARTER", "detail": "", "tone": "idle"},
                    {"label": "Latest warning", "value": "NONE", "detail": "", "tone": "idle"},
                ],
                capability_rows=[
                    {"id": "recorder", "label": "REC", "value": "blocked", "detail": "NEEDS PROFILE CART.", "tone": "locked"},
                    {"id": "scanner", "label": "SCAN", "value": "blocked", "detail": "NEEDS LOCAL SAMPLE.", "tone": "locked"},
                    {"id": "paper score", "label": "SCORE", "value": "blocked", "detail": "NEEDS FIRST RUN.", "tone": "locked"},
                    {"id": "live gate", "label": "GATE", "value": "locked", "detail": "PAPER-FIRST ONLY.", "tone": "locked"},
                ],
                connector_rows=[
                    {"id": "polymarket", "label": "POLYMARKET", "value": "disabled", "detail": "NOT ARMED.", "tone": "warning"},
                    {"id": "kalshi", "label": "KALSHI", "value": "disabled", "detail": "OPTIONAL CART.", "tone": "idle"},
                    {"id": "coach", "label": "COACH", "value": "disabled", "detail": "OPTIONAL LINK.", "tone": "idle"},
                ],
            )
            self.apply_model(model)
            self.open_setup_button.setText("LOAD CART")
            self.view_docs_button.setText("OPEN DOCS")
            self.action_bar.risk_badge.set_state("LOCKED", "locked")
            self._set_action_button(self.start_button, enabled=False, active_text="BOOT RECORDER", inactive_text="BOOT [LOCKED]")
            self._set_action_button(self.stop_button, enabled=False, active_text="STOP", inactive_text="STOP [IDLE]")
            self._set_action_button(self.replay_button, enabled=False, active_text="REPLAY", inactive_text="REPLAY [LOCKED]")
            self._set_action_button(self.verify_button, enabled=False, active_text="VERIFY", inactive_text="VERIFY [LOCKED]")
            self._set_action_button(self.scan_button, enabled=False, active_text="SCAN", inactive_text="SCAN [LOCKED]")
            self._set_action_button(self.paper_button, enabled=False, active_text="START RUN", inactive_text="RUN [LOCKED]")
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
            next_step = "ARM POLYMARKET AND ONE MODULE."
        elif is_running:
            next_step = "WAIT FOR SAMPLE COUNTS. DO NOT BREAK CAPTURE."
        elif not has_data:
            next_step = "BOOT RECORDER TO TAKE THE FIRST SAMPLE."
        elif candidate_count > 0 and not score_ready:
            next_step = "START A PAPER RUN AND BANK THE FIRST SCORE."
        elif not score_ready:
            next_step = "SCAN AGAIN UNTIL ONE ROUTE STAGES."
        elif profile.paper_gate_passed and profile.live_mode == "locked":
            next_step = "KEEP BANKING PAPER SCORE. GATE STAYS LOCKED."
        else:
            next_step = "HOLD THE LOOP: SAMPLE. SCAN. RUN. BANK."

        checklist_items = [
            ChecklistItem(
                id="boot",
                label="BOOT RECORDER.",
                detail="TAKE THE FIRST LOCAL BOOK SAMPLE.",
                complete=has_data or is_running,
                current=loadout_ready and not (has_data or is_running),
            ),
            ChecklistItem(
                id="wait",
                label="WAIT FOR SAMPLE COUNTS.",
                detail="WATCH RAW MSG AND BOOK TOTALS.",
                complete=has_data,
                current=is_running,
            ),
            ChecklistItem(
                id="scan",
                label="START PAPER RUN.",
                detail="ARM THE STARTER BOT WHEN ONE ROUTE STAGES.",
                complete=scanner_ready,
                current=has_data and not scanner_ready,
            ),
        ]
        milestone_specs = [
            ("loadout", "ARM LOADOUT", loadout_ready, "POLYMARKET AND ONE MODULE ARMED."),
            ("record", "TAKE SAMPLE", has_data, "RECORDER HAS LOCAL DATA."),
            ("inspect", "STAGE ROUTE", scanner_ready, "RADAR HAS AN EXPLAINABLE ROUTE."),
            ("score", "BANK SCORE", score_ready, "PAPER LEDGER HAS ONE COMPLETED RUN."),
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
                    else "NO SAMPLE YET."
                ),
                tone="active" if is_running or has_data else ("warning" if loadout_ready else "locked"),
            ),
            MachineStatus(
                id="scanner",
                label="SCAN",
                value="routes found" if candidate_count > 0 else ("ready" if scanner_ready else ("standby" if has_data else "waiting")),
                detail=(
                    f"{candidate_count} ROUTES CACHED."
                    if candidate_count > 0
                    else ("RUN SCAN AFTER SAMPLE LANDS." if has_data else "WAITING FOR RECORDER.")
                ),
                tone="active" if candidate_count > 0 else ("warning" if has_data else "locked"),
            ),
            MachineStatus(
                id="route",
                label="ARB",
                value="banked" if score_ready else ("staged" if candidate_count > 0 else "empty"),
                detail=(
                    f"{score_snapshot.completed_runs} RUNS BANKED."
                    if score_ready
                    else ("ONE ROUTE IS STAGED. START THE RUN." if candidate_count > 0 else "NO ROUTE STAGED.")
                ),
                tone="success" if score_ready else ("warning" if candidate_count > 0 else "locked"),
            ),
        ]

        model = HangarViewModel(
            title="HANGAR // LIVE",
            next_step=next_step,
            status_tiles=[
                {"label": "Paper mode", "value": "active", "tone": "active"},
                {"label": "Live gate", "value": "locked" if profile.live_mode == "locked" else profile.live_mode, "tone": "locked" if profile.live_mode == "locked" else "warning"},
                {"label": "Lab", "value": "offline" if not profile.lab_enabled else "online", "tone": "idle" if not profile.lab_enabled else "warning"},
            ],
            mission=profile.primary_mission,
            paper_score=(
                f"PAPER ${score_snapshot.paper_realized_pnl_cents / 100:.2f} // SCORE {score_snapshot.portfolio_score} // SLOTS {score_snapshot.available_bot_slots}"
                if score_ready
                else "PAPER SCORE // WAITING"
            ),
            primary_action_hint="COMMAND DECK STAYS FOCUSED UNTIL SAMPLE DATA AND STAGED ROUTES EXIST.",
            checklist_title="BOOT LIST",
            checklist=checklist_items,
            milestone_title=f"CLEAR TRACK {complete_count}/4",
            milestones=milestones,
            machine_statuses=machine_statuses,
            system_log=[
                f"[CART] {profile.display_name.upper()} ONLINE.",
                f"[REC] {machine_statuses[0].value.upper()} :: {machine_statuses[0].detail}",
                f"[SCAN] {machine_statuses[1].value.upper()} :: {machine_statuses[1].detail}",
                f"[ARB] {machine_statuses[2].value.upper()} :: {machine_statuses[2].detail}",
                f"[SAFE] PAPER=ACTIVE | GATE={profile.live_mode.upper()} | LAB={'ON' if profile.lab_enabled else 'OFF'}",
            ],
            telemetry_stats=[
                {"label": "Brand", "value": profile.brand_name, "detail": "", "tone": "active"},
                {"label": "Profile", "value": profile.display_name, "detail": "", "tone": "active"},
                {"label": "Goal", "value": profile.primary_goal.replace("_", " "), "detail": "", "tone": "idle"},
                {"label": "Recorder", "value": status.state.title(), "detail": status.last_message, "tone": machine_statuses[0].tone},
                {"label": "Data", "value": (f"{status.summary.raw_messages} RAW / {status.summary.book_snapshots} BOOKS" if status.summary is not None else "NO DB"), "detail": "", "tone": "warning" if has_data else "idle"},
                {"label": "Risk preset", "value": profile.risk_policy_id, "detail": "", "tone": "idle"},
                {"label": "Latest warning", "value": status.summary.latest_warning if status.summary and status.summary.latest_warning else "NONE", "detail": "", "tone": "warning" if status.summary and status.summary.latest_warning else "idle"},
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
        self.open_setup_button.setText("EDIT CART")
        self.view_docs_button.setText("OPEN DOCS")
        self.action_bar.risk_badge.set_state("PAPER", "active")
        primary_text = "START RUN" if candidate_count > 0 and has_data and not is_running else "BOOT RECORDER"
        self._set_action_button(self.start_button, enabled=not is_running, active_text=primary_text, inactive_text=f"{primary_text} [BUSY]")
        self._set_action_button(self.stop_button, enabled=is_running, active_text="STOP", inactive_text="STOP [IDLE]")
        self._set_action_button(self.replay_button, enabled=has_store and not is_running, active_text="REPLAY", inactive_text="REPLAY [LOCKED]")
        self._set_action_button(self.verify_button, enabled=has_store and not is_running, active_text="VERIFY", inactive_text="VERIFY [LOCKED]")
        self._set_action_button(self.scan_button, enabled=has_data and not is_running, active_text="SCAN", inactive_text="SCAN [LOCKED]")
        self._set_action_button(self.paper_button, enabled=candidate_count > 0, active_text="START RUN", inactive_text="RUN [LOCKED]")
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
            lines.append(f"{marker} {item.label.upper()}")
            if item.detail:
                lines.append(f"    {item.detail.upper()}")
        return "\n".join(lines)

    @staticmethod
    def _render_status_rows(items: list) -> str:
        return "\n".join(
            f"{item.label.upper():<13} {item.value.upper():<10} {item.detail.upper()}".rstrip()
            for item in items
        )
