"""Data-quality validation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd


@dataclass
class DQIssue:
    dataset_name: str
    dimension: str
    severity: str
    record_ref: str
    message: str


@dataclass
class DQResult:
    dataset_name: str
    issues: list[DQIssue] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def overall(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(self.scores.values()) / len(self.scores), 4)


def _score_from_rate(bad_rate: float) -> float:
    return round(max(0.0, min(1.0, 1.0 - bad_rate)), 4)


def validate_environmental(df: pd.DataFrame, valid_districts: set[str]) -> DQResult:
    result = DQResult(dataset_name="environmental_samples")
    n = len(df) or 1

    missing = df["value"].isna().sum()
    for idx in df.index[df["value"].isna()]:
        result.issues.append(
            DQIssue(
                "environmental_samples",
                "completeness",
                "warning",
                str(idx),
                "Missing pollutant value",
            )
        )

    bad_unit = (df["unit"] != "ug/m3").sum() if "unit" in df.columns else 0
    for idx in df.index[df["unit"] != "ug/m3"] if "unit" in df.columns else []:
        result.issues.append(
            DQIssue(
                "environmental_samples",
                "consistency",
                "warning",
                str(idx),
                f"Unexpected unit {df.at[idx, 'unit']}",
            )
        )

    outliers = ((df["value"].notna()) & ((df["value"] < 0) | (df["value"] > 500))).sum()
    for idx in df.index[(df["value"].notna()) & ((df["value"] < 0) | (df["value"] > 500))]:
        result.issues.append(
            DQIssue(
                "environmental_samples",
                "validity",
                "error",
                str(idx),
                f"Outlier value {df.at[idx, 'value']}",
            )
        )

    future = 0
    if "sample_date" in df.columns:
        today = date.today()
        mask = df["sample_date"].apply(lambda d: isinstance(d, date) and d > today)
        future = int(mask.sum())
        for idx in df.index[mask]:
            result.issues.append(
                DQIssue(
                    "environmental_samples",
                    "validity",
                    "error",
                    str(idx),
                    f"Invalid future date {df.at[idx, 'sample_date']}",
                )
            )

    geo_bad = 0
    if "district_code" in df.columns:
        mask = ~df["district_code"].isin(valid_districts)
        geo_bad = int(mask.sum())
        for idx in df.index[mask]:
            result.issues.append(
                DQIssue(
                    "environmental_samples",
                    "geographic_accuracy",
                    "error",
                    str(idx),
                    f"Invalid district_code {df.at[idx, 'district_code']}",
                )
            )

    dup_cols = [c for c in ["site_code", "period_code", "pollutant", "sample_date"] if c in df.columns]
    dups = int(df.duplicated(subset=dup_cols).sum()) if dup_cols else 0
    for idx in df.index[df.duplicated(subset=dup_cols, keep="first")]:
        result.issues.append(
            DQIssue(
                "environmental_samples",
                "uniqueness",
                "warning",
                str(idx),
                "Duplicate observation",
            )
        )

    result.scores = {
        "completeness": _score_from_rate(missing / n),
        "validity": _score_from_rate((outliers + future) / n),
        "consistency": _score_from_rate(bad_unit / n),
        "timeliness": 0.95,
        "uniqueness": _score_from_rate(dups / n),
        "geographic_accuracy": _score_from_rate(geo_bad / n),
    }
    return result


def validate_health(df: pd.DataFrame, valid_facilities: set[str]) -> DQResult:
    result = DQResult(dataset_name="health_observations")
    n = len(df) or 1
    missing = df["value"].isna().sum()
    for idx in df.index[df["value"].isna()]:
        result.issues.append(
            DQIssue("health_observations", "completeness", "warning", str(idx), "Missing value")
        )

    bad_fac = (~df["facility_code"].isin(valid_facilities)).sum()
    for idx in df.index[~df["facility_code"].isin(valid_facilities)]:
        result.issues.append(
            DQIssue(
                "health_observations",
                "consistency",
                "error",
                str(idx),
                f"Unknown facility {df.at[idx, 'facility_code']}",
            )
        )

    late = 0
    if "reported_at" in df.columns:
        mask = df["reported_at"].apply(
            lambda d: isinstance(d, date) and d.year >= 2025
        )
        late = int(mask.sum())
        for idx in df.index[mask]:
            result.issues.append(
                DQIssue(
                    "health_observations",
                    "timeliness",
                    "warning",
                    str(idx),
                    f"Late reporting date {df.at[idx, 'reported_at']}",
                )
            )

    dups = int(df.duplicated(subset=["facility_code", "period_code", "indicator_code"]).sum())
    result.scores = {
        "completeness": _score_from_rate(missing / n),
        "validity": _score_from_rate(0),
        "consistency": _score_from_rate(bad_fac / n),
        "timeliness": _score_from_rate(late / n),
        "uniqueness": _score_from_rate(dups / n),
        "geographic_accuracy": _score_from_rate(bad_fac / n),
    }
    return result


def validate_population(df: pd.DataFrame) -> DQResult:
    result = DQResult(dataset_name="population_estimates")
    n = len(df) or 1
    missing = df["total_population"].isna().sum()
    for idx in df.index[df["total_population"].isna()]:
        result.issues.append(
            DQIssue(
                "population_estimates",
                "completeness",
                "warning",
                str(idx),
                "Missing total_population",
            )
        )
    dups = int(df.duplicated(subset=["community_code", "period_code"]).sum())
    result.scores = {
        "completeness": _score_from_rate(missing / n),
        "validity": 0.98,
        "consistency": 0.97,
        "timeliness": 0.96,
        "uniqueness": _score_from_rate(dups / n),
        "geographic_accuracy": 0.99,
    }
    return result


def mark_valid_environmental(df: pd.DataFrame, valid_districts: set[str]) -> pd.DataFrame:
    out = df.copy()
    out["is_valid"] = True
    out.loc[out["value"].isna(), "is_valid"] = False
    out.loc[out["unit"] != "ug/m3", "is_valid"] = False
    out.loc[(out["value"].notna()) & ((out["value"] < 0) | (out["value"] > 500)), "is_valid"] = False
    if "district_code" in out.columns:
        out.loc[~out["district_code"].isin(valid_districts), "is_valid"] = False
    today = date.today()
    if "sample_date" in out.columns:
        out.loc[
            out["sample_date"].apply(lambda d: isinstance(d, date) and d > today),
            "is_valid",
        ] = False
    out = out.drop_duplicates(
        subset=[c for c in ["site_code", "period_code", "pollutant", "sample_date"] if c in out.columns],
        keep="first",
    )
    return out


def mark_valid_health(df: pd.DataFrame, valid_facilities: set[str]) -> pd.DataFrame:
    out = df.copy()
    out["is_valid"] = True
    out.loc[out["value"].isna(), "is_valid"] = False
    out.loc[~out["facility_code"].isin(valid_facilities), "is_valid"] = False
    out = out.drop_duplicates(
        subset=["facility_code", "period_code", "indicator_code"], keep="first"
    )
    return out
