from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .app_types import AppProfile, ConnectorId, ModuleId, default_run_presets
from .paths import AppPaths


class ProfilesDocument(BaseModel):
    schema_version: int = 3
    profiles: list[AppProfile] = Field(default_factory=list)


def _default_connectors(enabled_venues: list[str], ai_coach_enabled: bool) -> list[ConnectorId]:
    connectors: list[ConnectorId] = ["polymarket"] if "Polymarket" in enabled_venues else []
    if "Kalshi" in enabled_venues:
        connectors.append("kalshi")
    if ai_coach_enabled:
        connectors.append("coach")
    return connectors


def _default_modules(enabled_venues: list[str], lab_enabled: bool) -> list[ModuleId]:
    modules: list[ModuleId] = ["internal-binary"]
    if "Kalshi" in enabled_venues:
        modules.append("cross-venue-complement")
    else:
        modules.append("cross-venue-complement")
    if lab_enabled:
        modules.extend(["negative-risk-basket", "maker-rebate-lab"])
    return modules


def _primary_mission(primary_goal: str, enabled_venues: list[str]) -> str:
    if primary_goal == "paper_arbitrage":
        return "Build a clean local sample, run one route in practice, and grow score slowly."
    if primary_goal == "live_prepare":
        return "Stay in practice mode, finish diagnostics, and clear the live gate deliberately."
    if primary_goal == "lab_experiment":
        return "Keep Lab practice-only until recorder health and practice score look stable."
    if "Polymarket" in enabled_venues:
        return "Equip Polymarket, record a local sample, then inspect one scanner route."
    return "Create a profile and equip your first connector."


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
        if not normalized.equipped_connectors:
            normalized.equipped_connectors = _default_connectors(
                normalized.enabled_venues,
                normalized.ai_coach_enabled,
            )
        if not normalized.equipped_modules:
            normalized.equipped_modules = _default_modules(
                normalized.enabled_venues,
                normalized.lab_enabled,
            )
        if not normalized.primary_mission:
            normalized.primary_mission = _primary_mission(
                normalized.primary_goal,
                normalized.enabled_venues,
            )
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
        experience_level: str = "beginner",
        guided_mode: bool = True,
        lab_enabled: bool = False,
        live_unlocked: bool = False,
        ai_coach_enabled: bool = False,
        default_strategy_tier: str = "core",
        risk_policy_id: str = "starter",
        primary_goal: str = "learn_and_scan",
        live_rules_accepted: bool = False,
        risk_limits_acknowledged: bool = False,
        brand_name: str = "Superior",
        equipped_connectors: list[ConnectorId] | None = None,
        equipped_modules: list[ModuleId] | None = None,
        scoreboard_mode: str = "paper",
        first_run_completed: bool = False,
        primary_mission: str | None = None,
        copilot_provider_id: str = "none",
        copilot_model_name: str = "",
        copilot_base_url: str = "",
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
            experience_level=experience_level,
            guided_mode=guided_mode,
            lab_enabled=lab_enabled,
            live_unlocked=live_unlocked,
            ai_coach_enabled=ai_coach_enabled,
            default_strategy_tier=default_strategy_tier,
            risk_policy_id=risk_policy_id,
            primary_goal=primary_goal,
            live_rules_accepted=live_rules_accepted,
            risk_limits_acknowledged=risk_limits_acknowledged,
            brand_name=brand_name,
            equipped_connectors=equipped_connectors or _default_connectors(enabled_venues, ai_coach_enabled),
            equipped_modules=equipped_modules or _default_modules(enabled_venues, lab_enabled),
            scoreboard_mode=scoreboard_mode,
            first_run_completed=first_run_completed,
            primary_mission=primary_mission or _primary_mission(primary_goal, enabled_venues),
            copilot_provider_id=copilot_provider_id,
            copilot_model_name=copilot_model_name,
            copilot_base_url=copilot_base_url,
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
        duplicate.live_unlocked = False
        duplicate.first_run_completed = False
        duplicate.experimental_live_enabled = False
        duplicate.live_mode = "locked"
        duplicate.paper_gate_passed = False
        duplicate.paper_gate_passed_at = None
        duplicate.data_dir = self._paths.data_dir / duplicate.id
        duplicate.primary_mission = _primary_mission(duplicate.primary_goal, duplicate.enabled_venues)
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
        imported.live_unlocked = False
        imported.experimental_live_enabled = False
        imported.live_mode = "locked"
        imported.paper_gate_passed = False
        imported.paper_gate_passed_at = None
        if not imported.data_dir.is_absolute():
            imported.data_dir = self._paths.data_dir / imported.id
        if not imported.primary_mission:
            imported.primary_mission = _primary_mission(imported.primary_goal, imported.enabled_venues)
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
        if document.schema_version != 3:
            return ProfilesDocument(profiles=document.profiles)
        return document

    def _write(self, document: ProfilesDocument) -> None:
        self._paths.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.profiles_path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
