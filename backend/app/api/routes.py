"""HTTP エンドポイント定義。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.circuit_breaker import registry as cb_registry
from ..core.config import get_settings
from ..models.schemas import JobCreateRequest, JobResponse
from ..providers import get_registry
from ..services.job_manager import get_manager

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "providers": get_registry().status(),
        "overgen": {
            "multiplier": settings.overgen_multiplier,
            "displayed": settings.displayed_patterns,
        },
    }


@router.get("/providers/status")
async def providers_status() -> dict:
    return {
        "providers": get_registry().status(),
        "circuit_breakers": cb_registry.snapshot_all(),
    }


@router.post("/jobs", response_model=JobResponse)
async def create_job(req: JobCreateRequest) -> JobResponse:
    try:
        return await get_manager().submit(req)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    job = get_manager().get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job
