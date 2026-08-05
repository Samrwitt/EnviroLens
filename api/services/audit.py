"""Audit logging helpers."""

from sqlalchemy.orm import Session

from database.models.entities import AuditLog


def write_audit(db: Session, actor: str, action: str, resource: str, detail: str | None = None) -> None:
    db.add(AuditLog(actor=actor, action=action, resource=resource, detail=detail))
    db.commit()
