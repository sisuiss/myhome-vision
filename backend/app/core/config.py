"""アプリケーション設定（環境変数ベース）。"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数から読み込むアプリ設定。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # ---- DB / Queue ----
    database_url: str = "sqlite+aiosqlite:///./myhome_vision.db"
    redis_url: str = "redis://localhost:6379/0"

    # ---- Feature flags ----
    kling_enabled: bool = False

    # ---- Provider endpoints ----
    comfyui_endpoint: str = "http://localhost:8188"
    comfyui_api_key: str = ""
    viggle_endpoint: str = "https://api.viggle.ai/v1"
    viggle_api_key: str = ""
    runway_endpoint: str = "https://api.runwayml.com/v1"
    runway_api_key: str = ""
    kling_endpoint: str = "https://api.klingai.com/v1"
    kling_api_key: str = ""

    # ---- Over-generation ----
    overgen_multiplier: float = 2.0
    displayed_patterns: int = 4

    # ---- Quality gate ----
    quality_arcface_min: float = 0.65
    quality_pose_min: float = 0.70
    quality_uncanny_max: float = 0.30

    # ---- Circuit breaker ----
    cb_error_rate_threshold: float = 0.20
    cb_window_seconds: int = 300
    cb_cooldown_seconds: int = 600

    # ---- Anonymization ----
    anon_salt: str = Field(default="dev-only-change-me")
    failed_log_retention_days: int = 730


@lru_cache
def get_settings() -> Settings:
    return Settings()
