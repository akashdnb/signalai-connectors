from typing import Any

from pydantic import BaseModel, Field


class ConnectorRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)


class ConnectorResult(BaseModel):
    provider: str
    operation: str
    data: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class ConnectorError(BaseModel):
    code: str
    message: str
    retryable: bool
