from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request

from signalai_connectors.config import settings
from signalai_connectors.contracts import CompanyGetInput, CompanySearchInput
from signalai_connectors.http import ConnectorHttpClient
from signalai_connectors.providers.apollo import ApolloCompanyProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = ConnectorHttpClient()
    app.state.http = client
    app.state.apollo = (
        ApolloCompanyProvider(client, settings.apollo_api_key, settings.apollo_base_url)
        if settings.apollo_api_key
        else None
    )
    try:
        yield
    finally:
        await client.close()


app = FastAPI(title="SignalAI Connectors", version=settings.service_version, lifespan=lifespan)


def _authorize(service_token: str | None, tenant_id: str | None) -> None:
    if not settings.service_token:
        raise HTTPException(status_code=503, detail="service_auth_not_configured")
    if not service_token or service_token != settings.service_token:
        raise HTTPException(status_code=401, detail="invalid_service_credentials")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="x-signalai-tenant-id-required")


def _correlation_id(value: str | None) -> str:
    if not value:
        raise HTTPException(status_code=400, detail="x-correlation-id-required")
    return value


def _apollo(request: Request) -> ApolloCompanyProvider:
    provider = request.app.state.apollo
    if provider is None:
        raise HTTPException(status_code=503, detail="apollo_provider_not_configured")
    return provider


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready", "service": settings.service_name}


@app.post("/v1/company/search")
async def company_search(
    request: Request,
    payload: CompanySearchInput,
    x_correlation_id: str | None = Header(default=None),
    x_signalai_service_token: str | None = Header(default=None),
    x_signalai_tenant_id: str | None = Header(default=None),
) -> dict[str, object]:
    _authorize(x_signalai_service_token, x_signalai_tenant_id)
    correlation_id = _correlation_id(x_correlation_id)
    companies = await _apollo(request).search_companies(payload)
    return {
        "provider": "apollo",
        "operation": "company.search",
        "correlation_id": correlation_id,
        "companies": [company.model_dump() for company in companies],
    }


@app.post("/v1/company/get")
async def company_get(
    request: Request,
    payload: CompanyGetInput,
    x_correlation_id: str | None = Header(default=None),
    x_signalai_service_token: str | None = Header(default=None),
    x_signalai_tenant_id: str | None = Header(default=None),
) -> dict[str, object]:
    _authorize(x_signalai_service_token, x_signalai_tenant_id)
    correlation_id = _correlation_id(x_correlation_id)
    evidence = await _apollo(request).get_company(payload)
    return {
        "provider": "apollo",
        "operation": "company.get",
        "correlation_id": correlation_id,
        "company": evidence.model_dump(mode="json"),
    }
