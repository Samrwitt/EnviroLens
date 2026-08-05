# EnviroLens

### Integrated Environmental Health Data and Risk Intelligence Platform

EnviroLens integrates environmental, health, demographic, socioeconomic, and geospatial datasets to help governments and health organizations identify high-risk communities, evaluate data quality, monitor trends, and make evidence-based decisions.

**MVP use case:** ambient air pollution (PM2.5 / NO₂) and respiratory health risk in the fictional country **Verdania**.

## Quick Start

```bash
cp .env.example .env
docker compose up -d db redis
pip install -r requirements.txt
python -m synthetic_data.generators.generate_all
alembic upgrade head
python -m pipelines.run --all
python -m analysis.risk_model.calculate
python -m database.views.apply_views
uvicorn api.main:app --reload
```

PostGIS is published on **5433** and Redis on **6380** by default (to avoid clashing with local services). OpenAPI docs: http://localhost:8000/docs

API key header: `X-API-Key: dev-api-key-change-me`

## Technology Stack

| Layer | Tools |
|-------|--------|
| Backend | FastAPI, Pydantic, SQLAlchemy, Alembic |
| Data engineering | Pandas, Prefect, OpenPyXL, Great Expectations patterns |
| Database | PostgreSQL, PostGIS, Redis |
| Analysis | R (tidyverse, ggplot2, sf), Quarto |
| Geospatial | GeoPandas, Shapely, PostGIS, QGIS, Leaflet/Folium |
| Dashboards | Power BI (SQL views), optional web |
| Integration | Mock DHIS2 connector |
| Infra | Docker Compose, GitHub Actions |

## Repository Layout

```
envirolens/
├── api/                 # FastAPI backend
├── pipelines/           # ETL, validation, DQ, loading
├── database/            # Models, migrations, views, seed
├── analysis/            # Python risk model, R scripts, indicators
├── geospatial/          # Boundaries, maps, QGIS, spatial SQL
├── dashboards/          # Power BI connection docs + views
├── reports/             # Quarto technical, policy, DQ reports
├── metadata/            # Inventory, dictionary, indicator registry
├── integrations/        # Mock DHIS2
├── synthetic_data/      # Generators + CSV/GeoJSON outputs
├── tests/
├── docs/
└── training/
```

## MVP Features

1. Metadata catalogue for dataset ownership and quality status
2. Automated Python ETL with intentional DQ defect detection
3. Data-quality scores (completeness, validity, consistency, timeliness, uniqueness, geographic accuracy)
4. PostgreSQL + PostGIS relational/spatial schema
5. Transparent **AP-EHRI** (Air Pollution Environmental-Health Risk Index)
6. R epidemiological analysis + Quarto reports
7. GeoPandas / PostGIS maps and QGIS project
8. FastAPI with auth stub, pagination, OpenAPI
9. Mock DHIS2 org-unit and aggregate sync
10. Power BI–ready SQL views

## Privacy

All data is **synthetic and aggregated**. No personally identifiable health information is included. Risk scores support public-health planning and are not medical diagnoses.

## License

MIT — see [LICENSE](LICENSE).
