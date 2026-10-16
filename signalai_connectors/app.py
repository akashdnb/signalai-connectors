from contextlib import asynccontextmanager

from fastapi import FastAPI

from signalai_connectors.config import settings
from signalai_connectors.http import ConnectorHttpClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = ConnectorHttpClient()
    app.state.http = client
    try:
        yield
    finally:
        await client.close()


app = FastAPI(title="SignalAI Connectors", version=settings.service_version, lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready", "service": settings.service_name}
