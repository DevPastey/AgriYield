"""
Irrigation decision logic.

This is core agronomy logic — YOU implement it. Everything upstream
(weather data, ET calculations, soil texture) is wired and available;
this file turns that data into an actual "irrigate or don't" call.
"""

from app.schemas.recommendation import (
    DailyWeather,
    GrowthStage,
    IrrigationRecommendation,
    SoilTexture,
)

# TODO: Fill in real values — mm of total available water (TAW) per meter of
# root depth, by soil texture. Reference: FAO-56 Table 19 (Chapter 8) gives
# typical ranges; commonly cited midpoints (mm/m) to seed your table:
#
#     PSEUDOCODE / reference values (verify against FAO-56 Table 19):
#     sand            ~ 60-100   (use ~90)
#     loamy_sand      ~ 100-150  (use ~125)
#     sandy_loam      ~ 150-190  (use ~170)
#     loam            ~ 190-250  (use ~210)  # matches irrigation textbook "field capacity" heuristics
#     silt_loam       ~ 220-270  (use ~245)
#     silty_clay_loam ~ 200-240  (use ~220)
#     clay_loam       ~ 190-220  (use ~205)
#     clay            ~ 150-210  (use ~180)  # high TAW but low infiltration rate — note the tradeoff in comments
#
# Root depth (m) is crop- and growth-stage-specific (FAO-56 Table 22, e.g.
# maize ~1.0-1.7m at mid-season vs ~0.3m at initial stage) — you'll likely
# want a second small lookup table for that, keyed by crop_type + GrowthStage,
# since TAW for the root zone = SOIL_WATER_HOLDING_CAPACITY_MM_PER_M * root_depth_m.
SOIL_WATER_HOLDING_CAPACITY_MM_PER_M: dict[SoilTexture, float] = {
    # SoilTexture.SAND: 90.0,
    # SoilTexture.LOAM: 210.0,
    # SoilTexture.CLAY: 180.0,
}


def calculate_soil_moisture_deficit(
    previous_deficit_mm: float,
    soil_texture: SoilTexture,
    growth_stage: GrowthStage,
    recent_rainfall_mm: float,
    crop_water_requirement_mm: float,
    irrigation_applied_mm: float = 0.0,
) -> float:
    """
    TODO: Estimate the soil moisture deficit (mm) for the day, using a
    running "bucket model" (standard approach in FAO-56 Chapter 8, eq. 85).

        PSEUDOCODE (single-day update):
        effective_rainfall = min(recent_rainfall_mm, crop_water_requirement_mm)
        # simplification of FAO-56's more detailed effective-rainfall methods
        # (e.g. USDA SCS curve); a fixed efficiency factor is also common:
        #   effective_rainfall = recent_rainfall_mm * 0.8   (assume 20% runoff/deep percolation)

        deficit_today = previous_deficit_mm \
                        + crop_water_requirement_mm \
                        - effective_rainfall \
                        - irrigation_applied_mm

        deficit_today = clamp(deficit_today, lower=0, upper=root_zone_taw_mm)
        # root_zone_taw_mm = SOIL_WATER_HOLDING_CAPACITY_MM_PER_M[soil_texture] * root_depth_m(crop, growth_stage)
        # clamping at 0 = can't be wetter than field capacity (excess drains away)
        # clamping at TAW = a reasonable cap; beyond this the crop is already
        #   at permanent wilting point and further deficit tracking adds noise

        return deficit_today

    You'll call this once per day inside generate_irrigation_plan's loop,
    threading `previous_deficit_mm` from one day to the next (start at 0 for
    day 1, i.e. assume the field starts near field capacity — a reasonable
    default; make it a documented assumption).

    Returns:
        Soil moisture deficit in mm (0 = field capacity, higher = drier).
    """
    raise NotImplementedError("TODO: implement bucket-model soil moisture deficit")


def decide_irrigation(
    date_,
    weather: DailyWeather,
    soil_moisture_deficit_mm: float,
    management_allowed_depletion_mm: float,
    next_day_rainfall_forecast_mm: float = 0.0,
) -> IrrigationRecommendation:
    """
    TODO: Decide whether to irrigate on this day and how much.

    Management Allowed Depletion (MAD) is the standard FAO-56 concept
    (Chapter 8, eq. 83): irrigate before the deficit crosses a threshold
    fraction (p) of Total Available Water, since crops experience water
    stress before they're fully depleted.

        PSEUDOCODE:
        # management_allowed_depletion_mm = p * root_zone_taw_mm
        # typical p (depletion fraction) by crop, FAO-56 Table 22: ~0.5-0.6
        # for most field/vegetable crops (maize ~0.55, tomato ~0.4).

        significant_rain_coming = next_day_rainfall_forecast_mm >= 8.0
        # 8mm is a common rule-of-thumb threshold for "worth skipping
        # irrigation" — adjust based on your crop's sensitivity; document
        # whichever value you pick and why.

        if soil_moisture_deficit_mm >= management_allowed_depletion_mm:
            if significant_rain_coming:
                should_irrigate = False
                reasoning = (
                    f"Deficit ({soil_moisture_deficit_mm:.0f}mm) has reached the "
                    f"threshold ({management_allowed_depletion_mm:.0f}mm), but "
                    f"{next_day_rainfall_forecast_mm:.0f}mm of rain is forecast "
                    f"tomorrow — holding off irrigation."
                )
            else:
                should_irrigate = True
                # Common target: refill the deficit back to field capacity
                # (i.e. irrigate the full deficit), or apply a fixed
                # depth per application per your local practice.
                irrigation_amount_mm = soil_moisture_deficit_mm
                reasoning = (
                    f"Soil moisture deficit ({soil_moisture_deficit_mm:.0f}mm) exceeds "
                    f"the management-allowed threshold ({management_allowed_depletion_mm:.0f}mm) "
                    f"with no significant rain forecast — irrigate {irrigation_amount_mm:.0f}mm today."
                )
        else:
            should_irrigate = False
            reasoning = (
                f"Soil moisture deficit ({soil_moisture_deficit_mm:.0f}mm) is within "
                f"the safe threshold ({management_allowed_depletion_mm:.0f}mm) — no "
                f"irrigation needed today."
            )

        return IrrigationRecommendation(date=date_, should_irrigate=should_irrigate, ...)

    Write a clear `reasoning` string — this is what makes the dashboard
    feel like a real advisory tool rather than a black box.

    Returns:
        An IrrigationRecommendation for this single day.
    """
    raise NotImplementedError("TODO: implement irrigation decision rule")


def generate_irrigation_plan(
    daily_weather: list[DailyWeather],
    soil_texture: SoilTexture,
    growth_stage: GrowthStage,
    crop_type: str,
) -> list[IrrigationRecommendation]:
    """
    TODO: Orchestrate the day-by-day irrigation plan.

        PSEUDOCODE:
        deficit = 0.0  # assume field starts at/near field capacity — documented assumption
        root_zone_taw = SOIL_WATER_HOLDING_CAPACITY_MM_PER_M[soil_texture] * root_depth_m(crop_type, growth_stage)
        mad_threshold = depletion_fraction(crop_type) * root_zone_taw  # FAO-56 Table 22 'p' values

        recommendations = []
        for i, day in enumerate(daily_weather):
            etc = evapotranspiration.calculate_crop_water_requirement(
                day, crop_type, growth_stage, latitude, day_of_year(day.date)
            )
            deficit = calculate_soil_moisture_deficit(
                previous_deficit_mm=deficit,
                soil_texture=soil_texture,
                growth_stage=growth_stage,
                recent_rainfall_mm=day.rainfall_mm,
                crop_water_requirement_mm=etc,
            )
            next_day_rain = daily_weather[i + 1].rainfall_mm if i + 1 < len(daily_weather) else 0.0
            rec = decide_irrigation(day.date, day, deficit, mad_threshold, next_day_rain)

            if rec.should_irrigate:
                # irrigation refills the deficit — feed that back in so
                # tomorrow's bucket-model update starts from the new (lower) deficit
                deficit = max(0.0, deficit - (rec.irrigation_amount_mm or 0.0))

            recommendations.append(rec)

        return recommendations

    This loops over `daily_weather` in order, maintaining a running soil
    moisture deficit (see calculate_soil_moisture_deficit), calling
    evapotranspiration.calculate_crop_water_requirement() for each day, and
    calling decide_irrigation() to produce that day's recommendation.

    Returns:
        One IrrigationRecommendation per day in daily_weather.
    """
    raise NotImplementedError("TODO: implement the day-by-day orchestration loop")
