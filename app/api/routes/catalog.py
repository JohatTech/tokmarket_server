from fastapi import APIRouter, HTTPException, Query
from app.models.catalog import CatalogResponse, EstimateLine, EstimateRequest
from app.services.catalog import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=CatalogResponse)
async def get_catalog(q: str | None = None, provider: str | None = None, free_only: bool = Query(False)):
    return catalog_service.catalog(q, provider, free_only)


@router.post("/refresh", response_model=CatalogResponse)
async def refresh_catalog():
    return await catalog_service.refresh()


@router.post("/estimate", response_model=list[EstimateLine])
async def estimate_cost(payload: EstimateRequest):
    estimates = catalog_service.estimate(payload)
    if not estimates:
        raise HTTPException(404, "No requested models were found in the current catalog")
    return estimates
