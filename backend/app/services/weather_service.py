"""
Weather integration service.

Wraps OpenWeatherMap's free-tier "5 day / 3 hour forecast" endpoint and
collapses it into one DailyWeather entry per day. This is plumbing, not
agronomy — it's fully implemented so you can focus your effort on the
irrigation/fertilizer logic in irrigation_engine.py and fertilizer_engine.py.

If you have a One Call 3.0 subscription (has a free tier with a card on
file), set OPENWEATHER_USE_ONECALL=true in .env and extend `_fetch_onecall`
below for real daily aggregates + rain probability.
"""

from collections import defaultdict
from datetime import date, datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.schemas.recommendation import DailyWeather

settings = get_settings()

# Very small in-memory cache: {(lat, lon): (fetched_at_epoch, [DailyWeather, ...])}
# Fine for a portfolio project / single-instance deploy. Swap for Redis if you
# ever run multiple backend instances.
_cache: dict[tuple[float, float], tuple[float, list[DailyWeather]]] = {}


class WeatherServiceError(RuntimeError):
    """Raised when the upstream weather API can't be reached or returns bad data."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=1, max=8))
async def _fetch_5day_forecast(lat: float, lon: float) -> dict:
    if not settings.openweather_api_key or settings.openweather_api_key == "your_openweathermap_key_here":
        raise WeatherServiceError(
            "OPENWEATHER_API_KEY is not set. Get a free key at "
            "https://home.openweathermap.org/api_keys and put it in backend/.env"
        )

    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_api_key,
        "units": "metric",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{settings.openweather_base_url}/forecast", params=params)
        response.raise_for_status()
        return response.json()


def _collapse_to_daily(raw: dict) -> list[DailyWeather]:
    """
    OpenWeatherMap's free /forecast endpoint returns 3-hour steps for 5 days.
    We group by calendar date and take min/max/mean across the day's steps.
    """
    buckets: dict[date, list[dict]] = defaultdict(list)

    for entry in raw.get("list", []):
        dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
        buckets[dt.date()].append(entry)

    daily: list[DailyWeather] = []
    for day, entries in sorted(buckets.items()):
        temps = [e["main"]["temp"] for e in entries]
        humidity = [e["main"]["humidity"] for e in entries]
        wind = [e["wind"]["speed"] for e in entries]
        rainfall = sum(e.get("rain", {}).get("3h", 0.0) for e in entries)
        conditions = [e["weather"][0]["main"] for e in entries if e.get("weather")]
        # crude "most common condition of the day" — good enough for a dashboard label
        dominant_condition = max(set(conditions), key=conditions.count) if conditions else "Unknown"

        daily.append(
            DailyWeather(
                date=day,
                temp_min_c=round(min(temps), 1),
                temp_max_c=round(max(temps), 1),
                humidity_pct=round(sum(humidity) / len(humidity), 1),
                rainfall_mm=round(rainfall, 2),
                wind_speed_ms=round(sum(wind) / len(wind), 2),
                condition=dominant_condition,
            )
        )

    return daily


async def get_seven_day_outlook(lat: float, lon: float) -> list[DailyWeather]:
    """
    Public entry point used by the recommendation routes/services.

    NOTE: the free /forecast endpoint only covers ~5 days. We return what's
    available (typically 5-6 daily buckets, since the first/last day are
    partial). If you upgrade to One Call 3.0 you'll get a true 7-8 day range —
    swap the implementation of _fetch_5day_forecast accordingly.
    """
    cache_key = (round(lat, 3), round(lon, 3))
    now = datetime.now(timezone.utc).timestamp()

    if cache_key in _cache:
        fetched_at, cached_days = _cache[cache_key]
        if now - fetched_at < settings.weather_cache_ttl_seconds:
            return cached_days

    raw = await _fetch_5day_forecast(lat, lon)
    daily = _collapse_to_daily(raw)
    _cache[cache_key] = (now, daily)
    return daily
