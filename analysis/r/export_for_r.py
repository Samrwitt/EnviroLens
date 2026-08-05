"""Export analysis CSVs for R / Quarto consumption."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database.session import engine

OUT = Path(__file__).resolve().parent / "exports"
OUT.mkdir(parents=True, exist_ok=True)


def export_all() -> None:
    queries = {
        "risk_scores.csv": """
            SELECT c.code AS community_code, a.code AS district_code, rp.code AS period_code,
                   ri.score, ri.risk_band, ri.pm25_component, ri.respiratory_component
            FROM risk_indicators ri
            JOIN communities c ON c.id = ri.community_id
            JOIN administrative_areas a ON a.id = c.admin_area_id
            JOIN reporting_periods rp ON rp.id = ri.period_id
        """,
        "environmental_pm25.csv": """
            SELECT c.code AS community_code, rp.code AS period_code, AVG(es.value) AS mean_pm25
            FROM environmental_samples es
            JOIN environmental_monitoring_sites s ON s.id = es.site_id
            JOIN communities c ON c.id = s.community_id
            JOIN reporting_periods rp ON rp.id = es.period_id
            WHERE es.pollutant = 'PM2.5' AND es.is_valid
            GROUP BY c.code, rp.code
        """,
        "health_resp.csv": """
            SELECT c.code AS community_code, rp.code AS period_code, AVG(ho.value) AS mean_resp
            FROM health_observations ho
            JOIN health_facilities f ON f.id = ho.facility_id
            JOIN communities c ON c.id = f.community_id
            JOIN reporting_periods rp ON rp.id = ho.period_id
            WHERE ho.indicator_code = 'RESP_ENC_RATE' AND ho.is_valid
            GROUP BY c.code, rp.code
        """,
        "data_quality.csv": """
            SELECT dataset_name, completeness, validity, consistency, timeliness,
                   uniqueness, geographic_accuracy, overall
            FROM data_quality_scores
        """,
    }
    with engine.connect() as conn:
        for name, sql in queries.items():
            df = pd.read_sql(text(sql), conn)
            df.to_csv(OUT / name, index=False)
            print(f"Wrote {OUT / name} ({len(df)} rows)")


if __name__ == "__main__":
    export_all()
