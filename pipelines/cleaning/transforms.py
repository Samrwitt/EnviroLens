"""Cleaning and standardization transforms."""

from __future__ import annotations

import pandas as pd


UNIT_MAP = {
    "ug/m3": "ug/m3",
    "µg/m3": "ug/m3",
    "ug/m³": "ug/m3",
    "ppm": "ppm",  # flagged later as inconsistent for PM2.5/NO2 ambient
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [c.strip().lower().replace(" ", "_") for c in out.columns]
    return out


def parse_dates(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce").dt.date
    return out


def normalize_units(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "unit" in out.columns:
        out["unit"] = out["unit"].map(lambda u: UNIT_MAP.get(str(u).strip(), str(u).strip()))
    return out


def clean_environmental(df: pd.DataFrame) -> pd.DataFrame:
    out = standardize_columns(df)
    out = parse_dates(out, ["sample_date"])
    out = normalize_units(out)
    if "pollutant" in out.columns:
        out["pollutant"] = out["pollutant"].astype(str).str.upper().str.replace("PM2.5", "PM2.5")
        out["pollutant"] = out["pollutant"].replace({"PM25": "PM2.5", "NO₂": "NO2"})
    return out


def clean_health(df: pd.DataFrame) -> pd.DataFrame:
    out = standardize_columns(df)
    out = parse_dates(out, ["reported_at"])
    if "indicator_code" in out.columns:
        out["indicator_code"] = out["indicator_code"].astype(str).str.upper()
    return out


def clean_population(df: pd.DataFrame) -> pd.DataFrame:
    return standardize_columns(df)


def clean_ses(df: pd.DataFrame) -> pd.DataFrame:
    out = standardize_columns(df)
    if "indicator_code" in out.columns:
        out["indicator_code"] = out["indicator_code"].astype(str).str.upper()
    return out
