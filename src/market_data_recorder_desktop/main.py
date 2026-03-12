from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

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
    parser = argparse.ArgumentParser(description="Superior desktop app")
    parser.add_argument("--auto-launch", action="store_true", help="Launch from OS startup.")
    parser.add_argument("--profile-id", default=None, help="Optional profile ID to auto-run.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Launch the desktop app in smoke-test mode and exit after writing a JSON report.",
    )
    parser.add_argument(
        "--smoke-output",
        default=None,
        help="Optional JSON path used by --smoke-test to persist startup results.",
    )
    return parser


def create_window(
    *,
    auto_launch: bool = False,
    profile_id: str | None = None,
    smoke_test: bool = False,
) -> DesktopMainWindow:
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
        allow_setup_wizard_on_empty_profiles=not smoke_test,
        show_tray_icon=not smoke_test,
    )
    if auto_launch:
        window.handle_auto_launch(profile_id)
    return window


def _apply_style(app: QApplication) -> None:
    app.setApplicationName("Superior")
    app.setApplicationDisplayName("Superior")
    app.setOrganizationName("Superior")
    app.setFont(QFont("Segoe UI", 10))
    icon_path = _app_icon_path()
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setStyleSheet(
        """
        QWidget {
          color: #edf3ff;
        }
        QMainWindow {
          background: #05101f;
          color: #edf3ff;
        }
        QWidget#centralFrame, QWidget#pageFrame, QWizard, QWizardPage {
          background: #05101f;
        }
        QTabWidget::pane {
          border: 1px solid #163151;
          border-radius: 14px;
          background: #0a1528;
        }
        QTabBar::tab {
          background: #0d1b33;
          color: #93a8c8;
          padding: 11px 18px;
          border-top-left-radius: 10px;
          border-top-right-radius: 10px;
          margin-right: 6px;
          border: 1px solid #163151;
        }
        QTabBar::tab:selected {
          background: #10223f;
          color: #edf3ff;
        }
        QLabel#heroTitle {
          font-size: 26px;
          font-weight: 700;
          color: #f5fbff;
        }
        QLabel#heroText {
          font-size: 15px;
          color: #a6b8d4;
        }
        QPushButton {
          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4ec6ff, stop:1 #846dff);
          color: #04111f;
          border: 1px solid #8ed3ff;
          padding: 10px 16px;
          border-radius: 12px;
          font-weight: 600;
        }
        QPushButton:hover {
          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #73d4ff, stop:1 #9b88ff);
        }
        QPushButton:pressed {
          padding-top: 11px;
        }
        QGroupBox {
          border: 1px solid #163151;
          border-radius: 14px;
          margin-top: 12px;
          padding: 12px;
          background: #0d1b33;
          font-weight: 600;
        }
        QGroupBox::title {
          subcontrol-origin: margin;
          left: 10px;
          padding: 0 4px;
          color: #f5fbff;
        }
        QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget {
          border: 1px solid #1f3f69;
          border-radius: 10px;
          padding: 8px;
          background: #071425;
          color: #edf3ff;
          selection-background-color: #4ec6ff;
        }
        QListWidget::item:selected {
          background: #12335f;
        }
        QComboBox::drop-down {
          border: none;
        }
        QCheckBox {
          color: #c6d5eb;
        }
        QStatusBar {
          background: #071425;
          color: #9db3d3;
          border-top: 1px solid #163151;
        }
        """
    )


def _app_icon_path() -> Path | None:
    candidates: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if isinstance(meipass, str):
        candidates.append(Path(meipass) / "superior.ico")
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "superior.ico")
    candidates.append(Path(__file__).resolve().parents[2] / "packaging" / "windows" / "superior.ico")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _smoke_report(app: QApplication, window: DesktopMainWindow) -> dict[str, object]:
    return {
        "app_name": app.applicationName(),
        "display_name": app.applicationDisplayName(),
        "window_title": window.windowTitle(),
        "window_visible": window.isVisible(),
        "app_icon_present": not app.windowIcon().isNull(),
        "window_icon_present": not window.windowIcon().isNull(),
        "system_tray_available": QSystemTrayIcon.isSystemTrayAvailable(),
    }


def _run_smoke_test(
    app: QApplication,
    window: DesktopMainWindow,
    *,
    output_path: Path | None,
) -> int:
    result: dict[str, object] = {}
    error_message: str | None = None

    def finish() -> None:
        nonlocal result, error_message
        try:
            result = _smoke_report(app, window)
            if output_path is not None:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        except Exception as exc:  # pragma: no cover - smoke mode failure path
            error_message = str(exc)
        finally:
            window.close()
            app.quit()

    QTimer.singleShot(400, finish)
    exit_code = app.exec()
    if error_message is not None:
        raise RuntimeError(error_message)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.smoke_test and args.smoke_output is None:
        parser.error("--smoke-output is required when --smoke-test is used.")
    app = QApplication(sys.argv if argv is None else ["Superior", *argv])
    _apply_style(app)
    window = create_window(auto_launch=args.auto_launch, profile_id=args.profile_id, smoke_test=args.smoke_test)
    window.show()
    if args.smoke_test:
        return _run_smoke_test(
            app,
            window,
            output_path=Path(args.smoke_output) if args.smoke_output is not None else None,
        )
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
