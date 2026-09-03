"""
Weather endpoints. Fully implemented — thin wrapper around weather_service.
"""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.recommendation import DailyWeather, LocationLookup
from app.services.weather_service import (
    WeatherServiceError,
    get_seven_day_outlook,
    reverse_geocode,
)

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


@router.get("/location", response_model=LocationLookup)
async def location_from_coordinates(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    try:
        name = await reverse_geocode(lat, lon)
        return LocationLookup(name=name, latitude=lat, longitude=lon)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
