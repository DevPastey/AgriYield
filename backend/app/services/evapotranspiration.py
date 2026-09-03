"""FAO-56 reference ET and DB-backed crop coefficients."""

import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    backend_root = Path(__file__).resolve().parents[2]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from app.schemas.recommendation import DailyWeather, GrowthStage
from app.services.agrony_repository import get_crop_stage_profile


def calculate_reference_et(weather: DailyWeather, latitude: float, day_of_year: int) -> float:
    """Calculate Hargreaves reference ET0 in mm/day from forecast weather."""
    latitude_radians = math.radians(latitude)
    earth_sun_distance = 1 + 0.033 * math.cos(2 * math.pi * day_of_year / 365)
    solar_declination = 0.409 * math.sin((2 * math.pi * day_of_year / 365) - 1.39)
    sunset_cosine = -math.tan(latitude_radians) * math.tan(solar_declination)
    sunset_angle = 0.0 if sunset_cosine >= 1 else math.pi if sunset_cosine <= -1 else math.acos(sunset_cosine)
    extraterrestrial_radiation = (
        (24 * 60 / math.pi)
        * 0.0820
        * earth_sun_distance
        * (
            sunset_angle * math.sin(latitude_radians) * math.sin(solar_declination)
            + math.cos(latitude_radians) * math.cos(solar_declination) * math.sin(sunset_angle)
        )
    )
    mean_temperature = (weather.temp_min_c + weather.temp_max_c) / 2
    temperature_range = max(weather.temp_max_c - weather.temp_min_c, 0)
    return round(max(0.0, 0.0023 * (mean_temperature + 17.8) * math.sqrt(temperature_range) * extraterrestrial_radiation * 0.408), 2)


def get_crop_coefficient(crop_type: str, growth_stage: GrowthStage, **_: object) -> float:
    """Read the stage Kc directly from the seeded `crop_coefficients` table."""
    return get_crop_stage_profile(crop_type, growth_stage).kc_value


def calculate_crop_water_requirement(
    weather: DailyWeather,
    crop_type: str,
    growth_stage: GrowthStage,
    latitude: float,
    day_of_year: int,
    **_: object,
) -> float:
    return round(
        calculate_reference_et(weather, latitude, day_of_year)
        * get_crop_coefficient(crop_type, growth_stage),
        2,
    )
