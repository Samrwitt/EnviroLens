"""Pydantic schemas for API responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class RegionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    level: str


class DistrictOut(RegionOut):
    parent_id: Optional[int] = None


class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    facility_type: str
    has_lab_access: bool
    community_id: Optional[int] = None


class EnvironmentalSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: int
    pollutant: str
    value: Optional[float] = None
    unit: str
    sample_date: Optional[date] = None
    is_valid: bool


class HealthIndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    facility_id: int
    indicator_code: str
    indicator_name: str
    value: Optional[float] = None
    period_id: int
    is_valid: bool


class RiskScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    community_id: int
    period_id: int
    index_code: str
    score: float
    risk_band: str
    methodology_version: str


class DataQualityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    dataset_name: str
    period_code: Optional[str] = None
    completeness: float
    validity: float
    consistency: float
    timeliness: float
    uniqueness: float
    geographic_accuracy: float
    overall: float


class MetadataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    dataset_name: str
    owning_institution: str
    geographic_coverage: Optional[str] = None
    reporting_frequency: Optional[str] = None
    data_quality_status: Optional[str] = None
    sensitivity_level: Optional[str] = None


class ReportInfo(BaseModel):
    name: str
    path: str
    description: str


class ImportRequest(BaseModel):
    source: str = Field(description="csv|excel|json|dhis2")
    dataset: str = "environmental_samples"


class ValidateRequest(BaseModel):
    dataset: str = "environmental_samples"


class RiskCalculateRequest(BaseModel):
    period_code: Optional[str] = None


class MessageOut(BaseModel):
    status: str
    detail: str
    extras: Optional[dict] = None
