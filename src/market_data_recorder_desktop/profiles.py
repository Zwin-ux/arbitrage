from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .app_types import AppProfile, default_run_presets
from .paths import AppPaths


class ProfilesDocument(BaseModel):
    schema_version: int = 1
    profiles: list[AppProfile] = Field(default_factory=list)


class ProfileStore:
    def __init__(self, paths: AppPaths):
        self._paths = paths
        self._paths.ensure()
        self._preset_ids = {preset.id for preset in default_run_presets()}

    @property
    def profiles_path(self) -> Path:
        return self._paths.profiles_path

    def list_profiles(self) -> list[AppProfile]:
        return self._load().profiles

    def get_profile(self, profile_id: str) -> AppProfile | None:
        for profile in self.list_profiles():
            if profile.id == profile_id:
                return profile
        return None

    def save_profile(self, profile: AppProfile) -> AppProfile:
        document = self._load()
        now = datetime.now(timezone.utc)
        normalized = profile.model_copy(deep=True)
        if not normalized.id:
            normalized.id = str(uuid.uuid4())
        if normalized.default_preset not in self._preset_ids:
            normalized.default_preset = "continuous-record"
        normalized.data_dir.mkdir(parents=True, exist_ok=True)
        normalized.updated_at = now
        if normalized.auto_start:
            for existing in document.profiles:
                existing.auto_start = False
        for index, existing in enumerate(document.profiles):
            if existing.id == normalized.id:
                document.profiles[index] = normalized
                self._write(document)
                return normalized
        document.profiles.append(normalized)
        self._write(document)
        return normalized

    def create_profile(
        self,
        *,
        display_name: str,
        template: str,
        enabled_venues: list[str],
        market_filters: list[str] | None = None,
        auto_start: bool = False,
        start_minimized: bool = False,
        default_preset: str = "continuous-record",
        data_dir: Path | None = None,
        notes: str | None = None,
    ) -> AppProfile:
        profile_id = str(uuid.uuid4())
        target_dir = data_dir or (self._paths.data_dir / profile_id)
        profile = AppProfile(
            id=profile_id,
            display_name=display_name,
            template=template,
            data_dir=target_dir,
            enabled_venues=enabled_venues,
            market_filters=market_filters or [],
            auto_start=auto_start,
            start_minimized=start_minimized,
            default_preset=default_preset,
            notes=notes,
        )
        return self.save_profile(profile)

    def delete_profile(self, profile_id: str) -> None:
        document = self._load()
        document.profiles = [profile for profile in document.profiles if profile.id != profile_id]
        self._write(document)

    def duplicate_profile(self, profile_id: str, *, new_name: str | None = None) -> AppProfile:
        profile = self.get_profile(profile_id)
        if profile is None:
            raise KeyError(f"Unknown profile: {profile_id}")
        duplicate = profile.model_copy(deep=True)
        duplicate.id = str(uuid.uuid4())
        duplicate.display_name = new_name or f"{profile.display_name} Copy"
        duplicate.auto_start = False
        duplicate.data_dir = self._paths.data_dir / duplicate.id
        now = datetime.now(timezone.utc)
        duplicate.created_at = now
        duplicate.updated_at = now
        return self.save_profile(duplicate)

    def export_profile(self, profile_id: str, output_path: Path) -> Path:
        profile = self.get_profile(profile_id)
        if profile is None:
            raise KeyError(f"Unknown profile: {profile_id}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return output_path

    def import_profile(self, input_path: Path) -> AppProfile:
        imported = AppProfile.model_validate_json(input_path.read_text(encoding="utf-8"))
        imported.id = str(uuid.uuid4())
        imported.auto_start = False
        if not imported.data_dir.is_absolute():
            imported.data_dir = self._paths.data_dir / imported.id
        return self.save_profile(imported)

    def auto_start_profile(self) -> AppProfile | None:
        for profile in self.list_profiles():
            if profile.auto_start:
                return profile
        return None

    def _load(self) -> ProfilesDocument:
        if not self._paths.profiles_path.exists():
            return ProfilesDocument()
        payload = json.loads(self._paths.profiles_path.read_text(encoding="utf-8"))
        document = ProfilesDocument.model_validate(payload)
        if document.schema_version != 1:
            return ProfilesDocument(profiles=document.profiles)
        return document

    def _write(self, document: ProfilesDocument) -> None:
        self._paths.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.profiles_path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
