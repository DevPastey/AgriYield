"""Repository for FAO-56 crop data stored in PostgreSQL."""

from dataclasses import dataclass

from sqlalchemy import text

from app.core.database import engine
from app.schemas.recommendation import GrowthStage


@dataclass(frozen=True)
class CropStageProfile:
    name: str
    kc_value: float
    stage_duration_days: int
    root_depth_m: float
    base_n: float
    base_p: float
    base_k: float
    depletion_fraction: float


def list_supported_crops() -> list[str]:
    statement = text(
        """
        SELECT c.name
        FROM crops AS c
        JOIN crop_coefficients AS cc ON cc.crop_id = c.id
        GROUP BY c.id, c.name
        HAVING COUNT(DISTINCT cc.growth_stage) = 4
        ORDER BY c.name
        """
    )
    with engine.connect() as connection:
        return list(connection.execute(statement).scalars())


def get_crop_stage_profile(crop_type: str, growth_stage: GrowthStage) -> CropStageProfile:
    statement = text(
        """
        SELECT c.name, cc.kc_value, cc.stage_duration_days, cc.root_depth_m,
               cc.base_n, cc.base_p, cc.base_k, c.depletion_fraction
        FROM crops AS c
        JOIN crop_coefficients AS cc ON cc.crop_id = c.id
        WHERE c.name = :crop_name
          AND cc.growth_stage = CAST(:growth_stage AS growth_stage)
        """
    )
    with engine.connect() as connection:
        row = connection.execute(
            statement,
            {"crop_name": crop_type.strip().lower(), "growth_stage": growth_stage.value},
        ).mappings().one_or_none()
    if row is None:
        raise ValueError(f"No FAO-56 profile exists for {crop_type!r} at {growth_stage.value!r}.")
    return CropStageProfile(**{key: float(row[key]) if key.startswith(("kc_", "root_", "base_", "depletion_")) else row[key] for key in row})
