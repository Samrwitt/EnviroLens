# EnviroLens Technical Architecture

## Context

EnviroLens MVP demonstrates an integrated environmental-health intelligence platform for ambient air pollution (PM2.5 / NO₂) and respiratory outcomes in the fictional country **Verdania**.

## Component diagram

```mermaid
flowchart TD
  sources[Synthetic CSVs Excel JSON mock DHIS2]
  etl[Python ETL validation DQ Prefect]
  db[(PostgreSQL PostGIS Redis)]
  api[FastAPI]
  r[R Quarto]
  geo[GeoPandas QGIS Folium]
  bi[Power BI SQL views]
  sources --> etl --> db
  db --> api
  db --> r
  db --> geo
  db --> bi
```

## Entity-relationship overview

```mermaid
erDiagram
  ADMINISTRATIVE_AREAS ||--o{ COMMUNITIES : contains
  COMMUNITIES ||--o{ HEALTH_FACILITIES : served_by
  COMMUNITIES ||--o{ ENVIRONMENTAL_MONITORING_SITES : hosts
  COMMUNITIES ||--o{ POPULATION_ESTIMATES : has
  COMMUNITIES ||--o{ SOCIOECONOMIC_INDICATORS : has
  COMMUNITIES ||--o{ RISK_INDICATORS : scored
  HEALTH_FACILITIES ||--o{ HEALTH_OBSERVATIONS : reports
  ENVIRONMENTAL_MONITORING_SITES ||--o{ ENVIRONMENTAL_SAMPLES : measures
  REPORTING_PERIODS ||--o{ HEALTH_OBSERVATIONS : covers
  REPORTING_PERIODS ||--o{ ENVIRONMENTAL_SAMPLES : covers
  DATA_SOURCES ||--o{ ENVIRONMENTAL_SAMPLES : origins
  DATA_SOURCES ||--o{ DATA_QUALITY_SCORES : assessed
```

## Runtime services

| Service | Image / process | Port |
|---------|-----------------|------|
| PostGIS | postgis/postgis:16-3.4 | 5432 |
| Redis | redis:7-alpine | 6379 |
| API | uvicorn api.main:app | 8000 |

## Security (MVP)

- API key header (`X-API-Key`) with role stub (admin / analyst / viewer)
- Audit log table for import / validate / risk actions
- Synthetic aggregate data only

## Deployment note

Local Docker Compose is the supported MVP path. AWS deployment (ECS/RDS) is documented as a future Phase 7 activity.
