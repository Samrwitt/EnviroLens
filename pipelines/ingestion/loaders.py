"""Ingest CSV, Excel, and JSON sources."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pipelines.paths import CSV_DIR, EXCEL_DIR, JSON_DIR


def read_csv(name: str) -> pd.DataFrame:
    path = CSV_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def read_excel(name: str, sheet: str | None = None) -> pd.DataFrame:
    path = EXCEL_DIR / name
    return pd.read_excel(path, sheet_name=sheet or 0)


def read_json(name: str) -> pd.DataFrame | dict:
    path = JSON_DIR / name
    if name.endswith(".geojson"):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if name.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        return data
    return pd.read_json(path)


def load_reference_frames() -> dict[str, pd.DataFrame]:
    return {
        "admin": read_csv("administrative_areas.csv"),
        "communities": read_csv("communities.csv"),
        "facilities": read_csv("health_facilities.csv"),
        "sites": read_csv("monitoring_sites.csv"),
        "sources": read_csv("exposure_sources.csv"),
        "labs": read_csv("laboratories.csv"),
        "periods": read_csv("reporting_periods.csv"),
    }


def load_core_datasets() -> dict[str, pd.DataFrame]:
    env_csv = read_csv("environmental_samples.csv")
    env_xlsx = read_excel("environmental_samples.xlsx")
    # Prefer CSV; assert Excel readable for stack coverage
    assert len(env_xlsx) > 0
    health = read_csv("health_observations.csv")
    health_json = read_json("health_observations.json")
    assert isinstance(health_json, pd.DataFrame) and len(health_json) > 0
    population = read_csv("population_estimates.csv")
    ses = read_csv("socioeconomic_indicators.csv")
    return {
        "environmental_samples": env_csv,
        "health_observations": health,
        "population_estimates": population,
        "socioeconomic_indicators": ses,
    }
