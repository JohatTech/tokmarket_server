from asyncio import gather
from datetime import UTC, datetime
from app.models.catalog import CatalogResponse, EstimateLine, EstimateRequest, ModelPrice, ProviderInfo
from app.providers.registry import provider_registry


class CatalogService:
    def __init__(self) -> None:
        self.adapters = provider_registry()
        self.models: list[ModelPrice] = []
        self.updated_at: datetime | None = None

    async def refresh(self) -> CatalogResponse:
        results = await gather(*(adapter.fetch_models() for adapter in self.adapters), return_exceptions=True)
        refreshed: list[ModelPrice] = []
        for adapter, result in zip(self.adapters, results):
            if isinstance(result, Exception):
                adapter.info = adapter.info.model_copy(update={"status": "error"})
                continue
            refreshed.extend(result)
        if refreshed:
            self.models = refreshed
            self.updated_at = datetime.now(UTC)
        return self.catalog()

    def catalog(self, query: str | None = None, provider: str | None = None, free_only: bool = False) -> CatalogResponse:
        needle = (query or "").lower()
        models = [m for m in self.models if (not provider or m.provider == provider) and (not free_only or m.is_free) and (not needle or needle in f"{m.provider} {m.model} {m.model_id}".lower())]
        models.sort(key=lambda m: (m.market_rank or 10_000, m.input_per_million + m.output_per_million))
        return CatalogResponse(updated_at=self.updated_at, models=models, providers=[adapter.info for adapter in self.adapters])

    def estimate(self, payload: EstimateRequest) -> list[EstimateLine]:
        wanted = set(payload.model_ids)
        return [EstimateLine(model_id=m.id, monthly_cost=round((m.input_per_million * payload.input_tokens / 1_000_000 + m.output_per_million * payload.output_tokens / 1_000_000) * payload.calls_per_month, 6)) for m in self.models if m.id in wanted]


catalog_service = CatalogService()
