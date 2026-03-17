from __future__ import annotations

from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _draw_pixel_frame(painter: QPainter, rect: Any, *, border: QColor, inset: QColor) -> None:
    painter.setPen(QPen(border, 2))
    painter.drawRect(rect)
    inner_rect = rect.adjusted(6, 6, -6, -6)
    if inner_rect.width() > 0 and inner_rect.height() > 0:
        painter.setPen(QPen(inset, 1))
        painter.drawRect(inner_rect)


class FlickerLabel(QLabel):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("MarqueeTitle")
        self._phase_index = 0
        self._phases = ("bright", "dim", "bright", "bright")
        self.setProperty("flickerPhase", self._phases[0])
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(240)

    def _advance(self) -> None:
        self._phase_index = (self._phase_index + 1) % len(self._phases)
        self.setProperty("flickerPhase", self._phases[self._phase_index])
        _repolish(self)


class TexturedFrame(QFrame):
    def __init__(self, texture_mode: str = "scanlines") -> None:
        super().__init__()
        self._texture_mode = texture_mode

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        frame_rect = self.rect().adjusted(1, 1, -2, -2)
        _draw_pixel_frame(
            painter,
            frame_rect,
            border=QColor("#19dcff"),
            inset=QColor(255, 255, 255, 26),
        )

        if self._texture_mode == "scanlines":
            pen = QPen(QColor(255, 255, 255, 16))
            painter.setPen(pen)
            y = 1
            while y < self.height():
                painter.drawLine(8, y, self.width() - 9, y)
                y += 5
        elif self._texture_mode == "cartridge":
            pen = QPen(QColor(255, 255, 255, 14))
            painter.setPen(pen)
            x = -self.height() // 3
            while x < self.width():
                painter.drawLine(x, 0, x + self.height() // 2, self.height())
                x += 18
            painter.setPen(QPen(QColor("#ffd84a"), 1))
            for y in (10, 16, self.height() - 17, self.height() - 11):
                painter.drawLine(10, y, self.width() - 11, y)
        elif self._texture_mode == "bezel":
            pen = QPen(QColor(255, 255, 255, 12))
            painter.setPen(pen)
            for y in range(10, self.height() - 10, 4):
                painter.drawLine(10, y, self.width() - 11, y)
            painter.setPen(QPen(QColor("#31436e"), 1))
            for x in range(-self.height() // 2, self.width(), 20):
                painter.drawLine(x, 8, x + self.height() // 2, self.height() - 8)
            painter.fillRect(10, 10, 10, 10, QColor("#ffd84a"))
            painter.fillRect(self.width() - 20, 10, 10, 10, QColor("#ff33cc"))
            painter.fillRect(10, self.height() - 20, 10, 10, QColor("#19dcff"))
            painter.fillRect(self.width() - 20, self.height() - 20, 10, 10, QColor("#5cffb2"))

        pixel_pen = QPen(QColor("#19dcff"))
        painter.setPen(pixel_pen)
        painter.drawPoint(4, 4)
        painter.drawPoint(self.width() - 5, 4)
        painter.drawPoint(4, self.height() - 5)
        painter.drawPoint(self.width() - 5, self.height() - 5)


class SignalLamp(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("signalLamp", True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self.dot_label = QLabel("●")
        self.dot_label.setProperty("signalLampDot", True)
        self.text_block = QWidget()
        text_layout = QVBoxLayout(self.text_block)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        self.title_label = QLabel(label)
        self.title_label.setProperty("signalLampTitle", True)
        self.value_label = QLabel("OFF")
        self.value_label.setProperty("signalLampValue", True)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)
        layout.addWidget(self.dot_label)
        layout.addWidget(self.text_block)
        self.set_state("OFF", "idle")

    def set_state(self, value: str, tone: str) -> None:
        self.value_label.setText(value.upper())
        self.setProperty("tone", tone)
        self.dot_label.setProperty("tone", tone)
        self.value_label.setProperty("tone", tone)
        _repolish(self)
        _repolish(self.dot_label)
        _repolish(self.value_label)


class RuntimeDeck(TexturedFrame):
    def __init__(self) -> None:
        super().__init__("scanlines")
        self.setObjectName("RuntimeDeck")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        top_label = QLabel("Machine telemetry")
        top_label.setProperty("sectionLabel", True)
        layout.addWidget(top_label)

        lamp_row = QHBoxLayout()
        lamp_row.setContentsMargins(0, 0, 0, 0)
        lamp_row.setSpacing(8)
        self.cart_lamp = SignalLamp("Cart")
        self.data_lamp = SignalLamp("Data")
        self.safe_lamp = SignalLamp("Safe")
        self.lab_lamp = SignalLamp("Lab")
        for lamp in (self.cart_lamp, self.data_lamp, self.safe_lamp, self.lab_lamp):
            lamp_row.addWidget(lamp)
        layout.addLayout(lamp_row)

        self.hint_label = QLabel("LOAD PROFILE  |  BOOT RECORDER  |  PAPER FIRST")
        self.hint_label.setObjectName("MachineHint")
        layout.addWidget(self.hint_label)

    def set_status(
        self,
        *,
        cart_value: str,
        cart_tone: str,
        data_value: str,
        data_tone: str,
        safe_value: str,
        safe_tone: str,
        lab_value: str,
        lab_tone: str,
        hint: str,
    ) -> None:
        self.cart_lamp.set_state(cart_value, cart_tone)
        self.data_lamp.set_state(data_value, data_tone)
        self.safe_lamp.set_state(safe_value, safe_tone)
        self.lab_lamp.set_state(lab_value, lab_tone)
        self.hint_label.setText(hint.upper())


class ProfileBar(TexturedFrame):
    def __init__(self) -> None:
        super().__init__("bezel")
        self.setObjectName("ProfileBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        label = QLabel("Loaded profile")
        label.setProperty("sectionLabel", True)
        self.profile_selector = QComboBox()
        self.profile_selector.setObjectName("ProfileSelector")
        self.setup_button = QPushButton("Open setup")
        self.setup_button.setProperty("buttonRole", "secondary")
        layout.addWidget(label)
        layout.addWidget(self.profile_selector, stretch=1)
        layout.addWidget(self.setup_button)


class AppHeader(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ShellHeader")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        marquee = TexturedFrame("cartridge")
        marquee.setObjectName("ShellMarquee")
        marquee_layout = QVBoxLayout(marquee)
        marquee_layout.setContentsMargins(12, 10, 12, 10)
        marquee_layout.setSpacing(2)
        self.eyebrow_label = QLabel("Prediction cartridge loaded")
        self.eyebrow_label.setObjectName("MarqueeEyebrow")
        self.title_label = FlickerLabel("SUPERIOR")
        self.subtitle_label = QLabel("Paper bot OS")
        self.subtitle_label.setObjectName("MarqueeSubtitle")
        marquee_layout.addWidget(self.eyebrow_label)
        marquee_layout.addWidget(self.title_label)
        marquee_layout.addWidget(self.subtitle_label)

        self.runtime_deck = RuntimeDeck()
        top_row.addWidget(marquee, 3)
        top_row.addWidget(self.runtime_deck, 5)
        layout.addLayout(top_row)

        self.profile_bar = ProfileBar()
        layout.addWidget(self.profile_bar)

    def set_machine_state(
        self,
        *,
        cart_value: str,
        cart_tone: str,
        data_value: str,
        data_tone: str,
        safe_value: str,
        safe_tone: str,
        lab_value: str,
        lab_tone: str,
        hint: str,
    ) -> None:
        self.runtime_deck.set_status(
            cart_value=cart_value,
            cart_tone=cart_tone,
            data_value=data_value,
            data_tone=data_tone,
            safe_value=safe_value,
            safe_tone=safe_tone,
            lab_value=lab_value,
            lab_tone=lab_tone,
            hint=hint,
        )


class PrimaryNav(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PrimaryNav")
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setTabsClosable(False)


class ContentFrame(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ContentFrame")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)


class ShellStateCard(QFrame):
    def __init__(self, title: str, detail: str, tone: str) -> None:
        super().__init__()
        self.setProperty("stateOverlay", True)
        self.setProperty("tone", tone)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("heroText")
        self.detail_label = QLabel(detail)
        self.detail_label.setWordWrap(True)
        self.detail_label.setProperty("muted", True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.detail_label)

    def set_copy(self, title: str, detail: str, tone: str) -> None:
        self.title_label.setText(title)
        self.detail_label.setText(detail)
        self.setProperty("tone", tone)
        _repolish(self)


class EmptyState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Insert profile", "Create a profile to boot the recorder and start the paper-first loop.", "warning")


class WaitingState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Waiting on recorder", "Boot recorder to build the first local market sample.", "warning")


class RouteReadyState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Route ready", "A scanner route is staged. Paper it before thinking about live mode.", "active")


class BlockedState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Blocked", "One or more dependencies still need attention before the next action unlocks.", "locked")


class ErrorState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Error", "Superior hit an error. Review diagnostics and local logs before retrying.", "error")


class SplashScreen(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("Booting Superior", "Loading local profile state, recorder services, and scanner surfaces.", "active")


class StateOverlayHost(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("OverlayHost")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.state_card = SplashScreen()
        layout.addWidget(self.state_card)
        self.hide()

    def show_state(self, title: str, detail: str, tone: str) -> None:
        self.state_card.set_copy(title, detail, tone)
        self.show()

    def clear(self) -> None:
        self.hide()


class DesktopShell(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DesktopShell")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        self.header = AppHeader()
        self.nav = PrimaryNav()
        self.overlay_host = StateOverlayHost()
        self.content_frame = TexturedFrame("bezel")
        self.content_frame.setObjectName("ContentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.nav_frame = TexturedFrame("scanlines")
        self.nav_frame.setObjectName("NavFrame")
        self.nav_layout = QVBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(10, 10, 10, 10)
        self.nav_layout.setSpacing(0)
        self.nav_layout.addWidget(self.nav)
        self.content_layout.addWidget(self.overlay_host)
        self.content_layout.addWidget(self.nav_frame, stretch=1)
        layout.addWidget(self.header)
        layout.addWidget(self.content_frame, stretch=1)
