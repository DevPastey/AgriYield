"""The crop catalogue is sourced from the FAO-56 PostgreSQL tables."""

from app.services.agrony_repository import list_supported_crops


def get_supported_crops() -> list[str]:
    return list_supported_crops()
