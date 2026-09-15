import importlib

import pytest

from app.core import config, database


def test_database_engine_is_initialized_lazily(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    config.get_settings.cache_clear()
    reloaded_database = importlib.reload(database)

    with pytest.raises(RuntimeError, match="DATABASE_URL is required to load agronomic data."):
        reloaded_database.get_engine()
