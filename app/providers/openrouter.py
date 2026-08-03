from datetime import UTC, datetime
import httpx
from app.models.catalog import ModelPrice, ProviderInfo
from app.providers.base import ProviderAdapter


class OpenRouterAdapter(ProviderAdapter):
    source_url = "https://openrouter.ai/api/v1/models?sort=most-popular"

    def __init__(self) -> None:
        self.info = ProviderInfo(id="openrouter", name="OpenRouter", status="ready", source_url=self.source_url)

    @staticmethod
    def _provider(model_id: str) -> str:
        prefix = model_id.split("/", 1)[0].replace("-", " ").replace("_", " ")
        return "xAI" if prefix.lower() == "x ai" else prefix.title()

    async def fetch_models(self) -> list[ModelPrice]:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Toktrade/1.0"}) as client:
            response = await client.get(self.source_url)
            response.raise_for_status()
        observed_at = datetime.now(UTC)
        models: list[ModelPrice] = []
        for rank, item in enumerate(response.json().get("data", []), start=1):
            pricing = item.get("pricing") or {}
            try:
                prompt = float(pricing.get("prompt", 0)) * 1_000_000
                completion = float(pricing.get("completion", 0)) * 1_000_000
            except (TypeError, ValueError):
                continue
            if prompt < 0 or completion < 0:
                continue
            model_id = item["id"]
            models.append(ModelPrice(
                id=f"openrouter:{model_id}", provider=self._provider(model_id), model=item.get("name", model_id),
                model_id=model_id, route="OpenRouter marketplace", market_rank=rank, input_per_million=prompt,
                output_per_million=completion, cache_read_per_million=float(pricing.get("input_cache_read", 0)) * 1_000_000,
                context_window=item.get("context_length"), modalities=(item.get("architecture") or {}).get("input_modalities", []),
                is_free=prompt == 0 and completion == 0, source_url=self.source_url, source_label="OpenRouter Models API", observed_at=observed_at,
            ))
        self.info = self.info.model_copy(update={"model_count": len(models), "last_refresh": observed_at, "status": "ready"})
        return models
