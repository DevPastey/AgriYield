"""
AgriYield-API — FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload

Run via Docker:
    docker compose up backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import recommendations, weather
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Precision irrigation & fertilizer recommendation engine.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
app.include_router(weather.router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
