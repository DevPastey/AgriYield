"""
Test scaffold for the agronomy logic layer.

Writing tests for irrigation_engine and fertilizer_engine as you implement
them is a strong scholarship signal — it shows engineering discipline, not
just a working demo. Fill in the TODOs alongside your implementation.
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

import pytest

from app.schemas.recommendation import DailyWeather, GrowthStage, SoilTexture
from app.services.evapotranspiration import (
    calculate_crop_water_requirement,
    calculate_reference_et,
)
from app.services.fertilizer_engine import calculate_npk_blend
from app.services.irrigation_engine import generate_irrigation_plan

pytestmark = pytest.mark.usefixtures("stub_crop_profiles")


@pytest.fixture
def sample_weather() -> DailyWeather:
    return DailyWeather(
        date="2026-06-01",
        temp_min_c=22.0,
        temp_max_c=33.0,
        humidity_pct=55.0,
        rainfall_mm=0.0,
        wind_speed_ms=2.1,
        condition="Clear",
    )


def test_reference_et_is_positive(sample_weather):
    et0 = calculate_reference_et(sample_weather, latitude=7.4, day_of_year=180)
    assert 1.0 < et0 < 12.0


def test_agronomy_engine_returns_reasonable_daily_outputs(sample_weather):
    et0 = calculate_reference_et(sample_weather, latitude=7.4, day_of_year=180)
    assert et0 > 0

    etc = calculate_crop_water_requirement(
        sample_weather,
        crop_type="maize",
        growth_stage=GrowthStage.DEVELOPMENT,
        latitude=7.4,
        day_of_year=sample_weather.date.timetuple().tm_yday,
        simplify_for_forecast=True,
    )
    assert etc > 0

    plan = generate_irrigation_plan(
        daily_weather=[sample_weather],
        latitude=7.4,
        soil_texture=SoilTexture.LOAM,
        growth_stage=GrowthStage.DEVELOPMENT,
        crop_type="maize",
    )
    assert len(plan) == 1
    assert isinstance(plan[0].should_irrigate, bool)
    assert plan[0].crop_water_requirement_mm == etc

    blend = calculate_npk_blend(
        crop_type="maize",
        growth_stage=GrowthStage.DEVELOPMENT,
        soil_texture=SoilTexture.SAND,
        recent_rainfall_mm=12.0,
    )
    assert blend.nitrogen_kg_per_ha > 0


def test_irrigation_triggered_on_dry_high_deficit_day(sample_weather):
    dry_days = [
        DailyWeather(
            date=f"2026-06-{day:02d}",
            temp_min_c=30.0,
            temp_max_c=42.0,
            humidity_pct=25.0,
            rainfall_mm=0.0,
            wind_speed_ms=3.5,
            condition="Clear",
        )
        for day in range(1, 21)
    ]

    plan = generate_irrigation_plan(
        daily_weather=dry_days,
        latitude=7.4,
        soil_texture=SoilTexture.LOAM,
        growth_stage=GrowthStage.DEVELOPMENT,
        crop_type="maize",
    )

    assert any(day.should_irrigate for day in plan)
    assert any(day.irrigation_amount_mm is not None and day.irrigation_amount_mm > 0 for day in plan)
    assert any("refill the root zone" in day.reasoning.lower() for day in plan)


def test_no_irrigation_when_rain_is_imminent(sample_weather):
    dry_days = [
        DailyWeather(
            date=f"2026-06-{day:02d}",
            temp_min_c=30.0,
            temp_max_c=42.0,
            humidity_pct=25.0,
            rainfall_mm=0.0,
            wind_speed_ms=3.5,
            condition="Clear",
        )
        for day in range(1, 20)
    ]
    rainy_day = DailyWeather(
        date="2026-06-20",
        temp_min_c=28.0,
        temp_max_c=36.0,
        humidity_pct=65.0,
        rainfall_mm=12.0,
        wind_speed_ms=2.0,
        condition="Rain",
    )
    final_day = DailyWeather(
        date="2026-06-21",
        temp_min_c=29.0,
        temp_max_c=38.0,
        humidity_pct=35.0,
        rainfall_mm=0.0,
        wind_speed_ms=2.0,
        condition="Clear",
    )

    plan = generate_irrigation_plan(
        daily_weather=dry_days + [rainy_day, final_day],
        latitude=7.4,
        soil_texture=SoilTexture.LOAM,
        growth_stage=GrowthStage.DEVELOPMENT,
        crop_type="maize",
    )

    deferred = next(
        day for day in plan if not day.should_irrigate and "forecast" in day.reasoning.lower()
    )
    assert deferred.date.isoformat() == "2026-06-19"
    assert deferred.irrigation_amount_mm == 0.0


def test_npk_blend_adjusts_for_sandy_soil():
    sand_blend = calculate_npk_blend(
        crop_type="maize",
        growth_stage=GrowthStage.DEVELOPMENT,
        soil_texture=SoilTexture.SAND,
        recent_rainfall_mm=12.0,
    )
    clay_blend = calculate_npk_blend(
        crop_type="maize",
        growth_stage=GrowthStage.DEVELOPMENT,
        soil_texture=SoilTexture.CLAY,
        recent_rainfall_mm=12.0,
    )

    assert sand_blend.nitrogen_kg_per_ha > clay_blend.nitrogen_kg_per_ha
    assert sand_blend.nitrogen_kg_per_ha > 0
    assert clay_blend.nitrogen_kg_per_ha > 0
