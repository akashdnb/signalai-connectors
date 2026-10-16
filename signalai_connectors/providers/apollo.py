from typing import Any

from signalai_connectors.contracts import (
    CompanyCandidate,
    CompanyEvidence,
    CompanyGetInput,
    CompanySearchInput,
)
from signalai_connectors.http import ConnectorHttpClient


class ApolloCompanyProvider:
    name = "apollo"
    operations = frozenset({"company.search", "company.get"})

    def __init__(self, http: ConnectorHttpClient, api_key: str, base_url: str) -> None:
        self._http = http
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    async def search_companies(
        self, request: CompanySearchInput
    ) -> list[CompanyCandidate]:
        response = await self._http.request(
            "POST",
            f"{self._base_url}/mixed_companies/search",
            headers=self._headers(),
            json={"q_organization_name": request.query, "page": 1, "per_page": request.limit},
        )
        payload = response.json()
        return [self._candidate(item) for item in payload.get("organizations", [])]

    async def get_company(self, request: CompanyGetInput) -> CompanyEvidence:
        request.validate_identifier()
        params: dict[str, str] = {}
        if request.domain:
            params["domain"] = request.domain
        elif request.company_name:
            params["organization_name"] = request.company_name
        elif request.linkedin_url:
            params["linkedin_url"] = request.linkedin_url

        response = await self._http.request(
            "GET",
            f"{self._base_url}/organizations/enrich",
            headers=self._headers(),
            params=params,
        )
        payload = response.json().get("organization") or {}
        return self._evidence(payload)

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self._api_key, "accept": "application/json"}

    @staticmethod
    def _candidate(item: dict[str, Any]) -> CompanyCandidate:
        return CompanyCandidate(
            provider_record_id=item.get("id"),
            name=item.get("name"),
            domain=item.get("primary_domain") or item.get("domain"),
            linkedin_url=item.get("linkedin_url"),
            website_url=item.get("website_url"),
            industry=item.get("industry"),
            employee_count=item.get("estimated_num_employees"),
            location=item.get("city") or item.get("state") or item.get("country"),
        )

    @staticmethod
    def _evidence(item: dict[str, Any]) -> CompanyEvidence:
        return CompanyEvidence(
            provider_record_id=item.get("id"),
            name=item.get("name"),
            domain=item.get("primary_domain") or item.get("domain"),
            linkedin_url=item.get("linkedin_url"),
            website_url=item.get("website_url"),
            description=item.get("short_description") or item.get("long_description"),
            industry=item.get("industry"),
            employee_count=item.get("estimated_num_employees"),
            location=item.get("city") or item.get("state") or item.get("country"),
            source_url=item.get("website_url") or item.get("linkedin_url"),
            raw_metadata={"provider": "apollo"},
        )
