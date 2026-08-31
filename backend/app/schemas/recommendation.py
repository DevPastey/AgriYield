"""
Data contracts for the recommendation endpoints.

These are intentionally fully specified (not TODOs) — they're the shape
of your API, and getting the shape right up front makes the logic layer
(services/) easier to implement correctly and test.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class SoilTexture(str, Enum):
    """USDA soil texture classes. Extend/trim to match the crops you support."""

    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"
    CLAY_LOAM = "clay_loam"
    CLAY = "clay"


class GrowthStage(str, Enum):
    """Generic FAO-56 style crop growth stages. Add crop-specific stages as needed."""

    INITIAL = "initial"
    DEVELOPMENT = "development"
    MID_SEASON = "mid_season"
    LATE_SEASON = "late_season"


class RecommendationRequest(BaseModel):
    crop_type: str = Field(..., examples=["maize", "cassava", "tomato"])
    soil_texture: SoilTexture
    growth_stage: GrowthStage
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: str | None = Field(default=None, examples=["Ibadan, Oyo State"])
    field_size_hectares: float | None = Field(default=None, gt=0)


class DailyWeather(BaseModel):
    date: date
    temp_min_c: float
    temp_max_c: float
    humidity_pct: float
    rainfall_mm: float
    wind_speed_ms: float
    condition: str


class IrrigationRecommendation(BaseModel):
    date: date
    should_irrigate: bool
    irrigation_amount_mm: float | None = None
    reasoning: str


class NPKBlend(BaseModel):
    nitrogen_kg_per_ha: float
    phosphorus_kg_per_ha: float
    potassium_kg_per_ha: float
    reasoning: str


class DailyPlan(BaseModel):
    date: date
    weather: DailyWeather
    irrigation: IrrigationRecommendation
    fertilizer: NPKBlend | None = None  # typically only populated on application days


class RecommendationResponse(BaseModel):
    request: RecommendationRequest
    generated_at: date
    seven_day_plan: list[DailyPlan]
    summary: str
