from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from market_data_recorder_desktop.app_types import SetupCompletionRoute, SetupStepState

from .primitives import CommandFooter, PixelPanel, repolish


class SetupPhaseCard(PixelPanel):
    def __init__(self, label: str) -> None:
        super().__init__("STEP", label, tone="idle", compact=True)
        self.value = QLabel("WAIT")
        self.value.setProperty("panelTitle", True)
        self.detail = QLabel("WAITING")
        self.detail.setProperty("panelToneText", True)
        self.body_layout.addWidget(self.value)
        self.body_layout.addWidget(self.detail)

    def set_state(self, state: SetupStepState) -> None:
        if state.active:
            value = "ACTIVE"
            tone = "active"
            detail = "CURRENT STEP"
        elif state.complete:
            value = "CLEAR"
            tone = "success"
            detail = "DONE"
        else:
            value = "WAIT"
            tone = "idle"
            detail = "PENDING"
        self.value.setText(value)
        self.detail.setText(detail)
        self.set_tone(tone)
        repolish(self.value)
        repolish(self.detail)


class SetupStepper(QWidget):
    def __init__(self, labels: list[str]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.phase_label = QLabel("SETUP STEPS")
        self.phase_label.setProperty("sectionLabel", True)
        layout.addWidget(self.phase_label)
        self._cards: list[SetupPhaseCard] = []
        for label in labels:
            card = SetupPhaseCard(label)
            self._cards.append(card)
            layout.addWidget(card)
        self.command_footer = CommandFooter(
            [
                ("B", "BACK"),
                ("A", "NEXT"),
                ("X", "REVIEW"),
                ("START", "FINISH"),
                ("SELECT", "GUIDE"),
            ]
        )
        layout.addWidget(self.command_footer)
        layout.addStretch(1)

    def set_steps(self, steps: list[SetupStepState]) -> None:
        for card, state in zip(self._cards, steps, strict=False):
            card.set_state(state)


class SetupCompletionState(PixelPanel):
    def __init__(self) -> None:
        super().__init__("STEP 06", "READY", tone="active")
        self.route_title = QLabel("HOME READY")
        self.route_title.setObjectName("heroText")
        self.route_detail = QLabel("HOME OPENS WITH RECORDER READY.")
        self.route_detail.setWordWrap(True)
        self.route_detail.setProperty("muted", True)
        self.body_layout.addWidget(self.route_title)
        self.body_layout.addWidget(self.route_detail)

    def set_route(self, route: SetupCompletionRoute) -> None:
        self.route_title.setText(route.title.upper())
        self.route_detail.setText(route.detail.upper())
