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


def test_query_returns_hindi_and_history_persists(api):
    query = "TEST_hindi undertrial bail BNSS Section 479"
    response = api.post(f"{BASE_URL}/api/research/query", json={"query": query}, timeout=15)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["hindi_answer"], str)
    assert "कानूनी" in payload["hindi_answer"]
    history = api.get(f"{BASE_URL}/api/research/history", timeout=15)
    assert history.status_code == 200
    assert any(item["query"] == query for item in history.json()["queries"])


def test_saved_brief_create_and_get(api):
    query = "TEST_saved brief Article 21"
    response = api.post(
        f"{BASE_URL}/api/research/saved",
        json={
            "query": query,
            "answer": "TEST answer",
            "confidence_score": 92.4,
            "citations": [{"id": "const-art21", "title": "Article 21"}],
            "hindi_answer": "TEST हिंदी उत्तर",
        },
        timeout=15,
    )
    assert response.status_code == 200
    saved = response.json()
    assert saved["query"] == query
    assert saved["id"].startswith("brief-")
    listing = api.get(f"{BASE_URL}/api/research/saved", timeout=15)
    assert listing.status_code == 200
    assert any(item["id"] == saved["id"] for item in listing.json()["briefs"])


def test_sources_expose_curated_official_metadata(api):
    for source_id in ("const-art21", "case-kesavananda"):
        response = api.get(f"{BASE_URL}/api/statutes/{source_id}", timeout=15)
        assert response.status_code == 200
        source = response.json()
        assert source["official_source"]
        assert source["official_url"].startswith("https://")