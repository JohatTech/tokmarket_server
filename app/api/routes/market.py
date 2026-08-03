from fastapi import APIRouter
from app.models.catalog import ModelPrice
from app.services.catalog import catalog_service

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/top-five", response_model=list[ModelPrice])
async def top_five_models():
    """Top five models by the source marketplace's most-popular ranking."""
    ranked = [model for model in catalog_service.models if model.market_rank is not None]
    return sorted(ranked, key=lambda model: model.market_rank)[:5]