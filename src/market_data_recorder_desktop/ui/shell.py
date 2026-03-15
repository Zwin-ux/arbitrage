from __future__ import annotations

from PySide6.QtCore import Qt
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


class ProfileBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        label = QLabel("Active profile")
        label.setProperty("sectionLabel", True)
        self.profile_selector = QComboBox()
        self.setup_button = QPushButton("Open guided setup")
        self.setup_button.setProperty("buttonRole", "secondary")
        layout.addWidget(label)
        layout.addWidget(self.profile_selector, stretch=1)
        layout.addWidget(self.setup_button)


class AppHeader(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ShellPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(14)
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        self.title_label = QLabel("Superior")
        self.title_label.setObjectName("heroTitle")
        self.subtitle_label = QLabel("Paper-first market scanner")
        self.subtitle_label.setObjectName("heroText")
        title_block.addWidget(self.title_label)
        title_block.addWidget(self.subtitle_label)
        self.profile_bar = ProfileBar()
        top_row.addLayout(title_block)
        top_row.addWidget(self.profile_bar, stretch=1)
        layout.addLayout(top_row)


class PrimaryNav(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setTabsClosable(False)


class ContentFrame(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ContentFrame")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
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


class EmptyState(ShellStateCard):
    def __init__(self) -> None:
        super().__init__("First launch", "Create a profile to boot the recorder and start the paper-first loop.", "warning")


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
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        self.header = AppHeader()
        self.nav = PrimaryNav()
        self.overlay_host = StateOverlayHost()
        self.content_frame = ContentFrame()
        layout.addWidget(self.header)
        layout.addWidget(self.overlay_host)
        layout.addWidget(self.nav, stretch=1)
