from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from market_data_recorder_desktop.app_types import SemanticStateColor


def repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class PixelPanel(QFrame):
    def __init__(self, sector: str, title: str, *, tone: str = "idle", compact: bool = False) -> None:
        super().__init__()
        self.setProperty("pixelPanel", True)
        self.setProperty("tone", tone)
        self.setProperty("compact", compact)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        self.sector_label = QLabel(sector)
        self.sector_label.setProperty("panelSector", True)
        self.title_label = QLabel(title)
        self.title_label.setProperty("panelTitle", True)
        self.tone_label = QLabel(tone)
        self.tone_label.setProperty("panelToneText", True)
        self.tone_label.setProperty("tone", tone)
        header_layout.addWidget(self.sector_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.tone_label)
        layout.addWidget(header)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(8 if compact else 16)
        layout.addWidget(self.body)

    def set_tone(self, tone: str) -> None:
        self.setProperty("tone", tone)
        self.tone_label.setText(tone.upper())
        self.tone_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.tone_label)


class TelemetryLamp(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("telemetryLamp", True)
        self.setProperty("tone", "idle")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        self.dot_label = QLabel("[]")
        self.dot_label.setProperty("telemetryLampDot", True)
        self.dot_label.setProperty("tone", "idle")
        text = QWidget()
        text_layout = QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        self.title_label = QLabel(label)
        self.title_label.setProperty("telemetryLampTitle", True)
        self.value_label = QLabel("OFFLINE")
        self.value_label.setProperty("telemetryLampValue", True)
        self.value_label.setProperty("tone", "idle")
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)
        layout.addWidget(self.dot_label)
        layout.addWidget(text)

    def set_state(self, value: str, *, tone: SemanticStateColor) -> None:
        self.value_label.setText(value.upper())
        self.setProperty("tone", tone)
        self.dot_label.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.dot_label)
        repolish(self.value_label)


class StateChip(QLabel):
    def __init__(self, label: str) -> None:
        super().__init__(label.upper())
        self.setProperty("stateChip", True)
        self.setProperty("tone", "idle")

    def set_tone(self, tone: SemanticStateColor, value: str) -> None:
        self.setText(value.upper())
        self.setProperty("tone", tone)
        repolish(self)


class StatusModule(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("statusModule", True)
        self.setProperty("tone", "idle")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.title_label = QLabel(label)
        self.title_label.setProperty("statusModuleTitle", True)
        self.value_label = QLabel("IDLE")
        self.value_label.setProperty("statusModuleValue", True)
        self.value_label.setProperty("tone", "idle")
        self.detail_label = QLabel("WAITING FOR INPUT.")
        self.detail_label.setProperty("statusModuleDetail", True)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)

    def set_state(self, value: str, detail: str, *, tone: SemanticStateColor) -> None:
        self.value_label.setText(value.upper())
        self.detail_label.setText(detail.upper())
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.value_label)


class MeterBar(QProgressBar):
    def __init__(self) -> None:
        super().__init__()
        self.setProperty("meterBar", True)
        self.setRange(0, 4)
        self.setValue(0)
        self.setTextVisible(False)
        self.setFixedHeight(16)


class RiskBadge(QLabel):
    def __init__(self) -> None:
        super().__init__("LOCKED")
        self.setProperty("riskBadge", True)
        self.setProperty("tone", "locked")

    def set_state(self, text: str, tone: SemanticStateColor) -> None:
        self.setText(text.upper())
        self.setProperty("tone", tone)
        repolish(self)


class StatCell(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setProperty("statCell", True)
        self.setProperty("tone", "idle")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        self.title_label = QLabel(title)
        self.title_label.setProperty("statCellTitle", True)
        self.value_label = QLabel(value)
        self.value_label.setProperty("statCellValue", True)
        self.value_label.setProperty("tone", "idle")
        self.detail_label = QLabel("")
        self.detail_label.setProperty("statCellDetail", True)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)

    def set_value(self, value: str, *, detail: str = "", tone: SemanticStateColor = "idle") -> None:
        self.value_label.setText(value.upper())
        self.detail_label.setText(detail.upper())
        self.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        repolish(self)
        repolish(self.value_label)


class InsetConsolePanel(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setProperty("consoleRole", "system")
        self.setMaximumHeight(144)


class CommandFooter(QFrame):
    def __init__(self, commands: list[tuple[str, str]]) -> None:
        super().__init__()
        self.setProperty("commandFooter", True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.command_labels: list[QLabel] = []
        for key, action in commands:
            label = QLabel(f"{key} {action}".upper())
            label.setProperty("commandKey", True)
            layout.addWidget(label)
            self.command_labels.append(label)
        layout.addStretch(1)
