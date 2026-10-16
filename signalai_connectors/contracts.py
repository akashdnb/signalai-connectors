from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, Field


class CompanySearchInput(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=100)


class CompanyGetInput(BaseModel):
    domain: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=200)
    linkedin_url: str | None = Field(default=None, max_length=500)

    def validate_identifier(self) -> None:
        if not any((self.domain, self.company_name, self.linkedin_url)):
            raise ValueError("company_identifier_required")


class CompanyCandidate(BaseModel):
    provider_record_id: str | None = None
    name: str | None = None
    domain: str | None = None
    linkedin_url: str | None = None
    website_url: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    location: str | None = None


class CompanyEvidence(BaseModel):
    provider_record_id: str | None = None
    name: str | None = None
    domain: str | None = None
    linkedin_url: str | None = None
    website_url: str | None = None
    description: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    location: str | None = None
    source_url: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class CompanyResearchResult(BaseModel):
    provider: str
    operation: str
    companies: list[CompanyCandidate] = Field(default_factory=list)
    evidence: list[CompanyEvidence] = Field(default_factory=list)
    correlation_id: str
