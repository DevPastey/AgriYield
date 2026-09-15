import pytest

from app.schemas.recommendation import GrowthStage
from app.services import (
    crop_catalog,
    evapotranspiration,
    fertilizer_engine,
    irrigation_engine,
)
from app.services.agrony_repository import CropStageProfile


@pytest.fixture
def stub_crop_profiles(monkeypatch):
    profile = CropStageProfile(
        name="maize",
        kc_value=1.15,
        stage_duration_days=40,
        root_depth_m=1.2,
        base_n=120.0,
        base_p=40.0,
        base_k=60.0,
        depletion_fraction=0.54,
    )

    def fake_get_crop_stage_profile(crop_type, growth_stage):
        if crop_type.strip().lower() != "maize" or growth_stage is not GrowthStage.DEVELOPMENT:
            raise ValueError(f"No FAO-56 profile exists for {crop_type!r} at {growth_stage.value!r}.")
        return profile

    monkeypatch.setattr(crop_catalog, "list_supported_crops", lambda: ["maize", "tomato", "cassava"])
    monkeypatch.setattr(evapotranspiration, "get_crop_stage_profile", fake_get_crop_stage_profile)
    monkeypatch.setattr(fertilizer_engine, "get_crop_stage_profile", fake_get_crop_stage_profile)
    monkeypatch.setattr(irrigation_engine, "get_crop_stage_profile", fake_get_crop_stage_profile)
