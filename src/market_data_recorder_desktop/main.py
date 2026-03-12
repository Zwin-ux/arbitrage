from __future__ import annotations

import argparse
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from market_data_recorder.config import RecorderSettings
from market_data_recorder.logging import configure_logging

from .controller import EngineController
from .credentials import CredentialVault
from .diagnostics import DiagnosticsService
from .paths import AppPaths
from .profiles import ProfileStore
from .startup import UnsupportedStartupManager, WindowsStartupManager
from .window import DesktopMainWindow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="market-data-recorder desktop app")
    parser.add_argument("--auto-launch", action="store_true", help="Launch from OS startup.")
    parser.add_argument("--profile-id", default=None, help="Optional profile ID to auto-run.")
    return parser


def create_window(*, auto_launch: bool = False, profile_id: str | None = None) -> DesktopMainWindow:
    settings = RecorderSettings()
    configure_logging(settings.log_level)
    paths = AppPaths.for_current_user()
    profile_store = ProfileStore(paths)
    credential_vault = CredentialVault()
    controller = EngineController(settings)
    diagnostics = DiagnosticsService(paths)
    startup_manager = WindowsStartupManager() if sys.platform.startswith("win") else UnsupportedStartupManager()
    window = DesktopMainWindow(
        paths=paths,
        profile_store=profile_store,
        credential_vault=credential_vault,
        controller=controller,
        diagnostics=diagnostics,
        startup_manager=startup_manager,
    )
    if auto_launch:
        window.handle_auto_launch(profile_id)
    return window


def _apply_style(app: QApplication) -> None:
    app.setApplicationName("market-data-recorder")
    app.setOrganizationName("OpenRecorder")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(
        """
        QMainWindow {
          background: #f7f2e7;
          color: #102542;
        }
        QTabWidget::pane {
          border: 1px solid #d9d1c1;
          border-radius: 10px;
          background: #fffdf9;
        }
        QTabBar::tab {
          background: #ede4d3;
          padding: 10px 16px;
          border-top-left-radius: 8px;
          border-top-right-radius: 8px;
          margin-right: 4px;
        }
        QTabBar::tab:selected {
          background: #fffdf9;
          color: #102542;
        }
        QLabel#heroTitle {
          font-size: 24px;
          font-weight: 700;
          color: #102542;
        }
        QLabel#heroText {
          font-size: 15px;
          line-height: 1.4;
        }
        QPushButton {
          background: #0f6cbd;
          color: white;
          border: none;
          padding: 10px 16px;
          border-radius: 10px;
          font-weight: 600;
        }
        QPushButton:hover {
          background: #0b568f;
        }
        QGroupBox {
          border: 1px solid #d9d1c1;
          border-radius: 10px;
          margin-top: 12px;
          padding: 12px;
          background: #fffdf9;
          font-weight: 600;
        }
        QGroupBox::title {
          subcontrol-origin: margin;
          left: 10px;
          padding: 0 4px;
        }
        QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget {
          border: 1px solid #cbbfa8;
          border-radius: 8px;
          padding: 8px;
          background: white;
        }
        QStatusBar {
          background: #ede4d3;
        }
        """
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    app = QApplication(sys.argv if argv is None else ["market-data-recorder-app", *argv])
    _apply_style(app)
    window = create_window(auto_launch=args.auto_launch, profile_id=args.profile_id)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
