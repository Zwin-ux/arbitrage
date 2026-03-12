from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


TemplateName = Literal["Recorder", "Research", "Custom"]
PresetMode = Literal["record", "replay", "verify"]
EngineState = Literal["idle", "running", "completed", "failed"]
CredentialState = Literal["missing", "saved", "validated", "invalid"]


class RunPreset(BaseModel):
    id: str
    label: str
    description: str
    mode: PresetMode
    runtime_seconds: float | None = None
    persist_discovery_metadata: bool = False
    max_pages: int | None = None
    asset_ids: list[str] = Field(default_factory=list)


class AppProfile(BaseModel):
    id: str
    display_name: str
    template: TemplateName = "Recorder"
    data_dir: Path
    enabled_venues: list[str] = Field(default_factory=lambda: ["Polymarket"])
    market_filters: list[str] = Field(default_factory=list)
    auto_start: bool = False
    start_minimized: bool = False
    default_preset: str = "continuous-record"
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CredentialField(BaseModel):
    key: str
    label: str
    help_text: str
    secret: bool = False
    multiline: bool = False
    required: bool = False
    placeholder: str | None = None


class CredentialValidationResult(BaseModel):
    ok: bool
    status: CredentialState
    message: str


class CredentialStatus(BaseModel):
    provider_id: str
    provider_label: str
    status: CredentialState
    message: str


class DashboardSummary(BaseModel):
    db_path: Path
    raw_messages: int = 0
    book_snapshots: int = 0
    health_events: int = 0
    last_recorded_at: datetime | None = None
    latest_warning: str | None = None


class EngineStatus(BaseModel):
    state: EngineState = "idle"
    active_profile_id: str | None = None
    active_preset_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_message: str = "Ready."
    last_error: str | None = None
    summary: DashboardSummary | None = None


def default_run_presets() -> list[RunPreset]:
    return [
        RunPreset(
            id="continuous-record",
            label="Continuous recorder",
            description="Record market data until you stop the app.",
            mode="record",
            persist_discovery_metadata=True,
        ),
        RunPreset(
            id="fast-smoke-run",
            label="Fast smoke run",
            description="Record a short sample to confirm the recorder works.",
            mode="record",
            runtime_seconds=30.0,
            max_pages=1,
        ),
        RunPreset(
            id="replay-latest",
            label="Replay latest DB",
            description="Summarize the current profile database.",
            mode="replay",
        ),
        RunPreset(
            id="verify-latest",
            label="Verify latest DB",
            description="Verify hashes and stream consistency for the current profile database.",
            mode="verify",
        ),
    ]
