from datetime import UTC, datetime
import httpx
from app.models.catalog import ModelPrice, ProviderInfo
from app.providers.base import ProviderAdapter
from app.services.benchmarks import map_benchmark_ranks


class OpenRouterAdapter(ProviderAdapter):
    source_url = "https://openrouter.ai/api/v1/models"

    def __init__(self) -> None:
        self.info = ProviderInfo(id="openrouter", name="OpenRouter", status="ready", source_url=self.source_url)

    @staticmethod
    def _provider(model_id: str) -> str:
        prefix = model_id.split("/", 1)[0].replace("-", " ").replace("_", " ").lower()
        if prefix in ("openai", "open ai"):
            return "OpenAI"
        if prefix == "anthropic":
            return "Anthropic"
        if prefix == "google":
            return "Google"
        if prefix in ("meta", "meta llama", "meta-llama"):
            return "Meta"
        if prefix in ("deepseek", "deep seek"):
            return "DeepSeek"
        if prefix in ("xai", "x ai", "x-ai"):
            return "xAI"
        if prefix in ("mistralai", "mistral ai", "mistral"):
            return "Mistral"
        if prefix == "cohere":
            return "Cohere"
        if prefix in ("amazon", "aws", "bedrock"):
            return "Amazon"
        return prefix.title()

    async def fetch_models(self) -> list[ModelPrice]:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Toktrade/1.0"}) as client:
            response = await client.get(self.source_url)
            response.raise_for_status()
        observed_at = datetime.now(UTC)
        raw_items = response.json().get("data", [])
        benchmark_map = map_benchmark_ranks(raw_items)

        models: list[ModelPrice] = []
        for item in raw_items:
            pricing = item.get("pricing") or {}
            try:
                prompt = float(pricing.get("prompt", 0)) * 1_000_000
                completion = float(pricing.get("completion", 0)) * 1_000_000
            except (TypeError, ValueError):
                continue
            if prompt < 0 or completion < 0:
                continue

            model_id = item["id"]
            bench_match = benchmark_map.get(model_id)

            if bench_match:
                provider_name = bench_match.provider
                display_name = bench_match.name
                market_rank = bench_match.rank
                benchmark_source = bench_match.benchmark_source
                benchmark_score = bench_match.benchmark_score
            else:
                provider_name = self._provider(model_id)
                display_name = item.get("name", model_id)
                market_rank = None
                benchmark_source = None
                benchmark_score = None

            models.append(ModelPrice(
                id=f"openrouter:{model_id}",
                provider=provider_name,
                model=display_name,
                model_id=model_id,
                route="OpenRouter marketplace",
                market_rank=market_rank,
                input_per_million=prompt,
                output_per_million=completion,
                cache_read_per_million=float(pricing.get("input_cache_read", 0)) * 1_000_000 if pricing.get("input_cache_read") is not None else None,
                context_window=item.get("context_length"),
                modalities=(item.get("architecture") or {}).get("input_modalities", []),
                is_free=prompt == 0 and completion == 0,
                source_url=self.source_url,
                source_label="OpenRouter Models API",
                observed_at=observed_at,
                benchmark_source=benchmark_source,
                benchmark_score=benchmark_score,
            ))

        self.info = self.info.model_copy(update={"model_count": len(models), "last_refresh": observed_at, "status": "ready"})
        return models
