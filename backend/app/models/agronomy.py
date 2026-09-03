import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class GrowthStage(str, enum.Enum):
    INITIAL = "initial"
    DEVELOPMENT = "development"
    MID_SEASON = "mid_season"
    LATE_SEASON = "late_season"

class SoilTexture(str, enum.Enum):
    SAND = "sand"
    LOAM = "loam"
    CLAY = "clay"
    # Extensible to loamy_sand, clay_loam, etc.

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # e.g., "maize", "tomato"
    scientific_name = Column(String, nullable=True)
    
    # Relationships
    coefficients = relationship("CropCoefficient", back_populates="crop", cascade="all, delete-orphan")
    fields = relationship("Field", back_populates="crop")

class CropCoefficient(Base):
    __tablename__ = "crop_coefficients"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    growth_stage = Column(Enum(GrowthStage), nullable=False)
    
    # FAO-56 Table 12 parameters
    kc_value = Column(Float, nullable=False)          # Point value or phase start value
    stage_duration_days = Column(Integer, nullable=False) # L_stage for target agro-zone
    root_depth_m = Column(Float, nullable=False)      # Rooting depth Z_r for this stage
    
    # Baseline Fertilizer needs (N - P - K in kg/ha)
    base_n = Column(Float, default=0.0)
    base_p = Column(Float, default=0.0)
    base_k = Column(Float, default=0.0)

    crop = relationship("Crop", back_populates="coefficients")

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    soil_texture = Column(Enum(SoilTexture), nullable=False)
    
    # Geographic location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, default=0.0)
    
    # Current lifecycle state markers
    planting_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    crop = relationship("Crop", back_populates="fields")
    activities = relationship("FieldActivity", back_populates="field", cascade="all, delete-orphan")

class FieldActivity(Base):
    __tablename__ = "field_activities"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String, nullable=False)  # "irrigation" or "fertilizer"
    amount_mm_or_kgha = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    field = relationship("Field", back_populates="activities")
