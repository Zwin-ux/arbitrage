from __future__ import annotations

import asyncio
import threading
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import structlog

from market_data_recorder.config import RecorderSettings
from market_data_recorder.replay import ReplayEngine
from market_data_recorder.service import RecorderService
from market_data_recorder.storage import DuckDBStorage
from market_data_recorder.verify import RecorderVerifier

from .app_types import AppProfile, DashboardSummary, EngineStatus, RunPreset, default_run_presets

RecordRunner = Callable[[RecorderSettings, RunPreset, Callable[[], bool]], None]
ReplayRunner = Callable[[Path], str]
VerifyRunner = Callable[[Path], str]


def _default_record_runner(
    settings: RecorderSettings,
    preset: RunPreset,
    stop_requested: Callable[[], bool],
) -> None:
    async def _run() -> None:
        service = RecorderService(settings)
        try:
            await service.record(
                runtime_seconds=preset.runtime_seconds,
                asset_ids=preset.asset_ids or None,
                max_pages=preset.max_pages,
                persist_discovery_metadata=preset.persist_discovery_metadata,
                stop_requested=stop_requested,
            )
        finally:
            await service.close()

    asyncio.run(_run())


def _default_replay_runner(db_path: Path) -> str:
    storage = DuckDBStorage(db_path)
    try:
        return ReplayEngine(storage).replay_summary().model_dump_json(indent=2)
    finally:
        storage.close()


def _default_verify_runner(db_path: Path) -> str:
    storage = DuckDBStorage(db_path)
    try:
        return RecorderVerifier(storage).verify().model_dump_json(indent=2)
    finally:
        storage.close()


class EngineController:
    def __init__(
        self,
        base_settings: RecorderSettings,
        *,
        presets: list[RunPreset] | None = None,
        record_runner: RecordRunner | None = None,
        replay_runner: ReplayRunner | None = None,
        verify_runner: VerifyRunner | None = None,
    ) -> None:
        self._base_settings = base_settings
        self._presets = presets or default_run_presets()
        self._record_runner = record_runner or _default_record_runner
        self._replay_runner = replay_runner or _default_replay_runner
        self._verify_runner = verify_runner or _default_verify_runner
        self._status = EngineStatus()
        self._thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._lock = threading.Lock()
        self._logger = structlog.get_logger(self.__class__.__name__)

    def presets(self) -> list[RunPreset]:
        return list(self._presets)

    def preset(self, preset_id: str) -> RunPreset:
        for preset in self._presets:
            if preset.id == preset_id:
                return preset
        raise KeyError(f"Unknown preset: {preset_id}")

    def run_preset(self, profile: AppProfile, preset_id: str) -> None:
        preset = self.preset(preset_id)
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("A recorder task is already running.")
            self._stop_flag.clear()
            self._status = EngineStatus(
                state="running",
                active_profile_id=profile.id,
                active_preset_id=preset.id,
                started_at=datetime.now(timezone.utc),
                last_message=f"Running {preset.label} for {profile.display_name}.",
                summary=self._build_summary(profile),
            )
            self._thread = threading.Thread(
                target=self._run_in_thread,
                name=f"pmr-{preset.id}",
                args=(profile, preset),
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_flag.set()

    def shutdown(self) -> None:
        self.stop()
        with self._lock:
            thread = self._thread
        if thread is not None:
            thread.join(timeout=5.0)

    def status(self, profile: AppProfile | None = None) -> EngineStatus:
        with self._lock:
            snapshot = self._status.model_copy(deep=True)
        if profile is not None:
            snapshot.summary = self._build_summary(profile)
        return snapshot

    def _run_in_thread(self, profile: AppProfile, preset: RunPreset) -> None:
        try:
            db_path = self._db_path(profile)
            if preset.mode == "record":
                self._record_runner(
                    self._settings_for_profile(profile),
                    preset,
                    self._stop_flag.is_set,
                )
                result_message = f"{preset.label} finished."
            elif preset.mode == "replay":
                result_message = self._replay_runner(db_path)
            elif preset.mode == "verify":
                result_message = self._verify_runner(db_path)
            else:
                raise RuntimeError(f"Unsupported preset mode: {preset.mode}")
            self._set_terminal_status(
                state="completed",
                profile=profile,
                preset=preset,
                message=result_message,
            )
        except Exception as exc:
            self._logger.exception("engine_run_failed", preset_id=preset.id, profile_id=profile.id)
            self._set_terminal_status(
                state="failed",
                profile=profile,
                preset=preset,
                message="Run failed.",
                error=str(exc),
            )
        finally:
            self._stop_flag.clear()
            with self._lock:
                self._thread = None

    def _set_terminal_status(
        self,
        *,
        state: str,
        profile: AppProfile,
        preset: RunPreset,
        message: str,
        error: str | None = None,
    ) -> None:
        with self._lock:
            self._status = EngineStatus(
                state=state,
                active_profile_id=profile.id,
                active_preset_id=preset.id,
                started_at=self._status.started_at,
                finished_at=datetime.now(timezone.utc),
                last_message=message,
                last_error=error,
                summary=self._build_summary(profile),
            )

    def _settings_for_profile(self, profile: AppProfile) -> RecorderSettings:
        db_path = self._db_path(profile)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return self._base_settings.model_copy(update={"duckdb_path": db_path})

    @staticmethod
    def _db_path(profile: AppProfile) -> Path:
        return profile.data_dir / "market_data.duckdb"

    def _build_summary(self, profile: AppProfile) -> DashboardSummary:
        db_path = self._db_path(profile)
        if not db_path.exists():
            return DashboardSummary(db_path=db_path)
        try:
            storage = DuckDBStorage(db_path)
        except Exception:
            return DashboardSummary(db_path=db_path)
        try:
            raw_messages, book_snapshots, health_events, last_recorded_at, latest_issue = (
                storage.fetch_dashboard_summary()
            )
            latest_warning: str | None = None
            if latest_issue is not None:
                latest_warning = f"{latest_issue[0]}: {latest_issue[1]}"
            return DashboardSummary(
                db_path=db_path,
                raw_messages=raw_messages,
                book_snapshots=book_snapshots,
                health_events=health_events,
                last_recorded_at=last_recorded_at,
                latest_warning=latest_warning,
            )
        finally:
            with suppress(Exception):
                storage.close()
