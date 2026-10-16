from collections.abc import Mapping

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from signalai_connectors.config import settings


class ConnectorHttpClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout_seconds),
            limits=httpx.Limits(max_connections=settings.max_concurrency),
            follow_redirects=True,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json: object | None = None,
    ) -> httpx.Response:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential_jitter(initial=0.5, max=8),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
            reraise=True,
        ):
            with attempt:
                response = await self._client.request(
                    method, url, headers=headers, params=params, json=json
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    response.raise_for_status()
                response.raise_for_status()
                if len(response.content) > settings.max_response_bytes:
                    raise ValueError("connector_response_too_large")
                return response
        raise RuntimeError("unreachable")
