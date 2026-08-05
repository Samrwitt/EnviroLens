# Power BI Dashboard — EnviroLens

Connect Power BI Desktop to PostgreSQL and use the reporting views.

## Connection

1. Get Data → PostgreSQL database
2. Server: `localhost` (or Compose host)
3. Database: `envirolens`
4. Use DirectQuery or Import

## Pages and views

| Dashboard page | SQL view | Purpose |
|----------------|----------|---------|
| Executive Overview | `vw_executive_overview` | KPIs: population, facilities, sites, high-risk count, DQ |
| Risk Analysis | `vw_risk_analysis` | Community AP-EHRI components and bands |
| Data Quality | `vw_data_quality` | Dimension scores by dataset |
| Health System Capacity | `vw_health_system_capacity` | Facilities, labs, monitoring by district |
| Interactive Map | `vw_risk_map` | Geometry + score for ArcGIS/Shape map visuals |

## Suggested filters

- Region / district / community (via district_code, community_code)
- Reporting period (`period_code`)
- Risk band
- Dataset name (DQ page)

## Refresh

After `python -m pipelines.run --all` and `python -m analysis.risk_model.calculate`, refresh the Power BI dataset.
