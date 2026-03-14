from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from .app_types import AppProfile, CredentialStatus, EngineStatus
from . import __version__
from .paths import AppPaths


class DiagnosticsService:
    def __init__(self, paths: AppPaths):
        self._paths = paths

    def export_bundle(
        self,
        *,
        profile: AppProfile | None,
        status: EngineStatus,
        credential_statuses: list[CredentialStatus],
        output_path: Path,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "app_version": self.app_version(),
            "platform": platform.platform(),
            "paths": self._paths.model_dump(mode="json"),
            "profile": profile.model_dump(mode="json") if profile is not None else None,
            "status": status.model_dump(mode="json"),
            "credential_statuses": [item.model_dump(mode="json") for item in credential_statuses],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def diagnostics_text(
        self,
        *,
        profile: AppProfile | None,
        status: EngineStatus,
        credential_statuses: list[CredentialStatus],
    ) -> str:
        lines = [
            f"App version: {self.app_version()}",
            f"Platform: {platform.platform()}",
            f"Config dir: {self._paths.config_dir}",
            f"Data dir: {self._paths.data_dir}",
            f"Log dir: {self._paths.log_dir}",
            f"Exports dir: {self._paths.exports_dir}",
            f"Engine state: {status.state}",
            f"Last message: {status.last_message}",
        ]
        if profile is not None:
            lines.extend(
                [
                    f"Brand: {profile.brand_name}",
                    f"Active profile: {profile.display_name}",
                    f"Profile data dir: {profile.data_dir}",
                    f"Default preset: {profile.default_preset}",
                    f"Primary goal: {profile.primary_goal}",
                    f"Primary mission: {profile.primary_mission}",
                    f"Experience level: {profile.experience_level}",
                    f"Guided mode: {profile.guided_mode}",
                    f"Lab enabled: {profile.lab_enabled}",
                    f"Live unlocked: {profile.live_unlocked}",
                    f"AI coach enabled: {profile.ai_coach_enabled}",
                    f"Risk policy: {profile.risk_policy_id}",
                ]
            )
        if status.summary is not None:
            lines.extend(
                [
                    f"DB path: {status.summary.db_path}",
                    f"Raw messages: {status.summary.raw_messages}",
                    f"Book snapshots: {status.summary.book_snapshots}",
                    f"Health events: {status.summary.health_events}",
                    f"Latest warning: {status.summary.latest_warning or 'None'}",
                ]
            )
        lines.append("Credentials:")
        for item in credential_statuses:
            lines.append(f"  - {item.provider_label}: {item.status} ({item.message})")
        return "\n".join(lines)

    @staticmethod
    def app_version() -> str:
        return __version__
