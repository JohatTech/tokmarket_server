from fastapi import APIRouter
from app.models.catalog import ProviderInfo
from app.services.catalog import catalog_service

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderInfo])
async def list_providers():
    if not catalog_service.models:
        await catalog_service.refresh()
    return [adapter.info for adapter in catalog_service.adapters]

