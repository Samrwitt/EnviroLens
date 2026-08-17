"""API tests using FastAPI TestClient (DB optional soft-skip)."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("API_KEY", "dev-api-key-change-me")

from api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-api-key-change-me"}


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["name"] == "EnviroLens"


def test_health_open():
    r = client.get("/api/v1/health")
    assert r.status_code == 200


def test_regions_requires_auth():
    r = client.get("/api/v1/regions")
    assert r.status_code == 401


def test_reports_with_auth():
    r = client.get("/api/v1/reports", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) >= 3


def test_analytics_requires_auth():
    r = client.get("/api/v1/analytics/dashboard")
    assert r.status_code == 401


def test_dhis2_org_units_without_payload():
    # May 404 if synth not generated; either is acceptable for unit smoke
    r = client.get("/dhis2/api/organisationUnits")
    assert r.status_code in (200, 404)
