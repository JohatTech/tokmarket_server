import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import catalog, market, providers
from app.core.config import get_settings
from app.services.catalog import catalog_service


async def periodic_refresh(hours: int) -> None:
    while True:
        await asyncio.sleep(hours * 3600)
        await catalog_service.refresh()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await catalog_service.refresh()
    task = None if os.getenv("VERCEL") else asyncio.create_task(periodic_refresh(get_settings().refresh_hours))
    yield
    if task:
        task.cancel()


settings = get_settings()
app = FastAPI(title="Toktrade API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials="*" not in settings.origins,
)
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(providers.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "catalog_updated_at": catalog_service.updated_at}