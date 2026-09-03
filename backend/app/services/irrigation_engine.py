"""Irrigation planner backed by crop profiles stored in PostgreSQL."""

from app.schemas.recommendation import (
    DailyWeather,
    GrowthStage,
    IrrigationRecommendation,
    SoilTexture,
)
from app.services.agrony_repository import get_crop_stage_profile
from app.services.evapotranspiration import calculate_crop_water_requirement

SOIL_WATER_HOLDING_CAPACITY_MM_PER_M: dict[SoilTexture, float] = {
    SoilTexture.SAND: 90.0, SoilTexture.LOAMY_SAND: 125.0, SoilTexture.SANDY_LOAM: 170.0,
    SoilTexture.LOAM: 210.0, SoilTexture.SILT_LOAM: 245.0, SoilTexture.SILTY_CLAY_LOAM: 220.0,
    SoilTexture.CLAY_LOAM: 205.0, SoilTexture.CLAY: 180.0,
}


def generate_irrigation_plan(
    daily_weather: list[DailyWeather], latitude: float, soil_texture: SoilTexture,
    growth_stage: GrowthStage, crop_type: str,
) -> list[IrrigationRecommendation]:
    profile = get_crop_stage_profile(crop_type, growth_stage)
    root_zone_taw = SOIL_WATER_HOLDING_CAPACITY_MM_PER_M[soil_texture] * profile.root_depth_m
    threshold = root_zone_taw * profile.depletion_fraction
    deficit = 0.0
    plan: list[IrrigationRecommendation] = []

    for index, weather in enumerate(daily_weather):
        etc = calculate_crop_water_requirement(
            weather, crop_type, growth_stage, latitude, weather.date.timetuple().tm_yday,
        )
        effective_rainfall = weather.rainfall_mm * 0.8
        deficit = min(root_zone_taw, max(0.0, deficit + etc - effective_rainfall))
        next_day_rain = daily_weather[index + 1].rainfall_mm if index + 1 < len(daily_weather) else 0.0
        should_irrigate = deficit >= threshold and next_day_rain < 8.0
        amount = round(deficit, 1) if should_irrigate else 0.0
        if should_irrigate:
            reasoning = f"Soil deficit is {deficit:.1f} mm, above the DB-configured threshold of {threshold:.1f} mm; refill the root zone."
            deficit = 0.0
        elif deficit >= threshold:
            reasoning = f"Soil deficit is {deficit:.1f} mm, but {next_day_rain:.1f} mm rain is forecast; defer irrigation."
        else:
            reasoning = f"Soil deficit is {deficit:.1f} mm, below the DB-configured threshold of {threshold:.1f} mm; no irrigation needed."
        plan.append(IrrigationRecommendation(
            date=weather.date, should_irrigate=should_irrigate, irrigation_amount_mm=amount,
            crop_water_requirement_mm=etc, reasoning=reasoning,
        ))
    return plan
