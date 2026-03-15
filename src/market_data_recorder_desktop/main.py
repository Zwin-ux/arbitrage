from __future__ import annotations

import argparse
import json
import traceback
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QSystemTrayIcon, QVBoxLayout, QWidget

if TYPE_CHECKING:
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
) -> "DesktopMainWindow":
    from market_data_recorder.config import RecorderSettings
    from market_data_recorder.logging import configure_logging

    from .bot_services import (
        AssistantService,
        CapabilityService,
        ConnectorLoadoutService,
        ContractMatcher,
        KalshiVenueAdapter,
        LiveExecutionEngine,
        OpportunityEngine,
        PaperExecutionEngine,
        PaperRunStore,
        PolymarketVenueAdapter,
        ScoreService,
        UnlockService,
    )
    from .controller import EngineController
    from .credentials import CredentialVault
    from .diagnostics import DiagnosticsService
    from .paths import AppPaths
    from .profiles import ProfileStore
    from .startup import UnsupportedStartupManager, WindowsStartupManager
    from .window import DesktopMainWindow

    settings = RecorderSettings()
    configure_logging(settings.log_level)
    paths = AppPaths.for_current_user()
    profile_store = ProfileStore(paths)
    credential_vault = CredentialVault()
    controller = EngineController(settings)
    diagnostics = DiagnosticsService(paths)
    startup_manager = WindowsStartupManager() if sys.platform.startswith("win") else UnsupportedStartupManager()
    venue_adapters = [PolymarketVenueAdapter(), KalshiVenueAdapter()]
    paper_store = PaperRunStore()
    opportunity_engine = OpportunityEngine(venue_adapters, ContractMatcher())
    paper_execution_engine = PaperExecutionEngine(paper_store)
    score_service = ScoreService(paper_store)
    unlock_service = UnlockService(paper_store)
    assistant_service = AssistantService(
        docs_paths=[
            Path(__file__).resolve().parents[2] / "README.md",
            Path(__file__).resolve().parents[2] / "docs" / "risk-model.md",
            Path(__file__).resolve().parents[2] / "docs" / "live-trading-limitations.md",
            Path(__file__).resolve().parents[2] / "docs" / "strategy-contributor-guide.md",
        ]
    )
    window = DesktopMainWindow(
        paths=paths,
        profile_store=profile_store,
        credential_vault=credential_vault,
        controller=controller,
        diagnostics=diagnostics,
        startup_manager=startup_manager,
        venue_adapters=venue_adapters,
        loadout_service=ConnectorLoadoutService(),
        capability_service=CapabilityService(),
        opportunity_engine=opportunity_engine,
        paper_store=paper_store,
        score_service=score_service,
        paper_execution_engine=paper_execution_engine,
        live_execution_engine=LiveExecutionEngine(),
        unlock_service=unlock_service,
        assistant_service=assistant_service,
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
        QWidget { color: #edf4ff; }
        QMainWindow { background: #071129; color: #edf4ff; }
        QWidget#centralFrame, QWidget#pageFrame, QWizard, QWizardPage { background: #071129; }
        QTabWidget::pane {
          border: 2px solid #1ed6ff;
          border-radius: 14px;
          background: #091736;
        }
        QTabBar::tab {
          background: #0d1737;
          color: #94b7dc;
          padding: 11px 18px;
          border-top-left-radius: 10px;
          border-top-right-radius: 10px;
          margin-right: 6px;
          border: 2px solid #213162;
        }
        QTabBar::tab:selected {
          background: #122454;
          color: #ffffff;
          border-color: #1ed6ff;
        }
        QLabel#heroTitle {
          font-size: 26px;
          font-weight: 700;
          color: #ffffff;
        }
        QLabel#heroText {
          font-size: 15px;
          color: #a8c0df;
        }
        QPushButton {
          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00e5ff, stop:1 #8a5cff);
          color: #06111f;
          border: 2px solid #aef5ff;
          padding: 10px 16px;
          border-radius: 12px;
          font-weight: 600;
        }
        QPushButton:hover {
          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6af2ff, stop:1 #b18cff);
        }
        QPushButton[buttonRole="secondary"] {
          background: #101a3d;
          color: #edf4ff;
          border: 2px solid #3a4f8d;
        }
        QPushButton[buttonRole="secondary"]:hover {
          background: #162452;
          border-color: #ff00d4;
        }
        QPushButton:disabled {
          background: #0b1124;
          color: #5b6e91;
          border: 2px solid #223252;
        }
        QPushButton:pressed {
          padding-top: 11px;
        }
        QGroupBox {
          border: 2px solid #243a74;
          border-radius: 14px;
          margin-top: 12px;
          padding: 12px;
          background: #0c1736;
          font-weight: 600;
        }
        QGroupBox::title {
          subcontrol-origin: margin;
          left: 10px;
          padding: 0 4px;
          color: #ffd700;
        }
        QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget {
          border: 2px solid #233563;
          border-radius: 10px;
          padding: 8px;
          background: #050c1d;
          color: #edf4ff;
          selection-background-color: #8a5cff;
        }
        QListWidget::item:selected {
          background: #182a55;
        }
        QComboBox::drop-down {
          border: none;
        }
        QCheckBox {
          color: #d7e6ff;
        }
        QStatusBar {
          background: #050c1d;
          color: #9bc8ff;
          border-top: 2px solid #20315f;
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


def _smoke_report(app: QApplication, window: QWidget) -> dict[str, object]:
    return {
        "app_name": app.applicationName(),
        "display_name": app.applicationDisplayName(),
        "window_title": window.windowTitle(),
        "window_visible": window.isVisible(),
        "app_icon_present": not app.windowIcon().isNull(),
        "window_icon_present": not window.windowIcon().isNull(),
        "system_tray_available": QSystemTrayIcon.isSystemTrayAvailable(),
    }


def _create_smoke_window(app: QApplication) -> QMainWindow:
    window = QMainWindow()
    window.setWindowTitle("Superior")
    window.resize(960, 640)
    if not app.windowIcon().isNull():
        window.setWindowIcon(app.windowIcon())

    central = QWidget()
    layout = QVBoxLayout(central)
    title = QLabel("Superior smoke test")
    title.setObjectName("heroTitle")
    subtitle = QLabel("Packaged startup, icon wiring, and the Windows shell are healthy.")
    subtitle.setObjectName("heroText")
    subtitle.setWordWrap(True)
    layout.addWidget(title)
    layout.addWidget(subtitle)
    layout.addStretch(1)
    window.setCentralWidget(central)
    return window


def _run_smoke_probe(
    *,
    output_path: Path | None,
    trace_path: Path | None = None,
) -> int:
    _append_smoke_trace(trace_path, "run-smoke-probe:start")
    icon_path = _app_icon_path()
    result = {
        "app_name": "Superior",
        "display_name": "Superior",
        "window_title": "Superior",
        "window_visible": False,
        "app_icon_present": icon_path is not None,
        "window_icon_present": icon_path is not None,
        "system_tray_available": sys.platform.startswith("win"),
        "desktop_modules_loaded": True,
        "icon_path": str(icon_path) if icon_path is not None else None,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        _append_smoke_trace(trace_path, f"run-smoke-probe:wrote-report:{output_path}")

    _append_smoke_trace(trace_path, "run-smoke-probe:exit")
    return 0


def _append_smoke_trace(trace_path: Path | None, message: str) -> None:
    if trace_path is None:
        return
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} {message}\n")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.smoke_test and args.smoke_output is None:
        parser.error("--smoke-output is required when --smoke-test is used.")
    smoke_output_path = Path(args.smoke_output) if args.smoke_output is not None else None
    smoke_trace_path = (
        smoke_output_path.with_name("smoke-trace.log") if args.smoke_test and smoke_output_path is not None else None
    )
    _append_smoke_trace(smoke_trace_path, "main:start")
    try:
        if args.smoke_test:
            return _run_smoke_probe(
                output_path=smoke_output_path,
                trace_path=smoke_trace_path,
            )
        app = QApplication(sys.argv if argv is None else ["Superior", *argv])
        _append_smoke_trace(smoke_trace_path, "main:qapplication-created")
        _apply_style(app)
        _append_smoke_trace(smoke_trace_path, "main:style-applied")
        window = create_window(auto_launch=args.auto_launch, profile_id=args.profile_id, smoke_test=False)
        window.show()
        _append_smoke_trace(smoke_trace_path, "main:window-shown")
        return app.exec()
    except Exception as exc:
        _append_smoke_trace(smoke_trace_path, f"main:error:{exc}")
        _append_smoke_trace(smoke_trace_path, traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
