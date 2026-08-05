"""Mock DHIS2-style integration endpoints and sync helpers."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models.entities import DHIS2SyncLog
from database.session import get_db
from pipelines.paths import JSON_DIR

router = APIRouter(prefix="/dhis2", tags=["dhis2-mock"])


class DataValue(BaseModel):
    dataElement: str
    period: str
    orgUnit: str
    value: str


class DataValueSet(BaseModel):
    dataValues: list[DataValue]


@router.get("/api/organisationUnits")
def organisation_units(db: Session = Depends(get_db)):
    path = JSON_DIR / "dhis2_mock_payload.json"
    if not path.exists():
        raise HTTPException(404, "Synthetic DHIS2 payload missing; run data generator")
    payload = json.loads(path.read_text(encoding="utf-8"))
    units = payload.get("organisationUnits", [])
    db.add(
        DHIS2SyncLog(
            direction="out",
            endpoint="/api/organisationUnits",
            status="success",
            records_count=len(units),
            message="Served mock organisation units",
        )
    )
    db.commit()
    return {"organisationUnits": units}


@router.post("/api/dataValueSets")
def import_data_value_sets(body: DataValueSet, db: Session = Depends(get_db)):
    ok = []
    failed = []
    for dv in body.dataValues:
        try:
            float(dv.value)
            ok.append(dv.orgUnit)
        except ValueError:
            failed.append(dv.orgUnit)
    status = "success" if not failed else "partial"
    db.add(
        DHIS2SyncLog(
            direction="in",
            endpoint="/api/dataValueSets",
            status=status,
            records_count=len(ok),
            message=f"accepted={len(ok)} failed={len(failed)}",
        )
    )
    db.commit()
    return {"status": status, "imported": len(ok), "failed": failed}


@router.get("/api/syncLogs")
def sync_logs(db: Session = Depends(get_db)):
    logs = db.query(DHIS2SyncLog).order_by(DHIS2SyncLog.id.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "direction": l.direction,
            "endpoint": l.endpoint,
            "status": l.status,
            "records_count": l.records_count,
            "message": l.message,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


def run_demo_sync(db: Session) -> dict:
    """Import synthetic payload into mock DHIS2 and log the transfer."""
    path = JSON_DIR / "dhis2_mock_payload.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("dataValueSets", {}).get("dataValues", [])
    body = DataValueSet(dataValues=[DataValue(**v) for v in values])
    # Call logic inline
    result = import_data_value_sets(body, db)
    return result
