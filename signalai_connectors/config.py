from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIGNALAI_", env_file=".env", extra="ignore")

    service_name: str = "signalai-connectors"
    service_version: str = "0.1.0"
    request_timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    max_response_bytes: int = Field(default=5_000_000, ge=1024, le=50_000_000)
    max_concurrency: int = Field(default=50, ge=1, le=500)
    apollo_base_url: str = "https://api.apollo.io/api/v1"
    apollo_api_key: str | None = None


settings = Settings()
