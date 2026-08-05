"""Calculate AP-EHRI community risk scores and write to risk_indicators."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from database.models.entities import RiskIndicator
from database.session import SessionLocal

log = logging.getLogger("envirolens.risk")

WEIGHTS = {
    "pm25": 0.25,
    "resp": 0.20,
    "prox": 0.15,
    "vuln": 0.15,
    "pov": 0.10,
    "access": 0.10,
    "incomplete": 0.05,
}


def _minmax(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    mn, mx = s.min(), s.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mn) / (mx - mn)


def _band(score: float) -> str:
    if score >= 0.75:
        return "very_high"
    if score >= 0.55:
        return "high"
    if score >= 0.35:
        return "moderate"
    return "low"


def fetch_components(session: Session) -> pd.DataFrame:
    sql = text(
        """
        WITH pm25 AS (
            SELECT c.id AS community_id, p.id AS period_id,
                   AVG(es.value) AS mean_pm25
            FROM environmental_samples es
            JOIN environmental_monitoring_sites s ON s.id = es.site_id
            JOIN communities c ON c.id = s.community_id
            JOIN reporting_periods p ON p.id = es.period_id
            WHERE es.pollutant = 'PM2.5' AND es.is_valid = true AND es.value IS NOT NULL
            GROUP BY c.id, p.id
        ),
        resp AS (
            SELECT c.id AS community_id, ho.period_id,
                   AVG(ho.value) AS mean_resp
            FROM health_observations ho
            JOIN health_facilities f ON f.id = ho.facility_id
            JOIN communities c ON c.id = f.community_id
            WHERE ho.indicator_code = 'RESP_ENC_RATE' AND ho.is_valid = true
            GROUP BY c.id, ho.period_id
        ),
        prox AS (
            SELECT c.id AS community_id,
                   MIN(ST_DistanceSphere(c.centroid, e.location)) AS dist_m
            FROM communities c
            CROSS JOIN exposure_sources e
            WHERE c.centroid IS NOT NULL AND e.location IS NOT NULL
            GROUP BY c.id
        ),
        pop AS (
            SELECT community_id, period_id,
                   total_population,
                   COALESCE(under5,0) + COALESCE(elderly_65plus,0) AS vulnerable
            FROM population_estimates
        ),
        pov AS (
            SELECT community_id, period_id, value AS poverty
            FROM socioeconomic_indicators
            WHERE indicator_code = 'POVERTY_INDEX'
        ),
        access AS (
            SELECT c.id AS community_id,
                   CASE WHEN BOOL_OR(f.has_lab_access) THEN 0.0 ELSE 1.0 END AS access_gap,
                   MIN(ST_DistanceSphere(c.centroid, f.location)) AS facility_dist_m
            FROM communities c
            LEFT JOIN health_facilities f ON f.community_id = c.id
            GROUP BY c.id
        )
        SELECT c.id AS community_id,
               p.id AS period_id,
               p.code AS period_code,
               pm25.mean_pm25,
               resp.mean_resp,
               prox.dist_m,
               CASE WHEN pop.total_population > 0
                    THEN pop.vulnerable::float / pop.total_population
                    ELSE NULL END AS vuln_share,
               pov.poverty,
               access.access_gap,
               access.facility_dist_m
        FROM communities c
        CROSS JOIN reporting_periods p
        LEFT JOIN pm25 ON pm25.community_id = c.id AND pm25.period_id = p.id
        LEFT JOIN resp ON resp.community_id = c.id AND resp.period_id = p.id
        LEFT JOIN prox ON prox.community_id = c.id
        LEFT JOIN pop ON pop.community_id = c.id AND pop.period_id = p.id
        LEFT JOIN pov ON pov.community_id = c.id AND pov.period_id = p.id
        LEFT JOIN access ON access.community_id = c.id
        """
    )
    return pd.read_sql(sql, session.bind)


def calculate_risk(session: Session | None = None) -> pd.DataFrame:
    own = session is None
    session = session or SessionLocal()
    try:
        df = fetch_components(session)
        if df.empty:
            log.warning("No component rows; skipping risk calculation")
            return df

        out_frames = []
        for period_id, g in df.groupby("period_id"):
            g = g.copy()
            # Invert distance: closer => higher risk
            prox_raw = 1.0 / (1.0 + g["dist_m"].fillna(g["dist_m"].median()) / 1000.0)
            access_raw = (
                0.7 * g["access_gap"].fillna(0.5)
                + 0.3 * _minmax(g["facility_dist_m"].fillna(g["facility_dist_m"].median()))
            )
            missing_frac = g[
                ["mean_pm25", "mean_resp", "dist_m", "vuln_share", "poverty"]
            ].isna().mean(axis=1)

            for col in ["mean_pm25", "mean_resp", "vuln_share", "poverty"]:
                med = g[col].median()
                g[col] = g[col].fillna(med if pd.notna(med) else 0)

            comps = {
                "pm25": _minmax(g["mean_pm25"]),
                "resp": _minmax(g["mean_resp"]),
                "prox": _minmax(prox_raw),
                "vuln": _minmax(g["vuln_share"]),
                "pov": _minmax(g["poverty"]),
                "access": _minmax(access_raw),
                "incomplete": missing_frac.clip(0, 1),
            }
            score = sum(WEIGHTS[k] * comps[k] for k in WEIGHTS)
            g["score"] = score.round(4)
            g["risk_band"] = g["score"].map(_band)
            g["pm25_component"] = comps["pm25"]
            g["respiratory_component"] = comps["resp"]
            g["proximity_component"] = comps["prox"]
            g["vulnerability_component"] = comps["vuln"]
            g["poverty_component"] = comps["pov"]
            g["access_component"] = comps["access"]
            g["completeness_component"] = comps["incomplete"]
            out_frames.append(g)

        result = pd.concat(out_frames, ignore_index=True)
        session.execute(delete(RiskIndicator))
        for _, row in result.iterrows():
            session.add(
                RiskIndicator(
                    community_id=int(row["community_id"]),
                    period_id=int(row["period_id"]),
                    index_code="AP_EHRI",
                    score=float(row["score"]),
                    risk_band=row["risk_band"],
                    pm25_component=float(row["pm25_component"]),
                    respiratory_component=float(row["respiratory_component"]),
                    proximity_component=float(row["proximity_component"]),
                    vulnerability_component=float(row["vulnerability_component"]),
                    poverty_component=float(row["poverty_component"]),
                    access_component=float(row["access_component"]),
                    completeness_component=float(row["completeness_component"]),
                    methodology_version="1.0",
                )
            )
        session.commit()
        log.info("Wrote %s risk indicator rows", len(result))
        return result
    finally:
        if own:
            session.close()


def main():
    logging.basicConfig(level=logging.INFO)
    df = calculate_risk()
    print(df[["community_id", "period_code", "score", "risk_band"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
