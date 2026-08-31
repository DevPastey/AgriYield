"""
Weather endpoints. Fully implemented — thin wrapper around weather_service.
"""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.recommendation import DailyWeather
from app.services.weather_service import WeatherServiceError, get_seven_day_outlook

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/outlook", response_model=list[DailyWeather])
async def weather_outlook(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    """Return the multi-day weather outlook for a location. Used standalone
    by the frontend's weather strip, and internally by the recommendation
    engine."""
    try:
        return await get_seven_day_outlook(lat, lon)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
