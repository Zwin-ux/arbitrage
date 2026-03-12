from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrySettings(BaseModel):
    initial_seconds: float = Field(default=1.0, ge=0.01)
    max_seconds: float = Field(default=30.0, ge=0.01)


class RecorderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PMR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gamma_api_url: str = "https://gamma-api.polymarket.com"
    clob_api_url: str = "https://clob.polymarket.com"
    market_ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    duckdb_path: Path = Path("data/market_data.duckdb")
    discovery_limit: int = Field(default=500, ge=1, le=500)
    discovery_max_pages: int | None = Field(default=None, ge=1)
    discovery_order: str = "volume_24hr"
    discovery_ascending: bool = False
    bootstrap_batch_size: int = Field(default=50, ge=1, le=200)
    stale_after_seconds: float = Field(default=30.0, ge=0.01)
    stale_check_interval_seconds: float = Field(default=10.0, ge=0.01)
    rediscovery_interval_seconds: float = Field(default=300.0, ge=10.0)
    reconnect_initial_seconds: float = Field(default=1.0, ge=0.1)
    reconnect_max_seconds: float = Field(default=30.0, ge=1.0)
    ws_ping_interval_seconds: float = Field(default=20.0, ge=1.0)
    ws_ping_timeout_seconds: float = Field(default=20.0, ge=1.0)
    auto_subscribe_new_markets: bool = True
    unsubscribe_resolved_markets: bool = True
    log_level: str = "INFO"

    @property
    def retry(self) -> RetrySettings:
        return RetrySettings(
            initial_seconds=self.reconnect_initial_seconds,
            max_seconds=self.reconnect_max_seconds,
        )
