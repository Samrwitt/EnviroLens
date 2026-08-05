# Data Governance and Privacy Note

## Principles

EnviroLens uses **synthetic, anonymized, or publicly styled aggregate** datasets. The project does not publish personally identifiable health information.

## Controls implemented in the MVP

| Control | Implementation |
|---------|----------------|
| No direct identifiers | Facility/community codes only; no patient IDs |
| Aggregation | Health indicators are facility–period aggregates |
| Role-based access | API key → role claims (admin/analyst/viewer/steward) |
| Audit logging | `audit_logs` and `dhis2_sync_logs` tables |
| Secure configuration | Secrets via `.env` (not committed); `.env.example` provided |
| Sharing restrictions | Documented per dataset in metadata catalogue |
| AI outputs | Not enabled in MVP; any future AI text must be human-reviewed |

## Risk communication

AP-EHRI scores support **public-health prioritization** and are **not medical diagnoses**.

## Retention (recommended)

- Raw quarantine / rejected records: 90 days
- Integrated warehouse facts: retained for analytical history
- Audit logs: minimum 1 year

## Stewardship

Each dataset in `metadata/data_inventory/catalogue.yaml` names a data steward, owning institution, and sensitivity level.
