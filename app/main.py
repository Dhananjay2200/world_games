"""
Main FastAPI Application Entrypoint for WorldGames AI.
High-throughput, GZip-compressed, static SPA-ready platform built for 1M+ concurrent readers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import get_settings
from app.database.session import init_models
from app.api.routes import health, topics, articles, publishing, workflow, automation, auth, news
from app.utils.logging import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: initialize database schema and performance indexes on startup."""
    from app.services.scheduler_service import SchedulerService
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")
    init_models()
    SchedulerService.reconcile_stale_state()
    yield
    if SchedulerService.is_running():
        await SchedulerService.stop_automation()
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Automated Global Games & Sports Research, Profile Generation & Publishing Platform.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable High-Speed GZip Compression for payloads >= 500 bytes (75-80% bandwidth reduction at 1M scale)
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=5)

# Register API v1 Routers
API_V1_PREFIX = "/api/v1"
app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(topics.router, prefix=API_V1_PREFIX)
app.include_router(articles.router, prefix=API_V1_PREFIX)
app.include_router(publishing.router, prefix=API_V1_PREFIX)
app.include_router(workflow.router, prefix=API_V1_PREFIX)
app.include_router(automation.router, prefix=API_V1_PREFIX)
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(news.router, prefix=API_V1_PREFIX)


@app.get("/")
def root_endpoint():
    return {
        "platform": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "public_feed": "/api/v1/publish/feed",
        "cache_telemetry": "/api/v1/publish/cache/stats",
        "react_app": "/app",
    }


# Mount compiled React SPA if built for single-container production serving
dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
assets_dir = os.path.join(dist_dir, "assets")
if os.path.exists(dist_dir) and os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/app", tags=["Frontend"])
    @app.get("/admin", tags=["Frontend"])
    @app.get("/app/{full_path:path}", tags=["Frontend"])
    async def serve_react_app(full_path: str = ""):
        return FileResponse(os.path.join(dist_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
