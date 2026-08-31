"""
Evapotranspiration calculations.

This is core agronomy logic — YOU implement it. The function signatures
and docstrings below define the contract the rest of the app expects,
so you can build/test this file in isolation.
"""

from app.schemas.recommendation import DailyWeather, GrowthStage


def calculate_reference_et(weather: DailyWeather, latitude: float, day_of_year: int) -> float:
    """
    TODO: Calculate reference evapotranspiration (ET0) in mm/day.

    You have two standard options. Given the weather API only supplies
    temp/humidity/wind (no solar radiation or pressure), Hargreaves is the
    realistic choice for this project — Penman-Monteith is included below
    for reference/comparison if you ever add a radiation data source.

    Reference: FAO Irrigation and Drainage Paper 56, Chapter 2-4.
    http://www.fao.org/3/x0490e/x0490e00.htm

    --- OPTION A: Hargreaves equation (recommended — matches available data) ---
    Needs only Tmin, Tmax, and extraterrestrial radiation (Ra), which is a
    function of latitude + day-of-year alone (no measured radiation needed).

        PSEUDOCODE:
        tmean = (tmax_c + tmin_c) / 2
        ra = calculate_extraterrestrial_radiation(latitude, day_of_year)  # MJ/m^2/day, see helper below
        et0 = 0.0023 * (tmean + 17.8) * sqrt(tmax_c - tmin_c) * ra_to_mm(ra)
        # ra_to_mm: multiply Ra (MJ/m^2/day) by 0.408 to convert to mm/day
        # equivalent (FAO-56 eq. 52): ET0 = 0.0023 * (Tmean + 17.8) * (Tmax - Tmin)^0.5 * 0.408 * Ra

    --- OPTION B: FAO-56 Penman-Monteith (full form, needs Rn, G, es, ea, Δ, γ) ---
    Only pursue this if you extend the weather integration to also pull solar
    radiation and atmospheric pressure (not available from OpenWeatherMap's
    free tier without extra endpoints).

        PSEUDOCODE (FAO-56 eq. 6):
        et0 = (0.408 * delta * (Rn - G) + gamma * (900 / (Tmean + 273)) * u2 * (es - ea)) \
              / (delta + gamma * (1 + 0.34 * u2))
        # delta = slope of saturation vapor pressure curve (kPa/°C), f(Tmean)
        # gamma  = psychrometric constant (kPa/°C), f(atmospheric pressure)
        # es     = saturation vapor pressure (kPa), f(Tmax, Tmin)
        # ea     = actual vapor pressure (kPa), f(es, humidity_pct)
        # Rn     = net radiation at surface (MJ/m^2/day) — NOT currently available
        # G      = soil heat flux density (~0 for daily calcs)
        # u2     = wind speed at 2m height (m/s) — adjust wind_speed_ms if measured elsewhere

    Helper you'll also need for Option A:

        def calculate_extraterrestrial_radiation(latitude_deg, day_of_year) -> float:
            '''FAO-56 eq. 21-25: Ra (MJ/m^2/day) from latitude + Julian day.
            Involves solar declination, sunset hour angle, and inverse
            relative distance Earth-Sun. Fully derivable from lat + day_of_year
            alone — no external data needed. See FAO-56 Annex 2 for the
            step-by-step formula.'''
            raise NotImplementedError

    Returns:
        ET0 in mm/day.
    """
    raise NotImplementedError("TODO: implement reference ET calculation (Hargreaves recommended)")


def get_crop_coefficient(crop_type: str, growth_stage: GrowthStage) -> float:
    """
    TODO: Return the crop coefficient (Kc) for the given crop and growth stage.

    Reference: FAO-56 Table 12 (Chapter 6) — single crop coefficients for
    initial, mid-season, and late-season stages, for ~80 crops.
    http://www.fao.org/3/x0490e/x0490e0b.htm#TopOfPage

    FAO-56 only gives you 3 stage values (Kc_ini, Kc_mid, Kc_late); "development"
    is the linear ramp between Kc_ini and Kc_mid, and "late_season" itself often
    ramps down to Kc_end. A reasonable simplification for a 7-day forecast
    window is to treat each of the 4 GrowthStage values as a fixed point rather
    than interpolating continuously — document that simplification if you take it.

    Selected FAO-56 Table 12 reference values to seed your table (verify
    against the source table before using — these vary by climate too):

        PSEUDOCODE / reference table:
        maize:   Kc_ini=0.3,  Kc_mid=1.20, Kc_late=0.60-0.35 (fresh/dry harvest)
        tomato:  Kc_ini=0.6,  Kc_mid=1.15, Kc_late=0.70-0.90
        cassava: not in FAO-56's core table — commonly cited in agronomy
                 literature around Kc_ini=0.3, Kc_mid=0.8-1.1 depending on
                 canopy closure; cite whichever regional study you use.

    Build the lookup as:
        CROP_KC: dict[str, dict[GrowthStage, float]] = {
            "maize": {
                GrowthStage.INITIAL: 0.3,
                GrowthStage.DEVELOPMENT: ...,   # interpolate toward Kc_mid
                GrowthStage.MID_SEASON: 1.20,
                GrowthStage.LATE_SEASON: ...,   # interpolate toward Kc_late
            },
            ...
        }

    Start with the 2-3 crops you're demoing, not all of FAO-56 — depth over
    breadth for a portfolio project. Move this table to app/data/ once it grows.

    Returns:
        Dimensionless Kc value, typically 0.3–1.2.
    """
    raise NotImplementedError("TODO: implement Kc lookup")


def calculate_crop_water_requirement(
    weather: DailyWeather, crop_type: str, growth_stage: GrowthStage, latitude: float, day_of_year: int
) -> float:
    """
    TODO: Calculate crop evapotranspiration (ETc) in mm/day.

    Reference: FAO-56 Chapter 6, eq. 58.

        PSEUDOCODE:
        et0 = calculate_reference_et(weather, latitude, day_of_year)
        kc = get_crop_coefficient(crop_type, growth_stage)
        etc = et0 * kc
        return etc

    Edge cases worth handling explicitly:
    - Very wet days (rainfall_mm high): ETc as computed still holds — it's
      demand-side, not supply-side. Don't zero it out; that's
      irrigation_engine's job when it nets ETc against rainfall.
    - Missing/None Kc for an unsupported crop_type: raise a clear error
      rather than silently defaulting to Kc=1.0.

    This is the number irrigation_engine.py will compare against rainfall
    and soil water-holding capacity to decide whether to irrigate.

    Returns:
        ETc in mm/day.
    """
    raise NotImplementedError("TODO: combine et0 * kc, handle edge cases (e.g. unsupported crop_type)")
