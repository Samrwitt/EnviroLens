"""Load cleaned frames into PostgreSQL / PostGIS."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from geoalchemy2.elements import WKTElement
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database.models.entities import (
    AdministrativeArea,
    AdminLevel,
    Community,
    DataQualityIssue,
    DataQualityScore,
    DataSource,
    DQDimension,
    EnvironmentalMonitoringSite,
    EnvironmentalSample,
    ExposureSource,
    HealthFacility,
    HealthObservation,
    Laboratory,
    PopulationEstimate,
    ReportingPeriod,
    SensitivityLevel,
    SocioeconomicIndicator,
)
from pipelines.paths import BOUNDARIES, ROOT
from pipelines.validation.dq_engine import DQResult


def _point(lon: float, lat: float) -> WKTElement:
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def _box_wkt(lon: float, lat: float, w: float = 0.35, h: float = 0.3) -> WKTElement:
    minx, maxx = lon - w / 2, lon + w / 2
    miny, maxy = lat - h / 2, lat + h / 2
    poly = (
        f"MULTIPOLYGON((({minx} {miny},{maxx} {miny},{maxx} {maxy},{minx} {maxy},{minx} {miny})))"
    )
    return WKTElement(poly, srid=4326)


def seed_metadata_catalogue(session: Session) -> None:
    path = ROOT / "metadata" / "data_inventory" / "catalogue.yaml"
    if not path.exists():
        return
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    # YAML is a markdown-ish list; also support structured list
    session.execute(delete(DataSource))
    defaults = [
        {
            "dataset_name": "Environmental Air Quality Samples",
            "owning_institution": "Verdania Environmental Protection Agency (VEPA)",
            "ministry_or_department": "Ministry of Environment",
            "geographic_coverage": "National",
            "reporting_frequency": "Quarterly",
            "available_variables": "site_code,pollutant,value,unit,sample_date",
            "data_format": "CSV/Excel",
            "sensitivity_level": SensitivityLevel.internal,
            "access_method": "file",
            "data_steward": "National Air Quality Coordinator",
            "data_quality_status": "monitored",
            "last_update_date": date(2024, 12, 31),
            "sharing_restrictions": "Aggregate public; site microdata internal",
            "description": "Ambient PM2.5 and NO2 measurements",
        },
        {
            "dataset_name": "Facility Respiratory Health Aggregates",
            "owning_institution": "Verdania Ministry of Health",
            "ministry_or_department": "Department of Epidemiology",
            "geographic_coverage": "National",
            "reporting_frequency": "Quarterly",
            "available_variables": "facility_code,indicator_code,value,population_at_risk",
            "data_format": "CSV/JSON/DHIS2",
            "sensitivity_level": SensitivityLevel.restricted,
            "access_method": "DHIS2 mock",
            "data_steward": "HIS Manager",
            "data_quality_status": "monitored",
            "last_update_date": date(2024, 12, 31),
            "sharing_restrictions": "Facility aggregates only",
            "description": "Respiratory encounter rates",
        },
        {
            "dataset_name": "Community Population and Socioeconomic Indicators",
            "owning_institution": "Verdania National Statistics Office",
            "ministry_or_department": "Ministry of Planning",
            "geographic_coverage": "National",
            "reporting_frequency": "Quarterly",
            "available_variables": "total_population,under5,elderly,poverty_index",
            "data_format": "CSV",
            "sensitivity_level": SensitivityLevel.public,
            "access_method": "open data",
            "data_steward": "Census Data Manager",
            "data_quality_status": "good",
            "last_update_date": date(2024, 12, 31),
            "sharing_restrictions": "Public aggregate statistics",
            "description": "Population and poverty indicators",
        },
    ]
    for d in defaults:
        session.add(DataSource(**d))
    session.flush()


def load_reference(session: Session, frames: dict) -> dict[str, dict[str, int]]:
    """Load admin hierarchy, facilities, sites, etc. Returns code->id maps."""
    session.execute(delete(EnvironmentalSample))
    session.execute(delete(HealthObservation))
    session.execute(delete(PopulationEstimate))
    session.execute(delete(SocioeconomicIndicator))
    session.execute(delete(ExposureSource))
    session.execute(delete(EnvironmentalMonitoringSite))
    session.execute(delete(HealthFacility))
    session.execute(delete(Laboratory))
    session.execute(delete(Community))
    session.execute(delete(AdministrativeArea))
    session.execute(delete(ReportingPeriod))
    session.flush()

    level_map = {
        "country": AdminLevel.country,
        "region": AdminLevel.region,
        "district": AdminLevel.district,
        "community": AdminLevel.community,
    }

    admin_ids: dict[str, int] = {}
    # Load parents before children by level order
    admin_df = frames["admin"].copy()
    order = {"country": 0, "region": 1, "district": 2, "community": 3}
    admin_df["_ord"] = admin_df["level"].map(order)
    admin_df = admin_df.sort_values("_ord")

    for _, row in admin_df.iterrows():
        parent_id = admin_ids.get(row["parent_code"]) if pd_notna(row.get("parent_code")) else None
        obj = AdministrativeArea(
            code=row["code"],
            name=row["name"],
            level=level_map[row["level"]],
            parent_id=parent_id,
            geometry=_box_wkt(float(row["lon"]), float(row["lat"])),
        )
        session.add(obj)
        session.flush()
        admin_ids[row["code"]] = obj.id

    period_ids: dict[str, int] = {}
    for _, row in frames["periods"].iterrows():
        obj = ReportingPeriod(
            code=row["code"],
            label=row["label"],
            start_date=pd_to_date(row["start_date"]),
            end_date=pd_to_date(row["end_date"]),
            period_type=row.get("period_type", "quarter"),
        )
        session.add(obj)
        session.flush()
        period_ids[row["code"]] = obj.id

    community_ids: dict[str, int] = {}
    for _, row in frames["communities"].iterrows():
        district_id = admin_ids[row["district_code"]]
        obj = Community(
            code=row["code"],
            name=row["name"],
            admin_area_id=district_id,
            geometry=_box_wkt(float(row["lon"]), float(row["lat"]), 0.1, 0.08),
            centroid=_point(float(row["lon"]), float(row["lat"])),
        )
        session.add(obj)
        session.flush()
        community_ids[row["code"]] = obj.id

    facility_ids: dict[str, int] = {}
    for _, row in frames["facilities"].iterrows():
        obj = HealthFacility(
            code=row["code"],
            name=row["name"],
            facility_type=row.get("facility_type", "clinic"),
            community_id=community_ids.get(row["community_code"]),
            admin_area_id=admin_ids.get(row["district_code"]),
            location=_point(float(row["lon"]), float(row["lat"])),
            has_lab_access=bool(row.get("has_lab_access", False)),
        )
        session.add(obj)
        session.flush()
        facility_ids[row["code"]] = obj.id

    site_ids: dict[str, int] = {}
    for _, row in frames["sites"].iterrows():
        obj = EnvironmentalMonitoringSite(
            code=row["code"],
            name=row["name"],
            community_id=community_ids.get(row["community_code"]),
            admin_area_id=admin_ids.get(row["district_code"]),
            location=_point(float(row["lon"]), float(row["lat"])),
            site_type=row.get("site_type", "ambient_air"),
        )
        session.add(obj)
        session.flush()
        site_ids[row["code"]] = obj.id

    for _, row in frames["sources"].iterrows():
        session.add(
            ExposureSource(
                code=row["code"],
                name=row["name"],
                source_type=row.get("source_type", "industrial"),
                pollutant=row.get("pollutant", "PM2.5"),
                admin_area_id=admin_ids.get(row["district_code"]),
                location=_point(float(row["lon"]), float(row["lat"])),
                estimated_emission_index=float(row["estimated_emission_index"])
                if pd_notna(row.get("estimated_emission_index"))
                else None,
            )
        )

    for _, row in frames["labs"].iterrows():
        session.add(
            Laboratory(
                code=row["code"],
                name=row["name"],
                admin_area_id=admin_ids.get(row["district_code"]),
                location=_point(float(row["lon"]), float(row["lat"])),
                can_process_respiratory=bool(row.get("can_process_respiratory", True)),
            )
        )

    session.flush()
    return {
        "admin": admin_ids,
        "periods": period_ids,
        "communities": community_ids,
        "facilities": facility_ids,
        "sites": site_ids,
    }


def pd_notna(v) -> bool:
    if v is None:
        return False
    try:
        import pandas as pd

        return not pd.isna(v)
    except Exception:
        return True


def pd_to_date(v):
    import pandas as pd

    if isinstance(v, date):
        return v
    return pd.to_datetime(v).date()


def persist_dq(session: Session, results: list[DQResult]) -> None:
    session.execute(delete(DataQualityIssue))
    session.execute(delete(DataQualityScore))
    dim_map = {d.value: d for d in DQDimension}
    for res in results:
        for issue in res.issues:
            session.add(
                DataQualityIssue(
                    dataset_name=issue.dataset_name,
                    dimension=dim_map[issue.dimension],
                    severity=issue.severity,
                    record_ref=issue.record_ref,
                    message=issue.message,
                )
            )
        session.add(
            DataQualityScore(
                dataset_name=res.dataset_name,
                period_code="2024",
                completeness=res.scores.get("completeness", 0),
                validity=res.scores.get("validity", 0),
                consistency=res.scores.get("consistency", 0),
                timeliness=res.scores.get("timeliness", 0),
                uniqueness=res.scores.get("uniqueness", 0),
                geographic_accuracy=res.scores.get("geographic_accuracy", 0),
                overall=res.overall,
            )
        )
    session.flush()


def load_fact_tables(session: Session, ids: dict, datasets: dict) -> None:
    ds = session.execute(select(DataSource)).scalars().all()
    ds_by_name = {d.dataset_name: d.id for d in ds}
    env_src = ds_by_name.get("Environmental Air Quality Samples")
    health_src = ds_by_name.get("Facility Respiratory Health Aggregates")

    env = datasets["environmental_samples"]
    for _, row in env.iterrows():
        site_id = ids["sites"].get(row["site_code"])
        if not site_id:
            continue
        session.add(
            EnvironmentalSample(
                site_id=site_id,
                period_id=ids["periods"].get(row["period_code"]),
                pollutant=row["pollutant"],
                value=float(row["value"]) if pd_notna(row["value"]) else None,
                unit=row.get("unit", "ug/m3"),
                sample_date=row["sample_date"] if pd_notna(row.get("sample_date")) else None,
                data_source_id=env_src,
                is_valid=bool(row.get("is_valid", True)),
                quality_flag=None if row.get("is_valid", True) else "rejected",
            )
        )

    health = datasets["health_observations"]
    for _, row in health.iterrows():
        fac_id = ids["facilities"].get(row["facility_code"])
        period_id = ids["periods"].get(row["period_code"])
        if not fac_id or not period_id:
            continue
        session.add(
            HealthObservation(
                facility_id=fac_id,
                period_id=period_id,
                indicator_code=row["indicator_code"],
                indicator_name=row.get("indicator_name", row["indicator_code"]),
                value=float(row["value"]) if pd_notna(row["value"]) else None,
                population_at_risk=float(row["population_at_risk"])
                if pd_notna(row.get("population_at_risk"))
                else None,
                age_group=row.get("age_group"),
                reported_at=row["reported_at"] if pd_notna(row.get("reported_at")) else None,
                data_source_id=health_src,
                is_valid=bool(row.get("is_valid", True)),
            )
        )

    for _, row in datasets["population_estimates"].iterrows():
        cid = ids["communities"].get(row["community_code"])
        pid = ids["periods"].get(row["period_code"])
        if not cid or not pid:
            continue
        session.add(
            PopulationEstimate(
                community_id=cid,
                period_id=pid,
                total_population=int(row["total_population"])
                if pd_notna(row.get("total_population"))
                else None,
                under5=int(row["under5"]) if pd_notna(row.get("under5")) else None,
                elderly_65plus=int(row["elderly_65plus"])
                if pd_notna(row.get("elderly_65plus"))
                else None,
                female=int(row["female"]) if pd_notna(row.get("female")) else None,
                male=int(row["male"]) if pd_notna(row.get("male")) else None,
            )
        )

    for _, row in datasets["socioeconomic_indicators"].iterrows():
        cid = ids["communities"].get(row["community_code"])
        pid = ids["periods"].get(row["period_code"])
        if not cid or not pid:
            continue
        session.add(
            SocioeconomicIndicator(
                community_id=cid,
                period_id=pid,
                indicator_code=row["indicator_code"],
                indicator_name=row.get("indicator_name", row["indicator_code"]),
                value=float(row["value"]) if pd_notna(row.get("value")) else None,
                unit=row.get("unit"),
            )
        )
    session.flush()
