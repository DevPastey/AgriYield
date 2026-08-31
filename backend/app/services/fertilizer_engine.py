"""
NPK fertilizer blend recommendation logic.

This is core agronomy logic — YOU implement it.
"""

from app.schemas.recommendation import GrowthStage, NPKBlend, SoilTexture


# TODO: Fill in baseline crop nutrient uptake/application recommendations.
# Extension-service publications (IITA, IFDC, FAO Fertilizer Use by Crop
# series, or your local ministry of agriculture) publish kg N-P-K/ha
# recommendations per crop and growth stage. Widely-cited general-purpose
# starting points (verify against a regional source before publishing this
# as real advice — these vary significantly by soil fertility baseline):
#
#     PSEUDOCODE / reference values, total season kg/ha, split across stages:
#     maize   total ~ N:120  P:30  K:60
#         initial:      N:20  P:30  K:0     (P applied at planting — basal dose)
#         development:  N:50  P:0   K:20    (first topdress, ~knee-high)
#         mid_season:   N:50  P:0   K:30    (second topdress, pre-tasseling)
#         late_season:  N:0   P:0   K:10
#
#     tomato  total ~ N:150  P:60  K:150 (heavier K demand — fruiting crop)
#         initial:      N:20  P:60  K:20
#         development:  N:50  P:0   K:40
#         mid_season:   N:60  P:0   K:60
#         late_season:  N:20  P:0   K:30
#
#     cassava total ~ N:80   P:40  K:80  (lower overall demand, tolerant of poor soils)
#         initial:      N:0   P:40  K:0
#         development:  N:40  P:0   K:40
#         mid_season:   N:40  P:0   K:40
#         late_season:  N:0   P:0   K:0
#
# Structure as:
CROP_NPK_BASELINE_KG_PER_HA: dict[str, dict[GrowthStage, tuple[float, float, float]]] = {
    # "maize": {
    #     GrowthStage.INITIAL: (20.0, 30.0, 0.0),      # (N, P, K)
    #     GrowthStage.DEVELOPMENT: (50.0, 0.0, 20.0),
    #     GrowthStage.MID_SEASON: (50.0, 0.0, 30.0),
    #     GrowthStage.LATE_SEASON: (0.0, 0.0, 10.0),
    # },
}

# TODO: Soil-texture-based adjustment factors.
#
#     PSEUDOCODE / agronomic rationale:
#     - Sandy soils (sand, loamy_sand): low cation exchange capacity, N and K
#       leach quickly with rain -> increase N by ~10-15%, consider recommending
#       split application over more, smaller doses rather than raising the total.
#     - Clay soils (clay, clay_loam): P fixation is higher (binds to clay
#       particles, less plant-available) -> increase P by ~10-20%.
#     - Loam / silt loam: baseline, factor ~1.0 across the board (used as the
#       reference soil the CROP_NPK_BASELINE table above assumes).
#
#     Example structure:
#     SoilTexture.SAND: {"nitrogen": 1.15, "phosphorus": 1.0, "potassium": 1.10},
#     SoilTexture.LOAM: {"nitrogen": 1.0, "phosphorus": 1.0, "potassium": 1.0},
#     SoilTexture.CLAY: {"nitrogen": 1.0, "phosphorus": 1.15, "potassium": 0.95},
SOIL_ADJUSTMENT_FACTORS: dict[SoilTexture, dict[str, float]] = {
    # SoilTexture.SAND: {"nitrogen": 1.15, "phosphorus": 1.0, "potassium": 1.1},
}


def calculate_npk_blend(
    crop_type: str,
    growth_stage: GrowthStage,
    soil_texture: SoilTexture,
    recent_rainfall_mm: float,
) -> NPKBlend:
    """
    TODO: Compute a recommended NPK blend (kg/ha) for this crop, stage, and soil.

        PSEUDOCODE:
        n_base, p_base, k_base = CROP_NPK_BASELINE_KG_PER_HA[crop_type][growth_stage]
        factors = SOIL_ADJUSTMENT_FACTORS.get(soil_texture, {"nitrogen": 1.0, "phosphorus": 1.0, "potassium": 1.0})

        n = n_base * factors["nitrogen"]
        p = p_base * factors["phosphorus"]
        k = k_base * factors["potassium"]

        # Leaching penalty: nitrate-N is highly mobile in soil water. A
        # simple heuristic — if heavy rain has recently fallen (or is
        # forecast), a portion of applied N is assumed lost and should be
        # topped up, especially on sandy soils.
        HEAVY_RAIN_THRESHOLD_MM = 25.0  # document/adjust this threshold
        if recent_rainfall_mm >= HEAVY_RAIN_THRESHOLD_MM:
            leaching_uplift = 1.10 if soil_texture in (SoilTexture.SAND, SoilTexture.LOAMY_SAND) else 1.05
            n *= leaching_uplift

        reasoning = build_reasoning_string(crop_type, growth_stage, soil_texture, factors, recent_rainfall_mm)
        # e.g. "Base N-P-K for maize at development stage, +15% N for sandy
        # soil leaching risk, +10% N for 32mm of rain in the last window."

        return NPKBlend(
            nitrogen_kg_per_ha=round(n, 1),
            phosphorus_kg_per_ha=round(p, 1),
            potassium_kg_per_ha=round(k, 1),
            reasoning=reasoning,
        )

    Write a human-readable `reasoning` string explaining every adjustment you
    made — this is the part that demonstrates real agronomy knowledge to a
    reviewer, not just a lookup table.

    Returns:
        NPKBlend with kg/ha for each nutrient and a reasoning string.
    """
    raise NotImplementedError("TODO: implement NPK blend calculation")


def should_apply_fertilizer_today(
    growth_stage: GrowthStage,
    days_since_last_application: int | None,
    day_index_in_plan: int,
) -> bool:
    """
    TODO: Decide whether today is an appropriate fertilizer application day.

    Split application is standard agronomic practice (reduces leaching loss
    vs. one large dose, matches nutrient release to crop demand curve).
    A simple, defensible schedule for a 7-day *forecast* window (not a full
    season): recommend an application once per growth-stage transition
    observed within the window, since that's when the CROP_NPK_BASELINE
    table's per-stage values are meant to be applied.

        PSEUDOCODE (simple version — good enough for a 7-day dashboard):
        MIN_DAYS_BETWEEN_APPLICATIONS = 14  # avoid recommending two doses back-to-back
        if days_since_last_application is not None and days_since_last_application < MIN_DAYS_BETWEEN_APPLICATIONS:
            return False

        # Recommend on the first day of the plan (baseline "current state"
        # application) — refine this once you're tracking real application
        # history per field (would need a small DB table).
        return day_index_in_plan == 0

    A more complete version would key off a persisted "last application
    date" per field (requires adding simple storage — SQLite/Postgres — which
    is a reasonable v2 scope-add, not required for the initial demo).

    Returns:
        True if fertilizer should be recommended for this day.
    """
    raise NotImplementedError("TODO: implement application-day scheduling rule")
