"""SQLAlchemy ORM models for EnviroLens (Verdania air-pollution MVP)."""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class AdminLevel(str, enum.Enum):
    country = "country"
    region = "region"
    district = "district"
    community = "community"


class SensitivityLevel(str, enum.Enum):
    public = "public"
    internal = "internal"
    restricted = "restricted"
    confidential = "confidential"


class DQDimension(str, enum.Enum):
    completeness = "completeness"
    validity = "validity"
    consistency = "consistency"
    timeliness = "timeliness"
    uniqueness = "uniqueness"
    geographic_accuracy = "geographic_accuracy"


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"
    data_steward = "data_steward"


class AdministrativeArea(Base):
    __tablename__ = "administrative_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    level: Mapped[AdminLevel] = mapped_column(Enum(AdminLevel), index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("administrative_areas.id"))
    geometry = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("AdministrativeArea", remote_side=[id], backref="children")
    communities = relationship("Community", back_populates="admin_area")


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    admin_area_id: Mapped[int] = mapped_column(ForeignKey("administrative_areas.id"), index=True)
    geometry = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    centroid = mapped_column(Geometry("POINT", srid=4326), nullable=True)

    admin_area = relationship("AdministrativeArea", back_populates="communities")
    population_estimates = relationship("PopulationEstimate", back_populates="community")
    socioeconomic_indicators = relationship("SocioeconomicIndicator", back_populates="community")
    risk_indicators = relationship("RiskIndicator", back_populates="community")


class HealthFacility(Base):
    __tablename__ = "health_facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    facility_type: Mapped[str] = mapped_column(String(64), default="clinic")
    community_id: Mapped[Optional[int]] = mapped_column(ForeignKey("communities.id"), index=True)
    admin_area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("administrative_areas.id"))
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    has_lab_access: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    community = relationship("Community")
    observations = relationship("HealthObservation", back_populates="facility")


class Laboratory(Base):
    __tablename__ = "laboratories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    admin_area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("administrative_areas.id"))
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    can_process_respiratory: Mapped[bool] = mapped_column(Boolean, default=True)


class EnvironmentalMonitoringSite(Base):
    __tablename__ = "environmental_monitoring_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    community_id: Mapped[Optional[int]] = mapped_column(ForeignKey("communities.id"), index=True)
    admin_area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("administrative_areas.id"))
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    site_type: Mapped[str] = mapped_column(String(64), default="ambient_air")

    samples = relationship("EnvironmentalSample", back_populates="site")


class ExposureSource(Base):
    __tablename__ = "exposure_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    source_type: Mapped[str] = mapped_column(String(64), default="industrial")
    pollutant: Mapped[str] = mapped_column(String(64), default="PM2.5")
    admin_area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("administrative_areas.id"))
    location = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    estimated_emission_index: Mapped[Optional[float]] = mapped_column(Float)


class ReportingPeriod(Base):
    __tablename__ = "reporting_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    label: Mapped[str] = mapped_column(String(64))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    period_type: Mapped[str] = mapped_column(String(32), default="quarter")


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(128), unique=True)
    owning_institution: Mapped[str] = mapped_column(String(128))
    ministry_or_department: Mapped[Optional[str]] = mapped_column(String(128))
    geographic_coverage: Mapped[Optional[str]] = mapped_column(String(128))
    reporting_frequency: Mapped[Optional[str]] = mapped_column(String(64))
    available_variables: Mapped[Optional[str]] = mapped_column(Text)
    data_format: Mapped[Optional[str]] = mapped_column(String(64))
    sensitivity_level: Mapped[SensitivityLevel] = mapped_column(
        Enum(SensitivityLevel), default=SensitivityLevel.internal
    )
    access_method: Mapped[Optional[str]] = mapped_column(String(64))
    data_steward: Mapped[Optional[str]] = mapped_column(String(128))
    data_quality_status: Mapped[Optional[str]] = mapped_column(String(64))
    last_update_date: Mapped[Optional[date]] = mapped_column(Date)
    sharing_restrictions: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)


class EnvironmentalSample(Base):
    __tablename__ = "environmental_samples"
    __table_args__ = (UniqueConstraint("site_id", "period_id", "pollutant", "sample_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("environmental_monitoring_sites.id"), index=True)
    period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"))
    pollutant: Mapped[str] = mapped_column(String(32), index=True)
    value: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(32), default="ug/m3")
    sample_date: Mapped[Optional[date]] = mapped_column(Date)
    data_source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("data_sources.id"))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    quality_flag: Mapped[Optional[str]] = mapped_column(String(64))

    site = relationship("EnvironmentalMonitoringSite", back_populates="samples")


class HealthObservation(Base):
    __tablename__ = "health_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("health_facilities.id"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("reporting_periods.id"), index=True)
    indicator_code: Mapped[str] = mapped_column(String(64), index=True)
    indicator_name: Mapped[str] = mapped_column(String(128))
    value: Mapped[Optional[float]] = mapped_column(Float)
    population_at_risk: Mapped[Optional[float]] = mapped_column(Float)
    age_group: Mapped[Optional[str]] = mapped_column(String(32))
    reported_at: Mapped[Optional[date]] = mapped_column(Date)
    data_source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("data_sources.id"))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)

    facility = relationship("HealthFacility", back_populates="observations")


class PopulationEstimate(Base):
    __tablename__ = "population_estimates"
    __table_args__ = (UniqueConstraint("community_id", "period_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("reporting_periods.id"), index=True)
    total_population: Mapped[Optional[int]] = mapped_column(Integer)
    under5: Mapped[Optional[int]] = mapped_column(Integer)
    elderly_65plus: Mapped[Optional[int]] = mapped_column(Integer)
    female: Mapped[Optional[int]] = mapped_column(Integer)
    male: Mapped[Optional[int]] = mapped_column(Integer)

    community = relationship("Community", back_populates="population_estimates")


class SocioeconomicIndicator(Base):
    __tablename__ = "socioeconomic_indicators"
    __table_args__ = (UniqueConstraint("community_id", "period_id", "indicator_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("reporting_periods.id"), index=True)
    indicator_code: Mapped[str] = mapped_column(String(64))
    indicator_name: Mapped[str] = mapped_column(String(128))
    value: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(32))

    community = relationship("Community", back_populates="socioeconomic_indicators")


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(128), index=True)
    dimension: Mapped[DQDimension] = mapped_column(Enum(DQDimension))
    severity: Mapped[str] = mapped_column(String(32), default="warning")
    record_ref: Mapped[Optional[str]] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DataQualityScore(Base):
    __tablename__ = "data_quality_scores"
    __table_args__ = (UniqueConstraint("dataset_name", "period_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(128), index=True)
    period_code: Mapped[Optional[str]] = mapped_column(String(32))
    completeness: Mapped[float] = mapped_column(Float, default=0.0)
    validity: Mapped[float] = mapped_column(Float, default=0.0)
    consistency: Mapped[float] = mapped_column(Float, default=0.0)
    timeliness: Mapped[float] = mapped_column(Float, default=0.0)
    uniqueness: Mapped[float] = mapped_column(Float, default=0.0)
    geographic_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    overall: Mapped[float] = mapped_column(Float, default=0.0)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskIndicator(Base):
    __tablename__ = "risk_indicators"
    __table_args__ = (UniqueConstraint("community_id", "period_id", "index_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("reporting_periods.id"), index=True)
    index_code: Mapped[str] = mapped_column(String(64), default="AP_EHRI")
    score: Mapped[float] = mapped_column(Float)
    risk_band: Mapped[str] = mapped_column(String(32))
    pm25_component: Mapped[Optional[float]] = mapped_column(Float)
    respiratory_component: Mapped[Optional[float]] = mapped_column(Float)
    proximity_component: Mapped[Optional[float]] = mapped_column(Float)
    vulnerability_component: Mapped[Optional[float]] = mapped_column(Float)
    poverty_component: Mapped[Optional[float]] = mapped_column(Float)
    access_component: Mapped[Optional[float]] = mapped_column(Float)
    completeness_component: Mapped[Optional[float]] = mapped_column(Float)
    methodology_version: Mapped[str] = mapped_column(String(32), default="1.0")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    community = relationship("Community", back_populates="risk_indicators")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    resource: Mapped[str] = mapped_column(String(128))
    detail: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AppUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(256))


class DHIS2SyncLog(Base):
    __tablename__ = "dhis2_sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    direction: Mapped[str] = mapped_column(String(16))
    endpoint: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
