"""
Test scaffold for the agronomy logic layer.

Writing tests for irrigation_engine and fertilizer_engine as you implement
them is a strong scholarship signal — it shows engineering discipline, not
just a working demo. Fill in the TODOs alongside your implementation.
"""

import pytest

from app.schemas.recommendation import DailyWeather, GrowthStage, SoilTexture


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
    # TODO: once evapotranspiration.calculate_reference_et is implemented,
    # assert it returns a sane ET0 value (typically 2-8 mm/day for most climates).
    pytest.skip("TODO: implement once calculate_reference_et is done")


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
