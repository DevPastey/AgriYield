"""PostgreSQL access for agronomic reference data."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required to load agronomic data.")
    database_url = settings.database_url
    # psycopg 3 is the project's supported PostgreSQL driver. Accept the
    # conventional `postgresql://` form already present in existing .env files.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(database_url, pool_pre_ping=True)
