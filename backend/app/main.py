import httpx
# Bypass corporate SSL certificate verification for local development
old_init = httpx.Client.__init__
def new_init(self, *args, **kwargs):
    kwargs["verify"] = False
    old_init(self, *args, **kwargs)
httpx.Client.__init__ = new_init


from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import init_db
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} Gateway ({settings.ENVIRONMENT})")
    await init_db()
    yield
    logger.info("🛑 Shutting down gateway services...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise AI Gateway & Semantic Caching Firewall",
    lifespan=lifespan,
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker & Kubernetes probes."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }