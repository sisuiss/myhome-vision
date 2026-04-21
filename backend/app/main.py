"""FastAPI エントリポイント。"""
from __future__ import annotations

from fastapi import FastAPI

from .api.routes import router
from .core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="MyHome Vision API (Phase 0 PoC)",
        version="0.0.1",
        description="モーション代役×全身AI生成による住空間未来体験サービスのPhase 0用 API。",
    )
    app.include_router(router)
    return app


app = create_app()
