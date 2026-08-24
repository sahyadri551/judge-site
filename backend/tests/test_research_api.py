"""Regression coverage for NyayaAI health, corpus, research, and analytics APIs."""
import os

import pytest
import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")


@pytest.fixture
def api():
    if not BASE_URL:
        pytest.skip("REACT_APP_BACKEND_URL is not configured")
    return requests.Session()


def test_health_and_analytics(api):
    health = api.get(f"{BASE_URL}/api/health", timeout=15)
    analytics = api.get(f"{BASE_URL}/api/analytics", timeout=15)
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
    assert analytics.status_code == 200
    assert analytics.json()["total_indexed_documents"] > 0


def test_statute_search_filter_and_detail(api):
    filtered = api.get(
        f"{BASE_URL}/api/statutes",
        params={"category": "BNSS", "search": "undertrial"},
        timeout=15,
    )
    detail = api.get(f"{BASE_URL}/api/statutes/bnss-479", timeout=15)
    missing = api.get(f"{BASE_URL}/api/statutes/missing", timeout=15)
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert detail.status_code == 200
    assert detail.json()["id"] == "bnss-479"
    assert missing.status_code == 404


def test_grounded_query_validation_and_scoping(api):
    answer = api.post(
        f"{BASE_URL}/api/research/query",
        json={"query": "What is bail?", "statute_filter": "BNSS"},
        timeout=15,
    )
    invalid = api.post(
        f"{BASE_URL}/api/research/query", json={"query": "x"}, timeout=15
    )
    assert answer.status_code == 200
    assert answer.json()["citations"]
    assert all("Nagarik" in citation["act"] for citation in answer.json()["citations"])
    assert invalid.status_code == 422