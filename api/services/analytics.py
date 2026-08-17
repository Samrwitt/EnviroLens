"""Aggregations for dashboard visualizations."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session


def dashboard_payload(db: Session) -> dict:
    latest = db.execute(
        text("SELECT id, code, label FROM reporting_periods ORDER BY end_date DESC LIMIT 1")
    ).mappings().first()
    latest_id = latest["id"] if latest else None
    latest_code = latest["code"] if latest else None
    latest_label = latest["label"] if latest else None

    kpis = db.execute(
        text(
            """
            SELECT
              (SELECT COUNT(*) FROM communities) AS communities,
              (SELECT COUNT(*) FROM health_facilities WHERE is_active) AS facilities,
              (SELECT COUNT(*) FROM environmental_monitoring_sites) AS monitoring_sites,
              (SELECT COUNT(*) FROM exposure_sources) AS exposure_sources,
              (SELECT COUNT(*) FROM risk_indicators
                 WHERE period_id = :pid AND risk_band IN ('high','very_high')) AS high_risk,
              (SELECT ROUND(AVG(score)::numeric, 4) FROM risk_indicators
                 WHERE period_id = :pid) AS mean_ap_ehri,
              (SELECT ROUND(AVG(overall)::numeric, 4) FROM data_quality_scores) AS overall_dq,
              (SELECT COALESCE(SUM(total_population), 0) FROM population_estimates
                 WHERE period_id = :pid) AS population,
              (SELECT COALESCE(SUM(COALESCE(under5,0) + COALESCE(elderly_65plus,0)), 0)
                 FROM population_estimates WHERE period_id = :pid) AS vulnerable,
              (SELECT ROUND(AVG(value)::numeric, 2) FROM environmental_samples
                 WHERE pollutant = 'PM2.5' AND is_valid AND period_id = :pid) AS mean_pm25,
              (SELECT ROUND(AVG(value)::numeric, 2) FROM health_observations
                 WHERE indicator_code = 'RESP_ENC_RATE' AND is_valid
                   AND period_id = :pid) AS mean_resp
            """
        ),
        {"pid": latest_id},
    ).mappings().one()

    risk_by_band = db.execute(
        text(
            """
            SELECT risk_band AS band, COUNT(*) AS count
            FROM risk_indicators
            WHERE period_id = :pid
            GROUP BY risk_band
            """
        ),
        {"pid": latest_id},
    ).mappings().all()

    risk_by_period = db.execute(
        text(
            """
            SELECT rp.code AS period, rp.label,
                   ROUND(AVG(ri.score)::numeric, 4) AS mean_score,
                   COUNT(*) FILTER (WHERE ri.risk_band IN ('high','very_high')) AS elevated,
                   COUNT(*) AS n
            FROM risk_indicators ri
            JOIN reporting_periods rp ON rp.id = ri.period_id
            GROUP BY rp.code, rp.label, rp.end_date
            ORDER BY rp.end_date
            """
        )
    ).mappings().all()

    top_communities = db.execute(
        text(
            """
            SELECT c.name AS community, c.code AS community_code, a.name AS district,
                   ri.score, ri.risk_band AS band,
                   ri.pm25_component, ri.respiratory_component, ri.proximity_component,
                   ri.vulnerability_component, ri.poverty_component, ri.access_component
            FROM risk_indicators ri
            JOIN communities c ON c.id = ri.community_id
            JOIN administrative_areas a ON a.id = c.admin_area_id
            WHERE ri.period_id = :pid
            ORDER BY ri.score DESC
            LIMIT 12
            """
        ),
        {"pid": latest_id},
    ).mappings().all()

    histogram = db.execute(
        text(
            """
            SELECT bucket, COUNT(*) AS count FROM (
              SELECT CASE
                WHEN score < 0.20 THEN '0.00–0.20'
                WHEN score < 0.35 THEN '0.20–0.35'
                WHEN score < 0.55 THEN '0.35–0.55'
                WHEN score < 0.75 THEN '0.55–0.75'
                ELSE '0.75–1.00'
              END AS bucket,
              CASE
                WHEN score < 0.20 THEN 1
                WHEN score < 0.35 THEN 2
                WHEN score < 0.55 THEN 3
                WHEN score < 0.75 THEN 4
                ELSE 5
              END AS ord
              FROM risk_indicators WHERE period_id = :pid
            ) t
            GROUP BY bucket, ord
            ORDER BY ord
            """
        ),
        {"pid": latest_id},
    ).mappings().all()

    stacked_bands = db.execute(
        text(
            """
            SELECT rp.code AS period,
                   COUNT(*) FILTER (WHERE ri.risk_band = 'low') AS low,
                   COUNT(*) FILTER (WHERE ri.risk_band = 'moderate') AS moderate,
                   COUNT(*) FILTER (WHERE ri.risk_band = 'high') AS high,
                   COUNT(*) FILTER (WHERE ri.risk_band = 'very_high') AS very_high
            FROM risk_indicators ri
            JOIN reporting_periods rp ON rp.id = ri.period_id
            GROUP BY rp.code, rp.end_date
            ORDER BY rp.end_date
            """
        )
    ).mappings().all()

    component_means = db.execute(
        text(
            """
            SELECT ROUND(AVG(pm25_component)::numeric, 3) AS "PM2.5",
                   ROUND(AVG(respiratory_component)::numeric, 3) AS "Respiratory",
                   ROUND(AVG(proximity_component)::numeric, 3) AS "Proximity",
                   ROUND(AVG(vulnerability_component)::numeric, 3) AS "Vulnerability",
                   ROUND(AVG(poverty_component)::numeric, 3) AS "Poverty",
                   ROUND(AVG(access_component)::numeric, 3) AS "Access gap",
                   ROUND(AVG(completeness_component)::numeric, 3) AS "Incompleteness"
            FROM risk_indicators WHERE period_id = :pid
            """
        ),
        {"pid": latest_id},
    ).mappings().first()

    pollution_trend = db.execute(
        text(
            """
            SELECT rp.code AS period,
                   ROUND(AVG(es.value) FILTER (WHERE es.pollutant = 'PM2.5' AND es.is_valid)::numeric, 2) AS pm25,
                   ROUND(AVG(es.value) FILTER (WHERE es.pollutant = 'NO2' AND es.is_valid)::numeric, 2) AS no2
            FROM reporting_periods rp
            LEFT JOIN environmental_samples es ON es.period_id = rp.id
            GROUP BY rp.code, rp.end_date
            ORDER BY rp.end_date
            """
        )
    ).mappings().all()

    health_trend = db.execute(
        text(
            """
            SELECT rp.code AS period,
                   ROUND(AVG(ho.value) FILTER (WHERE ho.is_valid)::numeric, 2) AS resp_rate
            FROM reporting_periods rp
            LEFT JOIN health_observations ho
              ON ho.period_id = rp.id AND ho.indicator_code = 'RESP_ENC_RATE'
            GROUP BY rp.code, rp.end_date
            ORDER BY rp.end_date
            """
        )
    ).mappings().all()

    dq = db.execute(
        text(
            """
            SELECT dataset_name, completeness, validity, consistency,
                   timeliness, uniqueness, geographic_accuracy, overall
            FROM data_quality_scores
            ORDER BY dataset_name
            """
        )
    ).mappings().all()

    facility_types = db.execute(
        text(
            """
            SELECT facility_type AS type, COUNT(*) AS count
            FROM health_facilities
            GROUP BY facility_type
            ORDER BY count DESC
            """
        )
    ).mappings().all()

    lab_access = db.execute(
        text(
            """
            SELECT CASE WHEN has_lab_access THEN 'With lab access' ELSE 'No lab access' END AS label,
                   COUNT(*) AS count
            FROM health_facilities
            GROUP BY has_lab_access
            """
        )
    ).mappings().all()

    district_risk = db.execute(
        text(
            """
            SELECT a.name AS district,
                   ROUND(AVG(ri.score)::numeric, 3) AS mean_score,
                   COUNT(*) FILTER (WHERE ri.risk_band IN ('high','very_high')) AS elevated
            FROM risk_indicators ri
            JOIN communities c ON c.id = ri.community_id
            JOIN administrative_areas a ON a.id = c.admin_area_id
            WHERE ri.period_id = :pid
            GROUP BY a.name
            ORDER BY mean_score DESC
            """
        ),
        {"pid": latest_id},
    ).mappings().all()

    comps = []
    if component_means:
        for key, value in component_means.items():
            comps.append({"component": key, "value": float(value) if value is not None else 0})

    band_rows = [_row(r) for r in risk_by_band]
    band_total = sum(int(r["count"]) for r in band_rows) or 1
    for r in band_rows:
        r["share"] = round(int(r["count"]) / band_total, 4)

    return {
        "latest_period": latest_code,
        "latest_period_label": latest_label,
        "kpis": {
            "communities": int(kpis["communities"] or 0),
            "facilities": int(kpis["facilities"] or 0),
            "monitoring_sites": int(kpis["monitoring_sites"] or 0),
            "exposure_sources": int(kpis["exposure_sources"] or 0),
            "high_risk": int(kpis["high_risk"] or 0),
            "mean_ap_ehri": float(kpis["mean_ap_ehri"] or 0),
            "overall_dq": float(kpis["overall_dq"] or 0),
            "population": int(kpis["population"] or 0),
            "vulnerable": int(kpis["vulnerable"] or 0),
            "mean_pm25": float(kpis["mean_pm25"] or 0),
            "mean_resp": float(kpis["mean_resp"] or 0),
        },
        "risk_by_band": band_rows,
        "risk_by_period": [_row(r) for r in risk_by_period],
        "top_communities": [_row(r) for r in top_communities],
        "score_histogram": [_row(r) for r in histogram],
        "stacked_bands": [_row(r) for r in stacked_bands],
        "component_means": comps,
        "pollution_trend": [_row(r) for r in pollution_trend],
        "health_trend": [_row(r) for r in health_trend],
        "data_quality": [_row(r) for r in dq],
        "facility_types": [_row(r) for r in facility_types],
        "lab_access": [_row(r) for r in lab_access],
        "district_risk": [_row(r) for r in district_risk],
    }


def _row(mapping) -> dict:
    out = {}
    for k, v in dict(mapping).items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out
