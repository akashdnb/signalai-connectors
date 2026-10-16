from collections.abc import Callable
from typing import Protocol

from signalai_connectors.models import ConnectorRequest, ConnectorResult


class ConnectorProvider(Protocol):
    name: str
    operations: frozenset[str]

    async def execute(self, request: ConnectorRequest) -> ConnectorResult: ...


ProviderFactory = Callable[[], ConnectorProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ConnectorProvider] = {}

    def register(self, provider: ConnectorProvider) -> None:
        if provider.name in self._providers:
            raise ValueError(f"provider_already_registered:{provider.name}")
        self._providers[provider.name] = provider

    def get(self, name: str) -> ConnectorProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"provider_not_found:{name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))
