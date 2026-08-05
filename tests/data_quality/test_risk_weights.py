"""Risk weight sanity checks."""

from analysis.risk_model.calculate import WEIGHTS, _band


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_bands():
    assert _band(0.1) == "low"
    assert _band(0.4) == "moderate"
    assert _band(0.6) == "high"
    assert _band(0.9) == "very_high"
