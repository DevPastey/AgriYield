"""Fertilizer recommendations using NPK baselines stored in PostgreSQL."""

from app.schemas.recommendation import GrowthStage, NPKBlend, SoilTexture
from app.services.agrony_repository import get_crop_stage_profile

SOIL_ADJUSTMENT_FACTORS: dict[SoilTexture, dict[str, float]] = {
    SoilTexture.SAND: {"nitrogen": 1.15, "phosphorus": 1.0, "potassium": 1.10},
    SoilTexture.LOAMY_SAND: {"nitrogen": 1.10, "phosphorus": 1.0, "potassium": 1.05},
    SoilTexture.SANDY_LOAM: {"nitrogen": 1.05, "phosphorus": 1.0, "potassium": 1.0},
    SoilTexture.LOAM: {"nitrogen": 1.0, "phosphorus": 1.0, "potassium": 1.0},
    SoilTexture.SILT_LOAM: {"nitrogen": 1.0, "phosphorus": 1.0, "potassium": 1.0},
    SoilTexture.SILTY_CLAY_LOAM: {"nitrogen": 0.95, "phosphorus": 1.0, "potassium": 1.0},
    SoilTexture.CLAY_LOAM: {"nitrogen": 0.95, "phosphorus": 1.10, "potassium": 0.95},
    SoilTexture.CLAY: {"nitrogen": 0.90, "phosphorus": 1.15, "potassium": 0.95},
}


def calculate_npk_blend(crop_type: str, growth_stage: GrowthStage, soil_texture: SoilTexture, recent_rainfall_mm: float) -> NPKBlend:
    profile = get_crop_stage_profile(crop_type, growth_stage)
    factors = SOIL_ADJUSTMENT_FACTORS[soil_texture]
    nitrogen = profile.base_n * factors["nitrogen"]
    phosphorus = profile.base_p * factors["phosphorus"]
    potassium = profile.base_k * factors["potassium"]
    if recent_rainfall_mm >= 25 and soil_texture in (SoilTexture.SAND, SoilTexture.LOAMY_SAND):
        nitrogen *= 1.15
    return NPKBlend(
        nitrogen_kg_per_ha=round(nitrogen, 1), phosphorus_kg_per_ha=round(phosphorus, 1),
        potassium_kg_per_ha=round(potassium, 1),
        reasoning=f"FAO-56 N-P-K baseline for {profile.name} was loaded from PostgreSQL and adjusted for {soil_texture.value} soil.",
    )


def should_apply_fertilizer_today(growth_stage: GrowthStage, days_since_last_application: int | None, day_index_in_plan: int) -> bool:
    return day_index_in_plan == 0 and (days_since_last_application is None or days_since_last_application >= 14)
