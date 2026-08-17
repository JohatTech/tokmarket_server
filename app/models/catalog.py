from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ModelPrice(BaseModel):
    id: str
    provider: str
    model: str
    model_id: str
    route: str
    market_rank: int | None = Field(default=None, ge=1)
    input_per_million: float = Field(ge=0)
    output_per_million: float = Field(ge=0)
    cache_read_per_million: float | None = Field(default=None, ge=0)
    context_window: int | None = Field(default=None, ge=0)
    modalities: list[str] = []
    is_free: bool = False
    source_url: HttpUrl
    source_label: str
    observed_at: datetime
    benchmark_source: str | None = None
    benchmark_score: str | None = None


class ProviderInfo(BaseModel):
    id: str
    name: str
    status: str
    source_url: HttpUrl
    model_count: int = 0
    last_refresh: datetime | None = None


class CatalogResponse(BaseModel):
    updated_at: datetime | None
    models: list[ModelPrice]
    providers: list[ProviderInfo]


class EstimateRequest(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    calls_per_month: int = Field(ge=0)
    model_ids: list[str] = Field(min_length=1, max_length=10)


class EstimateLine(BaseModel):
    model_id: str
    monthly_cost: float