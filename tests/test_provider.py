import pytest

from signalai_connectors.models import ConnectorRequest, ConnectorResult
from signalai_connectors.provider import ProviderRegistry


class FakeProvider:
    name = "fake"
    operations = frozenset({"search"})

    async def execute(self, request: ConnectorRequest) -> ConnectorResult:
        return ConnectorResult(provider=self.name, operation=request.operation)


def test_registry_registers_and_retrieves_provider():
    registry = ProviderRegistry()
    provider = FakeProvider()
    registry.register(provider)

    assert registry.names() == ("fake",)
    assert registry.get("fake") is provider


def test_registry_rejects_duplicate_provider():
    registry = ProviderRegistry()
    registry.register(FakeProvider())
    with pytest.raises(ValueError, match="provider_already_registered"):
        registry.register(FakeProvider())
