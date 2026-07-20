from fastapi import APIRouter
from app.routers.analytics import router as analytics_router
from app.routers.proxy import router as proxy_router

api_router = APIRouter()
api_router.include_router(proxy_router)
api_router.include_router(analytics_router)