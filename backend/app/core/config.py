"""
Centralized application configuration.

All environment-dependent values live here so the rest of the codebase
never calls os.environ directly. Backed by pydantic-settings, which reads
from `.env` automatically.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_env: str = "development"
    app_name: str = "AgriYield-API"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # --- OpenWeatherMap ---
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    openweather_geo_url: str = "https://api.openweathermap.org/geo/1.0"
    openweather_use_onecall: bool = False

    # --- Caching ---
    weather_cache_ttl_seconds: int = 1800

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — import and call this, don't instantiate Settings() directly."""
    return Settings()
