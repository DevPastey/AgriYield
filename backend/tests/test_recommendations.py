"""
Test scaffold for the agronomy logic layer.

Writing tests for irrigation_engine and fertilizer_engine as you implement
them is a strong scholarship signal — it shows engineering discipline, not
just a working demo. Fill in the TODOs alongside your implementation.
"""

import pytest

from app.schemas.recommendation import DailyWeather, GrowthStage, SoilTexture
from app.services.evapotranspiration import calculate_crop_water_requirement, calculate_reference_et
from app.services.fertilizer_engine import calculate_npk_blend
from app.services.irrigation_engine import generate_irrigation_plan


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
    # TODO: construct a scenario where soil moisture deficit clearly exceeds
    # the management-allowed depletion threshold, and assert
    # decide_irrigation(...) returns should_irrigate=True.
    pytest.skip("TODO: implement once irrigation_engine.decide_irrigation is done")


def test_no_irrigation_when_rain_is_imminent(sample_weather):
    # TODO: assert the engine correctly withholds/reduces irrigation when
    # meaningful rain is forecast in the next day or two.
    pytest.skip("TODO: implement once irrigation_engine is done")


def test_npk_blend_adjusts_for_sandy_soil():
    # TODO: assert calculate_npk_blend increases nitrogen (or whatever your
    # agronomy logic dictates) for SoilTexture.SAND vs SoilTexture.CLAY.
    pytest.skip("TODO: implement once fertilizer_engine.calculate_npk_blend is done")
