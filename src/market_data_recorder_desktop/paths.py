from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from platformdirs import PlatformDirs


class AppPaths(BaseModel):
    config_dir: Path
    data_dir: Path
    log_dir: Path
    exports_dir: Path
    profiles_path: Path

    @classmethod
    def for_current_user(cls) -> "AppPaths":
        dirs = PlatformDirs(appname="market-data-recorder", appauthor="OpenRecorder", roaming=True)
        config_dir = Path(dirs.user_config_dir)
        data_dir = Path(dirs.user_data_dir)
        log_dir = Path(dirs.user_log_dir)
        exports_dir = data_dir / "exports"
        return cls(
            config_dir=config_dir,
            data_dir=data_dir,
            log_dir=log_dir,
            exports_dir=exports_dir,
            profiles_path=config_dir / "profiles.json",
        )

    def ensure(self) -> None:
        for path in (self.config_dir, self.data_dir, self.log_dir, self.exports_dir):
            path.mkdir(parents=True, exist_ok=True)
