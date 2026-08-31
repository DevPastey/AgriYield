"""
The core recommendation endpoint.

The route itself is fully wired: it validates input, fetches live weather,
and assembles the response. The actual agronomy decisions come from
app/services/irrigation_engine.py and app/services/fertilizer_engine.py —
implement those and this endpoint will work end-to-end.
"""

from datetime import date as date_cls

from fastapi import APIRouter, HTTPException

from app.schemas.recommendation import (
    DailyPlan,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services import fertilizer_engine, irrigation_engine
from app.services.weather_service import WeatherServiceError, get_seven_day_outlook

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def create_recommendation(payload: RecommendationRequest):
    try:
        daily_weather = await get_seven_day_outlook(payload.latitude, payload.longitude)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not daily_weather:
        raise HTTPException(status_code=502, detail="No weather data returned for this location.")

    # --- Irrigation plan (TODO: implemented by you in irrigation_engine.py) ---
    try:
        irrigation_plan = irrigation_engine.generate_irrigation_plan(
            daily_weather=daily_weather,
            soil_texture=payload.soil_texture,
            growth_stage=payload.growth_stage,
            crop_type=payload.crop_type,
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail=f"Irrigation engine not implemented yet: {exc}",
        ) from exc

    # --- Fertilizer plan (TODO: implemented by you in fertilizer_engine.py) ---
    daily_plans: list[DailyPlan] = []
    for day_index, (weather, irrigation) in enumerate(zip(daily_weather, irrigation_plan)):
        fertilizer = None
        try:
            if fertilizer_engine.should_apply_fertilizer_today(
                growth_stage=payload.growth_stage,
                days_since_last_application=None,  # TODO: track this properly, e.g. via request or DB
                day_index_in_plan=day_index,
            ):
                fertilizer = fertilizer_engine.calculate_npk_blend(
                    crop_type=payload.crop_type,
                    growth_stage=payload.growth_stage,
                    soil_texture=payload.soil_texture,
                    recent_rainfall_mm=weather.rainfall_mm,
                )
        except NotImplementedError:
            # Fertilizer engine not implemented yet — irrigation-only response is still useful.
            pass

        daily_plans.append(
            DailyPlan(date=weather.date, weather=weather, irrigation=irrigation, fertilizer=fertilizer)
        )

    return RecommendationResponse(
        request=payload,
        generated_at=date_cls.today(),
        seven_day_plan=daily_plans,
        # TODO: replace with a real human-readable summary once the engines
        # are implemented, e.g. "Irrigate on 2 of 7 days; apply fertilizer once."
        summary="TODO: generate a plain-language summary of the week's plan.",
    )
