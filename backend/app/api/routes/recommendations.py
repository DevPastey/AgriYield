"""
The core recommendation endpoint.

The route itself is fully wired: it validates input, fetches live weather,
and assembles the response. The actual agronomy decisions come from
app/services/irrigation_engine.py and app/services/fertilizer_engine.py —
implement those and this endpoint will work end-to-end.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app.schemas.recommendation import (
    CropOption,
    DailyPlan,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services import fertilizer_engine, irrigation_engine
from app.services.crop_catalog import get_supported_crops
from app.services.weather_service import WeatherServiceError, get_seven_day_outlook

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/crops", response_model=list[CropOption])
async def list_supported_crops():
    return [CropOption(value=crop, label=crop.replace("_", " ").title()) for crop in get_supported_crops()]


@router.post("", response_model=RecommendationResponse)
async def create_recommendation(payload: RecommendationRequest):
    if payload.crop_type.strip().lower() not in get_supported_crops():
        raise HTTPException(status_code=422, detail="The selected crop is not supported for recommendations.")
    try:
        daily_weather = await get_seven_day_outlook(payload.latitude, payload.longitude)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not daily_weather:
        raise HTTPException(status_code=502, detail="No weather data returned for this location.")

    try:
        irrigation_plan = irrigation_engine.generate_irrigation_plan(
            daily_weather=daily_weather,
            latitude=payload.latitude,
            soil_texture=payload.soil_texture,
            growth_stage=payload.growth_stage,
            crop_type=payload.crop_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    daily_plans: list[DailyPlan] = []
    for day_index, (weather, irrigation) in enumerate(zip(daily_weather, irrigation_plan)):
        fertilizer = None
        try:
            if fertilizer_engine.should_apply_fertilizer_today(
                growth_stage=payload.growth_stage,
                days_since_last_application=None,
                day_index_in_plan=day_index,
            ):
                fertilizer = fertilizer_engine.calculate_npk_blend(
                    crop_type=payload.crop_type,
                    growth_stage=payload.growth_stage,
                    soil_texture=payload.soil_texture,
                    recent_rainfall_mm=weather.rainfall_mm,
                )
        except ValueError as exc:
            # Fertilizer engine not implemented yet — irrigation-only response is still useful.
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        daily_plans.append(
            DailyPlan(date=weather.date, weather=weather, irrigation=irrigation, fertilizer=fertilizer)
        )

    irrigated_days = sum(1 for item in daily_plans if item.irrigation.should_irrigate)
    fertilizer_days = sum(1 for item in daily_plans if item.fertilizer is not None)
    summary = (
        f"This plan recommends irrigation on {irrigated_days} day(s) and fertilizer on {fertilizer_days} day(s). "
        f"Use the crop calendar and day-by-day reasoning to adjust scheduling based on soil moisture and rainfall."
    )

    return RecommendationResponse(
        request=payload,
        generated_at=datetime.now(UTC).date(),
        seven_day_plan=daily_plans,
        summary=summary,
    )
