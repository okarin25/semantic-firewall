from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import AuditLogResponse, DashboardMetrics
from app.services.audit_service import audit_service
from app.services.cache_service import cache_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Dashboard"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_analytics(db: AsyncSession = Depends(get_db)):
    """Single aggregated DTO endpoint powering all React dashboard KPIs and charts."""
    cache_vector_count = cache_service.get_collection_size()
    return await audit_service.get_dashboard_metrics(db=db, cache_size=cache_vector_count)


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_recent_audit_logs(
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves real-time stream of intercepted request logs."""
    return await audit_service.get_recent_logs(db=db, limit=limit)