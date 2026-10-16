import httpx

from fastapi.testclient import TestClient

from signalai_connectors.app import app
from signalai_connectors.config import settings
from signalai_connectors.contracts import CompanyCandidate, CompanyEvidence
from signalai_connectors.providers.apollo import ApolloCompanyProvider


async def fake_search(self, payload):
    return [CompanyCandidate(provider_record_id="1", name=payload.query, domain="example.com")]


async def fake_get(self, payload):
    return CompanyEvidence(provider_record_id="1", name=payload.company_name or "Example")


def auth_headers() -> dict[str, str]:
    return {
        "x-signalai-service-token": "service-token",
        "x-signalai-tenant-id": "tenant-1",
    }


def test_company_search_requires_service_auth(monkeypatch):
    monkeypatch.setattr(settings, "service_token", "service-token")
    with TestClient(app) as client:
        response = client.post(
            "/v1/company/search",
            headers={"x-correlation-id": "corr-1"},
            json={"query": "SignalAI"},
        )
    assert response.status_code == 401


def test_company_search_requires_correlation_id(monkeypatch):
    monkeypatch.setattr(settings, "service_token", "service-token")
    monkeypatch.setattr(settings, "apollo_api_key", "test-key")
    monkeypatch.setattr(ApolloCompanyProvider, "search_companies", fake_search)
    with TestClient(app) as client:
        response = client.post(
            "/v1/company/search",
            headers=auth_headers(),
            json={"query": "SignalAI"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "x-correlation-id-required"


def test_company_search_returns_normalized_contract(monkeypatch):
    monkeypatch.setattr(settings, "service_token", "service-token")
    monkeypatch.setattr(settings, "apollo_api_key", "test-key")
    monkeypatch.setattr(ApolloCompanyProvider, "search_companies", fake_search)
    with TestClient(app) as client:
        response = client.post(
            "/v1/company/search",
            headers={**auth_headers(), "x-correlation-id": "corr-1"},
            json={"query": "SignalAI", "limit": 5},
        )
    assert response.status_code == 200
    assert response.json()["operation"] == "company.search"
    assert response.json()["correlation_id"] == "corr-1"
    assert response.json()["companies"][0]["domain"] == "example.com"


def test_company_get_requires_identifier(monkeypatch):
    monkeypatch.setattr(settings, "service_token", "service-token")
    monkeypatch.setattr(settings, "apollo_api_key", "test-key")
    with TestClient(app) as client:
        response = client.post(
            "/v1/company/get",
            headers={**auth_headers(), "x-correlation-id": "corr-2"},
            json={},
        )
    assert response.status_code == 422


def test_company_get_returns_evidence(monkeypatch):
    monkeypatch.setattr(settings, "service_token", "service-token")
    monkeypatch.setattr(settings, "apollo_api_key", "test-key")
    monkeypatch.setattr(ApolloCompanyProvider, "get_company", fake_get)
    with TestClient(app) as client:
        response = client.post(
            "/v1/company/get",
            headers={**auth_headers(), "x-correlation-id": "corr-3"},
            json={"company_name": "SignalAI"},
        )
    assert response.status_code == 200
    assert response.json()["company"]["name"] == "SignalAI"


def test_http_retryable_status():
    from signalai_connectors.http import _retryable

    response = httpx.Response(429, request=httpx.Request("GET", "https://example.com"))
    error = httpx.HTTPStatusError("rate limited", request=response.request, response=response)
    assert _retryable(error)
