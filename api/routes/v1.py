"""Versioned API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.schemas.common import (
    DataQualityOut,
    DistrictOut,
    EnvironmentalSampleOut,
    FacilityOut,
    HealthIndicatorOut,
    ImportRequest,
    MessageOut,
    MetadataOut,
    Page,
    RegionOut,
    ReportInfo,
    RiskCalculateRequest,
    RiskScoreOut,
    ValidateRequest,
)
from api.services.audit import write_audit
from api.services.auth import Principal, get_principal, require_roles
from database.models.entities import (
    AdminLevel,
    AdministrativeArea,
    DataQualityScore,
    DataSource,
    EnvironmentalSample,
    HealthFacility,
    HealthObservation,
    RiskIndicator,
)
from database.session import get_db

router = APIRouter(prefix="/api/v1")


def paginate(query, db: Session, page: int, page_size: int):
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return total, items


@router.get("/health")
def health():
    return {"status": "ok", "service": "envirolens-api"}


@router.get("/regions", response_model=Page[RegionOut])
def list_regions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(AdministrativeArea).where(AdministrativeArea.level == AdminLevel.region)
    total, items = paginate(q, db, page, page_size)
    return Page(
        items=[RegionOut(id=i.id, code=i.code, name=i.name, level=i.level.value) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/districts", response_model=Page[DistrictOut])
def list_districts(
    region_code: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(AdministrativeArea).where(AdministrativeArea.level == AdminLevel.district)
    if region_code:
        parent = db.scalar(
            select(AdministrativeArea).where(AdministrativeArea.code == region_code)
        )
        if parent:
            q = q.where(AdministrativeArea.parent_id == parent.id)
    total, items = paginate(q, db, page, page_size)
    return Page(
        items=[
            DistrictOut(
                id=i.id, code=i.code, name=i.name, level=i.level.value, parent_id=i.parent_id
            )
            for i in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/facilities", response_model=Page[FacilityOut])
def list_facilities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(HealthFacility)
    total, items = paginate(q, db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/environmental-samples", response_model=Page[EnvironmentalSampleOut])
def list_samples(
    pollutant: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(EnvironmentalSample)
    if pollutant:
        q = q.where(EnvironmentalSample.pollutant == pollutant)
    total, items = paginate(q, db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/health-indicators", response_model=Page[HealthIndicatorOut])
def list_health(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(HealthObservation)
    total, items = paginate(q, db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/risk-scores", response_model=Page[RiskScoreOut])
def list_risk(
    risk_band: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(RiskIndicator)
    if risk_band:
        q = q.where(RiskIndicator.risk_band == risk_band)
    total, items = paginate(q, db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/data-quality", response_model=Page[DataQualityOut])
def list_dq(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(DataQualityScore)
    total, items = paginate(q, db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/metadata", response_model=Page[MetadataOut])
def list_metadata(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    q = select(DataSource)
    total, items = paginate(q, db, page, page_size)
    mapped = [
        MetadataOut(
            id=i.id,
            dataset_name=i.dataset_name,
            owning_institution=i.owning_institution,
            geographic_coverage=i.geographic_coverage,
            reporting_frequency=i.reporting_frequency,
            data_quality_status=i.data_quality_status,
            sensitivity_level=i.sensitivity_level.value if i.sensitivity_level else None,
        )
        for i in items
    ]
    return Page(items=mapped, total=total, page=page, page_size=page_size)


@router.get("/reports", response_model=list[ReportInfo])
def list_reports(_: Principal = Depends(get_principal)):
    return [
        ReportInfo(
            name="Technical Report",
            path="reports/quarto/envirolens_technical_report.qmd",
            description="Methods, DQ, statistics, risk index",
        ),
        ReportInfo(
            name="Policy Brief",
            path="reports/policy_briefs/policy_brief.qmd",
            description="Two-page policy summary",
        ),
        ReportInfo(
            name="Data Quality Report",
            path="reports/data_quality/data_quality_report.qmd",
            description="Institution-facing DQ findings",
        ),
    ]


@router.post("/data/import", response_model=MessageOut)
def import_data(
    body: ImportRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles("admin", "analyst", "data_steward")),
):
    from pipelines.run import run_pipeline

    result = run_pipeline()
    write_audit(db, principal.username, "import", body.dataset, str(result))
    return MessageOut(status="ok", detail="Pipeline import completed", extras=result)


@router.post("/data/validate", response_model=MessageOut)
def validate_data(
    body: ValidateRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles("admin", "analyst", "data_steward")),
):
    from pipelines.ingestion.loaders import load_core_datasets, load_reference_frames
    from pipelines.cleaning.transforms import clean_environmental, clean_health, clean_population
    from pipelines.validation.dq_engine import (
        validate_environmental,
        validate_health,
        validate_population,
    )

    refs = load_reference_frames()
    core = load_core_datasets()
    if body.dataset == "environmental_samples":
        df = clean_environmental(core["environmental_samples"])
        districts = set(refs["admin"].loc[refs["admin"]["level"] == "district", "code"])
        res = validate_environmental(df, districts)
    elif body.dataset == "health_observations":
        df = clean_health(core["health_observations"])
        res = validate_health(df, set(refs["facilities"]["code"]))
    else:
        df = clean_population(core["population_estimates"])
        res = validate_population(df)
    write_audit(db, principal.username, "validate", body.dataset, f"overall={res.overall}")
    return MessageOut(
        status="ok",
        detail=f"Validated {body.dataset}",
        extras={"overall": res.overall, "issues": len(res.issues), "scores": res.scores},
    )


@router.post("/risk/calculate", response_model=MessageOut)
def calculate_risk_endpoint(
    body: RiskCalculateRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles("admin", "analyst")),
):
    from analysis.risk_model.calculate import calculate_risk
    from database.views.apply_views import apply_views

    df = calculate_risk(db)
    apply_views()
    write_audit(db, principal.username, "risk_calculate", "AP_EHRI", f"rows={len(df)}")
    return MessageOut(
        status="ok",
        detail="AP-EHRI recalculated",
        extras={"rows": len(df), "period_code": body.period_code},
    )
