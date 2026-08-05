"""Generate synthetic Verdania geography and air-pollution datasets.

Produces CSVs, Excel, JSON, and GeoJSON under synthetic_data/ with intentional
data-quality defects for the DQ engine to detect.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "synthetic_data"
BOUNDARIES = ROOT / "geospatial" / "boundaries"

RNG = random.Random(42)

REGIONS = [
    ("VR-N", "Northern Verdania", 1.5, 32.0),
    ("VR-C", "Central Verdania", 0.0, 32.5),
    ("VR-S", "Southern Verdania", -1.5, 33.0),
]

DISTRICTS_PER_REGION = 4
COMMUNITIES_PER_DISTRICT = 3  # 3*4*3 = 36 communities (~40)
PERIODS = [
    ("2024Q1", "2024 Q1", "2024-01-01", "2024-03-31"),
    ("2024Q2", "2024 Q2", "2024-04-01", "2024-06-30"),
    ("2024Q3", "2024 Q3", "2024-07-01", "2024-09-30"),
    ("2024Q4", "2024 Q4", "2024-10-01", "2024-12-31"),
]


def _box(lon: float, lat: float, w: float = 0.35, h: float = 0.3) -> list:
    return [
        [
            [lon - w / 2, lat - h / 2],
            [lon + w / 2, lat - h / 2],
            [lon + w / 2, lat + h / 2],
            [lon - w / 2, lat + h / 2],
            [lon - w / 2, lat - h / 2],
        ]
    ]


def build_geography() -> dict:
    features = []
    admin_rows = []
    community_rows = []
    facility_rows = []
    site_rows = []
    source_rows = []
    lab_rows = []

    # Country
    admin_rows.append(
        {
            "code": "VR",
            "name": "Verdania",
            "level": "country",
            "parent_code": None,
            "lon": 32.5,
            "lat": 0.0,
        }
    )
    features.append(
        {
            "type": "Feature",
            "properties": {"code": "VR", "name": "Verdania", "level": "country"},
            "geometry": {"type": "MultiPolygon", "coordinates": [_box(32.5, 0.0, 4.5, 5.0)]},
        }
    )

    district_idx = 0
    community_idx = 0
    for r_i, (r_code, r_name, r_lat, r_lon) in enumerate(REGIONS):
        admin_rows.append(
            {
                "code": r_code,
                "name": r_name,
                "level": "region",
                "parent_code": "VR",
                "lon": r_lon,
                "lat": r_lat,
            }
        )
        features.append(
            {
                "type": "Feature",
                "properties": {"code": r_code, "name": r_name, "level": "region"},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [_box(r_lon, r_lat, 1.4, 1.2)],
                },
            }
        )

        for d in range(DISTRICTS_PER_REGION):
            district_idx += 1
            d_code = f"{r_code}-D{d + 1:02d}"
            d_name = f"{r_name.split()[0]} District {d + 1}"
            d_lon = r_lon + (d % 2) * 0.55 - 0.25
            d_lat = r_lat + (d // 2) * 0.45 - 0.2
            admin_rows.append(
                {
                    "code": d_code,
                    "name": d_name,
                    "level": "district",
                    "parent_code": r_code,
                    "lon": d_lon,
                    "lat": d_lat,
                }
            )
            features.append(
                {
                    "type": "Feature",
                    "properties": {"code": d_code, "name": d_name, "level": "district"},
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [_box(d_lon, d_lat, 0.5, 0.4)],
                    },
                }
            )

            # One lab per district
            lab_rows.append(
                {
                    "code": f"LAB-{district_idx:03d}",
                    "name": f"{d_name} Public Laboratory",
                    "district_code": d_code,
                    "lon": d_lon + 0.02,
                    "lat": d_lat + 0.02,
                    "can_process_respiratory": True,
                }
            )

            for c in range(COMMUNITIES_PER_DISTRICT):
                community_idx += 1
                c_code = f"{d_code}-C{c + 1:02d}"
                c_name = f"Community {community_idx:02d}"
                c_lon = d_lon + (c - 1) * 0.12
                c_lat = d_lat + (c % 2) * 0.08 - 0.04
                community_rows.append(
                    {
                        "code": c_code,
                        "name": c_name,
                        "district_code": d_code,
                        "region_code": r_code,
                        "lon": c_lon,
                        "lat": c_lat,
                    }
                )
                features.append(
                    {
                        "type": "Feature",
                        "properties": {
                            "code": c_code,
                            "name": c_name,
                            "level": "community",
                            "district_code": d_code,
                        },
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [_box(c_lon, c_lat, 0.1, 0.08)],
                        },
                    }
                )

                # Facility
                facility_rows.append(
                    {
                        "code": f"HF-{community_idx:03d}",
                        "name": f"{c_name} Health Centre",
                        "facility_type": RNG.choice(["clinic", "health_centre", "hospital"]),
                        "community_code": c_code,
                        "district_code": d_code,
                        "lon": c_lon + 0.01,
                        "lat": c_lat + 0.01,
                        "has_lab_access": RNG.random() > 0.35,
                    }
                )

                # Monitoring site (most communities)
                if RNG.random() > 0.15:
                    site_rows.append(
                        {
                            "code": f"AQ-{community_idx:03d}",
                            "name": f"{c_name} Air Quality Station",
                            "community_code": c_code,
                            "district_code": d_code,
                            "lon": c_lon - 0.01,
                            "lat": c_lat - 0.01,
                            "site_type": "ambient_air",
                        }
                    )

                # Industrial exposure sources (sparse)
                if RNG.random() > 0.72:
                    source_rows.append(
                        {
                            "code": f"IND-{community_idx:03d}",
                            "name": f"{c_name} Industrial Facility",
                            "source_type": RNG.choice(["industrial", "power_plant", "quarry"]),
                            "pollutant": RNG.choice(["PM2.5", "NO2"]),
                            "district_code": d_code,
                            "lon": c_lon + RNG.uniform(-0.05, 0.05),
                            "lat": c_lat + RNG.uniform(-0.05, 0.05),
                            "estimated_emission_index": round(RNG.uniform(0.3, 1.0), 2),
                        }
                    )

    return {
        "features": features,
        "admin": admin_rows,
        "communities": community_rows,
        "facilities": facility_rows,
        "sites": site_rows,
        "sources": source_rows,
        "labs": lab_rows,
    }


def generate_environmental_samples(sites: list[dict]) -> pd.DataFrame:
    rows = []
    for period_code, _, start, end in PERIODS:
        for site in sites:
            base_pm = 18 + abs(hash(site["code"]) % 40) + (5 if "N" in site["district_code"] else 0)
            base_no2 = 12 + abs(hash(site["code"][::-1]) % 25)
            for pollutant, base, unit in [("PM2.5", base_pm, "ug/m3"), ("NO2", base_no2, "ug/m3")]:
                value = round(base + RNG.gauss(0, 4), 1)
                sample_date = start if RNG.random() > 0.1 else end
                row = {
                    "site_code": site["code"],
                    "community_code": site["community_code"],
                    "district_code": site["district_code"],
                    "period_code": period_code,
                    "pollutant": pollutant,
                    "value": value,
                    "unit": unit,
                    "sample_date": sample_date,
                }
                # Intentional defects
                if RNG.random() < 0.04:
                    row["value"] = None  # missing
                if RNG.random() < 0.02:
                    row["unit"] = "ppm"  # inconsistent unit
                if RNG.random() < 0.02:
                    row["value"] = 9999  # outlier
                if RNG.random() < 0.02:
                    row["district_code"] = "INVALID"  # bad geo
                if RNG.random() < 0.02:
                    row["sample_date"] = "2099-01-01"  # invalid future date
                rows.append(row)
                # Duplicate
                if RNG.random() < 0.015:
                    rows.append(dict(row))
    return pd.DataFrame(rows)


def generate_health_observations(facilities: list[dict]) -> pd.DataFrame:
    rows = []
    for period_code, _, start, end in PERIODS:
        for fac in facilities:
            pop = 800 + abs(hash(fac["code"]) % 4000)
            cases = max(0, int(pop * RNG.uniform(0.008, 0.045)))
            # Late reporting for some
            reported = end if RNG.random() > 0.12 else "2025-02-15"
            row = {
                "facility_code": fac["code"],
                "community_code": fac["community_code"],
                "district_code": fac["district_code"],
                "period_code": period_code,
                "indicator_code": "RESP_ENC_RATE",
                "indicator_name": "Respiratory encounter rate per 1,000",
                "value": round(cases / pop * 1000, 2),
                "population_at_risk": pop,
                "age_group": "all",
                "reported_at": reported,
                "cases": cases,
            }
            if RNG.random() < 0.03:
                row["value"] = None
            if RNG.random() < 0.02:
                row["facility_code"] = "HF-UNKNOWN"
            if RNG.random() < 0.02:
                row["age_group"] = "age_-5"  # impossible age label defect for DQ narrative
            rows.append(row)
            # Incomplete facility submission (skip some periods intentionally handled above)
    # Drop ~5% of facility-period combos already via random; add explicit missing set
    return pd.DataFrame(rows)


def generate_population_ses(communities: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    pop_rows = []
    ses_rows = []
    for period_code, *_ in PERIODS:
        for com in communities:
            total = 1200 + abs(hash(com["code"] + period_code) % 8000)
            under5 = int(total * RNG.uniform(0.10, 0.18))
            elderly = int(total * RNG.uniform(0.04, 0.12))
            female = int(total * RNG.uniform(0.48, 0.53))
            pop_rows.append(
                {
                    "community_code": com["code"],
                    "district_code": com["district_code"],
                    "period_code": period_code,
                    "total_population": total if RNG.random() > 0.03 else None,
                    "under5": under5,
                    "elderly_65plus": elderly,
                    "female": female,
                    "male": total - female if total else None,
                }
            )
            poverty = round(RNG.uniform(0.15, 0.72), 3)
            if RNG.random() < 0.03:
                poverty = None
            ses_rows.append(
                {
                    "community_code": com["code"],
                    "district_code": com["district_code"],
                    "period_code": period_code,
                    "indicator_code": "POVERTY_INDEX",
                    "indicator_name": "Multidimensional poverty index",
                    "value": poverty,
                    "unit": "index_0_1",
                }
            )
            ses_rows.append(
                {
                    "community_code": com["code"],
                    "district_code": com["district_code"],
                    "period_code": period_code,
                    "indicator_code": "URBANIZATION",
                    "indicator_name": "Urbanization share",
                    "value": round(RNG.uniform(0.1, 0.9), 3),
                    "unit": "proportion",
                }
            )
    return pd.DataFrame(pop_rows), pd.DataFrame(ses_rows)


def generate_periods() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "code": c,
                "label": l,
                "start_date": s,
                "end_date": e,
                "period_type": "quarter",
            }
            for c, l, s, e in PERIODS
        ]
    )


def generate_dhis2_payload(facilities: list[dict], health_df: pd.DataFrame) -> dict:
    org_units = [
        {
            "id": f"ou{i:04d}",
            "code": f["code"],
            "name": f["name"],
            "parent": f["district_code"],
        }
        for i, f in enumerate(facilities, start=1)
    ]
    data_values = []
    sample = health_df.dropna(subset=["value"]).head(50)
    for _, row in sample.iterrows():
        data_values.append(
            {
                "dataElement": "RESP_ENC_RATE",
                "period": row["period_code"].replace("Q", "Q"),
                "orgUnit": row["facility_code"],
                "value": str(row["value"]),
            }
        )
    return {
        "organisationUnits": org_units,
        "dataValueSets": {"dataValues": data_values},
    }


def write_outputs(geo: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    BOUNDARIES.mkdir(parents=True, exist_ok=True)
    (OUT / "csv").mkdir(exist_ok=True)
    (OUT / "excel").mkdir(exist_ok=True)
    (OUT / "json").mkdir(exist_ok=True)

    fc = {"type": "FeatureCollection", "features": geo["features"]}
    with open(BOUNDARIES / "verdania_admin.geojson", "w", encoding="utf-8") as f:
        json.dump(fc, f)
    with open(OUT / "json" / "verdania_admin.geojson", "w", encoding="utf-8") as f:
        json.dump(fc, f)

    pd.DataFrame(geo["admin"]).to_csv(OUT / "csv" / "administrative_areas.csv", index=False)
    pd.DataFrame(geo["communities"]).to_csv(OUT / "csv" / "communities.csv", index=False)
    pd.DataFrame(geo["facilities"]).to_csv(OUT / "csv" / "health_facilities.csv", index=False)
    pd.DataFrame(geo["sites"]).to_csv(OUT / "csv" / "monitoring_sites.csv", index=False)
    pd.DataFrame(geo["sources"]).to_csv(OUT / "csv" / "exposure_sources.csv", index=False)
    pd.DataFrame(geo["labs"]).to_csv(OUT / "csv" / "laboratories.csv", index=False)
    generate_periods().to_csv(OUT / "csv" / "reporting_periods.csv", index=False)

    env_df = generate_environmental_samples(geo["sites"])
    health_df = generate_health_observations(geo["facilities"])
    pop_df, ses_df = generate_population_ses(geo["communities"])

    env_df.to_csv(OUT / "csv" / "environmental_samples.csv", index=False)
    health_df.to_csv(OUT / "csv" / "health_observations.csv", index=False)
    pop_df.to_csv(OUT / "csv" / "population_estimates.csv", index=False)
    ses_df.to_csv(OUT / "csv" / "socioeconomic_indicators.csv", index=False)

    # Excel workbook for one source
    with pd.ExcelWriter(OUT / "excel" / "environmental_samples.xlsx") as writer:
        env_df.to_excel(writer, sheet_name="samples", index=False)

    # JSON export for health
    health_df.to_json(OUT / "json" / "health_observations.json", orient="records", date_format="iso")

    dhis2 = generate_dhis2_payload(geo["facilities"], health_df)
    with open(OUT / "json" / "dhis2_mock_payload.json", "w", encoding="utf-8") as f:
        json.dump(dhis2, f, indent=2)

    # Point GeoJSONs
    def points_fc(rows, code_key="code"):
        feats = []
        for r in rows:
            feats.append(
                {
                    "type": "Feature",
                    "properties": {k: v for k, v in r.items() if k not in ("lon", "lat")},
                    "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
                }
            )
        return {"type": "FeatureCollection", "features": feats}

    with open(BOUNDARIES / "facilities.geojson", "w", encoding="utf-8") as f:
        json.dump(points_fc(geo["facilities"]), f)
    with open(BOUNDARIES / "monitoring_sites.geojson", "w", encoding="utf-8") as f:
        json.dump(points_fc(geo["sites"]), f)
    with open(BOUNDARIES / "exposure_sources.geojson", "w", encoding="utf-8") as f:
        json.dump(points_fc(geo["sources"]), f)

    print(f"Wrote synthetic data to {OUT}")
    print(
        f"Communities={len(geo['communities'])}, sites={len(geo['sites'])}, "
        f"env_rows={len(env_df)}, health_rows={len(health_df)}"
    )


def main() -> None:
    geo = build_geography()
    write_outputs(geo)


if __name__ == "__main__":
    main()
