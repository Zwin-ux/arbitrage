from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from market_data_recorder_desktop.app_types import SetupCompletionRoute, SetupStepState


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class SetupStepCard(QFrame):
    def __init__(self, label: str, description: str = "") -> None:
        super().__init__()
        self.setProperty("stateCard", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)
        self.label = QLabel(label)
        self.label.setProperty("stateCardTitle", True)
        self.value = QLabel("WAITING")
        self.value.setProperty("stateCardValue", True)
        self.detail = QLabel(description)
        self.detail.setProperty("stateCardDetail", True)
        self.detail.setWordWrap(True)
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)

    def set_state(self, state: SetupStepState) -> None:
        if state.active:
            value = "ACTIVE"
            tone = "active"
        elif state.complete:
            value = "DONE"
            tone = "success"
        else:
            value = "WAIT"
            tone = "idle"
        self.value.setText(value)
        self.setProperty("tone", tone)
        self.value.setProperty("tone", tone)
        _repolish(self)
        _repolish(self.value)


class SetupStepper(QWidget):
    def __init__(self, labels: list[str]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        title = QLabel("Setup sequence")
        title.setProperty("sectionLabel", True)
        layout.addWidget(title)
        self._cards: list[SetupStepCard] = []
        for label in labels:
            card = SetupStepCard(label)
            self._cards.append(card)
            layout.addWidget(card)
        layout.addStretch(1)

    def set_steps(self, steps: list[SetupStepState]) -> None:
        for card, state in zip(self._cards, steps, strict=False):
            card.set_state(state)


class SetupCompletionState(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setProperty("stateCard", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        title = QLabel("Launch route")
        title.setProperty("sectionLabel", True)
        self.route_title = QLabel("Hangar recorder highlight")
        self.route_title.setObjectName("heroText")
        self.route_detail = QLabel(
            "Superior will open in Hangar with Boot recorder framed as the next action."
        )
        self.route_detail.setWordWrap(True)
        self.route_detail.setProperty("muted", True)
        layout.addWidget(title)
        layout.addWidget(self.route_title)
        layout.addWidget(self.route_detail)

    def set_route(self, route: SetupCompletionRoute) -> None:
        self.route_title.setText(route.title)
        self.route_detail.setText(route.detail)
