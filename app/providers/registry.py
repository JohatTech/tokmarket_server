from app.providers.base import ProviderAdapter
from app.providers.openrouter import OpenRouterAdapter


def provider_registry() -> list[ProviderAdapter]:
    # Add new direct-provider adapters here. They retain their own route/provenance.
    return [OpenRouterAdapter()]
