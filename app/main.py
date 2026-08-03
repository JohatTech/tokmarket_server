import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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


@app.middleware("http")
async def normalize_path_middleware(request: Request, call_next):
    path = request.scope.get("path", "")
    if "//" in path:
        request.scope["path"] = "/" + "/".join(filter(None, path.split("/")))
    return await call_next(request)


origins = settings.origins
is_wildcard = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_wildcard else origins,
    allow_origin_regex=None if is_wildcard else r"https://.*\.vercel\.app",
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# API routers (prefixed with /api/v1 and root fallback for direct requests)
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(providers.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")

app.include_router(catalog.router)
app.include_router(providers.router)
app.include_router(market.router)


@app.get("/health")
async def health():
    return {"status": "ok", "catalog_updated_at": catalog_service.updated_at}