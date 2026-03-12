from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from market_data_recorder_desktop.paths import AppPaths

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@dataclass
class FakeKeyring:
    store: dict[tuple[str, str], str] = field(default_factory=dict)

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.store.get((service_name, username))

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.store[(service_name, username)] = password

    def delete_password(self, service_name: str, username: str) -> None:
        self.store.pop((service_name, username), None)


@pytest.fixture
def fake_keyring() -> FakeKeyring:
    return FakeKeyring()


@pytest.fixture
def app_paths(tmp_path: Path) -> AppPaths:
    return AppPaths(
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        log_dir=tmp_path / "logs",
        exports_dir=tmp_path / "exports",
        profiles_path=tmp_path / "config" / "profiles.json",
    )
