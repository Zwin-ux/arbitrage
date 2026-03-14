from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path


class StartupManager(ABC):
    @abstractmethod
    def supported(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_enabled(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError


class UnsupportedStartupManager(StartupManager):
    def supported(self) -> bool:
        return False

    def is_enabled(self) -> bool:
        return False

    def set_enabled(self, enabled: bool) -> None:
        return None

    def description(self) -> str:
        return "Auto-start is not available on this platform."


class WindowsStartupManager(StartupManager):
    def __init__(self, startup_dir: Path | None = None):
        default_dir = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        self._startup_dir = startup_dir or default_dir
        self._launcher_path = self._startup_dir / "market-data-recorder-app.cmd"

    def supported(self) -> bool:
        return sys.platform.startswith("win")

    def is_enabled(self) -> bool:
        return self._launcher_path.exists()

    def set_enabled(self, enabled: bool) -> None:
        if not self.supported():
            return
        self._startup_dir.mkdir(parents=True, exist_ok=True)
        if enabled:
            self._launcher_path.write_text(self._launcher_contents(), encoding="utf-8")
        elif self._launcher_path.exists():
            self._launcher_path.unlink()

    def description(self) -> str:
        return "Run Superior at login using the current executable."

    def _launcher_contents(self) -> str:
        if getattr(sys, "frozen", False):
            command = f'"{sys.executable}" --auto-launch'
        else:
            command = f'"{sys.executable}" -m market_data_recorder_desktop.main --auto-launch'
        return f"@echo off\r\nstart \"\" {command}\r\n"
