from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from market_data_recorder_desktop.app_types import SemanticStateColor


def repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class SignalBadge(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("signalBadge", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        self.title_label = QLabel(label)
        self.title_label.setProperty("signalTitle", True)
        self.value_label = QLabel("OFFLINE")
        self.value_label.setProperty("signalValue", True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.set_state("offline", tone="locked")

    def set_state(self, value: str, *, tone: SemanticStateColor) -> None:
        self.value_label.setText(value.upper())
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.value_label)


class StateCard(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setProperty("stateCard", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        self.title_label = QLabel(title)
        self.title_label.setProperty("stateCardTitle", True)
        self.value_label = QLabel("IDLE")
        self.value_label.setProperty("stateCardValue", True)
        self.detail_label = QLabel("")
        self.detail_label.setProperty("stateCardDetail", True)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)
        self.set_state("idle", "Waiting for input.", tone="idle")

    def set_state(self, value: str, detail: str, *, tone: SemanticStateColor) -> None:
        self.value_label.setText(value.upper())
        self.detail_label.setText(detail)
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.value_label)


class StatCell(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setProperty("statCell", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        self.title_label = QLabel(title)
        self.title_label.setProperty("statCellTitle", True)
        self.value_label = QLabel(value)
        self.value_label.setProperty("statCellValue", True)
        self.detail_label = QLabel("")
        self.detail_label.setProperty("statCellDetail", True)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)

    def set_value(self, value: str, *, detail: str = "", tone: SemanticStateColor = "idle") -> None:
        self.value_label.setText(value)
        self.detail_label.setText(detail)
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.value_label)
