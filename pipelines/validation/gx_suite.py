"""Lightweight Great Expectations-style suite registration for stack coverage."""

from __future__ import annotations

import pandas as pd


def expect_column_values_not_null(df: pd.DataFrame, column: str) -> dict:
    nulls = int(df[column].isna().sum())
    return {
        "expectation": "expect_column_values_to_not_be_null",
        "column": column,
        "success": nulls == 0,
        "unexpected_count": nulls,
    }


def expect_column_values_in_set(df: pd.DataFrame, column: str, value_set: set) -> dict:
    bad = ~df[column].isin(value_set)
    return {
        "expectation": "expect_column_values_to_be_in_set",
        "column": column,
        "success": int(bad.sum()) == 0,
        "unexpected_count": int(bad.sum()),
    }


def run_environmental_suite(df: pd.DataFrame) -> list[dict]:
    return [
        expect_column_values_not_null(df, "site_code"),
        expect_column_values_in_set(df, "pollutant", {"PM2.5", "NO2", "pm2.5", "no2", "PM2.5"}),
    ]
