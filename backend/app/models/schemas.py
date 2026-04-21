"""API リクエスト／レスポンス スキーマ（Pydantic）。"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# -------- Subjects (Extensibility 5原則の subjects[]) --------

class SubjectRole(str, Enum):
    ADULT = "adult"
    CHILD = "child"
    PET = "pet"  # V3 以降


class Subject(BaseModel):
    role: SubjectRole
    gender: Literal["male", "female", "other"] | None = None
    age_band: str | None = Field(default=None, description="e.g., 30s, 40s, preschool")
    avatar_flag: bool = False


# -------- Consent --------

class ConsentLevel(int, Enum):
    L1_DOMESTIC = 1
    L2_US = 2
    L3_ALL = 3


class RetentionMode(str, Enum):
    STANDARD = "standard"  # 30日で自動削除
    EXTENDED = "extended"  # 永続（年次確認）


# -------- Job submission --------

class Scene(str, Enum):
    MORNING_COFFEE = "morning_coffee"
    BALCONY = "balcony"
    LIVING_DAY = "living_day"
    WEEKEND_BEDROOM = "weekend_bedroom"


class JobCreateRequest(BaseModel):
    session_id: str | None = None
    property_id: str | None = None
    scene: Scene
    consent_level: ConsentLevel = ConsentLevel.L1_DOMESTIC
    retention_mode: RetentionMode = RetentionMode.STANDARD
    subjects: list[Subject] = Field(min_length=1, max_length=6)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    QUALITY_REJECTED = "quality_rejected"


class GenerationAttempt(BaseModel):
    attempt_id: str
    provider: str
    status: JobStatus
    overgen_index: int
    quality_score: float | None = None
    arcface_score: float | None = None
    pose_score: float | None = None
    duration_ms: int | None = None
    failure_reason: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class JobResponse(BaseModel):
    job_id: str
    session_id: str | None
    scene: Scene
    consent_level: ConsentLevel
    retention_mode: RetentionMode
    status: JobStatus
    attempts: list[GenerationAttempt] = Field(default_factory=list)
    displayed_video_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
