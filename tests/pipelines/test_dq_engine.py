"""Unit tests for data-quality validation rules."""

import pandas as pd

from pipelines.validation.dq_engine import (
    mark_valid_environmental,
    validate_environmental,
    validate_health,
    validate_population,
)


def test_environmental_detects_missing_and_outlier():
    df = pd.DataFrame(
        [
            {
                "site_code": "AQ-001",
                "district_code": "VR-N-D01",
                "period_code": "2024Q1",
                "pollutant": "PM2.5",
                "value": None,
                "unit": "ug/m3",
                "sample_date": None,
            },
            {
                "site_code": "AQ-001",
                "district_code": "VR-N-D01",
                "period_code": "2024Q1",
                "pollutant": "NO2",
                "value": 9999,
                "unit": "ppm",
                "sample_date": None,
            },
            {
                "site_code": "AQ-002",
                "district_code": "INVALID",
                "period_code": "2024Q1",
                "pollutant": "PM2.5",
                "value": 20,
                "unit": "ug/m3",
                "sample_date": None,
            },
        ]
    )
    res = validate_environmental(df, {"VR-N-D01"})
    assert res.scores["completeness"] < 1
    assert res.scores["validity"] < 1
    assert res.scores["geographic_accuracy"] < 1
    assert len(res.issues) >= 3


def test_mark_valid_filters():
    df = pd.DataFrame(
        [
            {
                "site_code": "AQ-001",
                "district_code": "VR-N-D01",
                "period_code": "2024Q1",
                "pollutant": "PM2.5",
                "value": 25,
                "unit": "ug/m3",
                "sample_date": None,
            },
            {
                "site_code": "AQ-001",
                "district_code": "VR-N-D01",
                "period_code": "2024Q1",
                "pollutant": "PM2.5",
                "value": 25,
                "unit": "ug/m3",
                "sample_date": None,
            },
        ]
    )
    out = mark_valid_environmental(df, {"VR-N-D01"})
    assert len(out) == 1
    assert out.iloc[0]["is_valid"] is True


def test_health_unknown_facility():
    df = pd.DataFrame(
        [
            {
                "facility_code": "HF-UNKNOWN",
                "period_code": "2024Q1",
                "indicator_code": "RESP_ENC_RATE",
                "value": 12.0,
                "reported_at": None,
            }
        ]
    )
    res = validate_health(df, {"HF-001"})
    assert res.scores["consistency"] < 1


def test_population_missing():
    df = pd.DataFrame(
        [{"community_code": "C1", "period_code": "2024Q1", "total_population": None}]
    )
    res = validate_population(df)
    assert res.scores["completeness"] < 1
