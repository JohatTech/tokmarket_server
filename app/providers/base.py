from abc import ABC, abstractmethod
from app.models.catalog import ModelPrice, ProviderInfo


class ProviderAdapter(ABC):
    """A provider route. Keep first-party and marketplace prices separate."""
    info: ProviderInfo

    @abstractmethod
    async def fetch_models(self) -> list[ModelPrice]:
        """Fetch and normalize prices to USD per 1M tokens."""
