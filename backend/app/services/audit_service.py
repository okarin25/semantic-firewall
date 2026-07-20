from datetime import datetime, timedelta
from typing import List
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIAuditLog
from app.schemas import AuditLogResponse, DashboardMetrics, FirewallMetadata


class AuditService:
    """Handles audit database persistence and metrics aggregation."""

    async def log_transaction(
        self,
        db: AsyncSession,
        metadata: FirewallMetadata,
        prompt_text: str,
        completion_text: str,
        prompt_tokens: int,
        completion_tokens: int,
        client_ip: str = "127.0.0.1",
        user_id: str = None,
        session_id: str = None,
    ) -> APIAuditLog:
        """Persists transaction details to the relational database."""
        total_tokens = prompt_tokens + completion_tokens

        log_entry = APIAuditLog(
            id=metadata.request_id,
            request_id=metadata.request_id,
            timestamp=datetime.utcnow(),
            provider=metadata.provider,
            model_requested=metadata.model,
            prompt_hash=metadata.prompt_hash,
            prompt_text=prompt_text,
            prompt_tokens=prompt_tokens,
            cache_hit=metadata.cache_hit,
            similarity_score=metadata.similarity_score,
            cache_key=metadata.cache_key,
            completion_text=completion_text,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=metadata.latency_ms,
            cost_usd=metadata.estimated_cost_usd,
            cost_saved_usd=metadata.estimated_cost_saved_usd,
            client_ip=client_ip,
            user_id=user_id,
            session_id=session_id,
        )

        db.add(log_entry)
        await db.flush()
        logger.info(f"📝 Transaction audited successfully. Request ID: {metadata.request_id}")
        return log_entry

    async def get_dashboard_metrics(
        self, db: AsyncSession, cache_size: int = 0
    ) -> DashboardMetrics:
        """Aggregates system metrics for the single-endpoint React dashboard payload."""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)

        # Total Requests
        total_requests_query = await db.execute(select(func.count(APIAuditLog.id)))
        total_requests = total_requests_query.scalar() or 0

        # Requests Today
        requests_today_query = await db.execute(
            select(func.count(APIAuditLog.id)).where(APIAuditLog.timestamp >= today_start)
        )
        requests_today = requests_today_query.scalar() or 0

        # Hits & Misses
        cache_hits_query = await db.execute(
            select(func.count(APIAuditLog.id)).where(APIAuditLog.cache_hit == True)
        )
        cache_hits = cache_hits_query.scalar() or 0
        cache_misses = total_requests - cache_hits

        hit_rate = (cache_hits / total_requests * 100.0) if total_requests > 0 else 0.0

        # Financial Totals
        cost_spent_query = await db.execute(select(func.sum(APIAuditLog.cost_usd)))
        total_cost_spent = cost_spent_query.scalar() or 0.0

        cost_saved_query = await db.execute(select(func.sum(APIAuditLog.cost_saved_usd)))
        total_cost_saved = cost_saved_query.scalar() or 0.0

        # Average Latencies
        avg_latency_hit_query = await db.execute(
            select(func.avg(APIAuditLog.latency_ms)).where(APIAuditLog.cache_hit == True)
        )
        avg_latency_hit = avg_latency_hit_query.scalar() or 0.0

        avg_latency_miss_query = await db.execute(
            select(func.avg(APIAuditLog.latency_ms)).where(APIAuditLog.cache_hit == False)
        )
        avg_latency_miss = avg_latency_miss_query.scalar() or 0.0

        # Similarity Score Average
        avg_sim_query = await db.execute(
            select(func.avg(APIAuditLog.similarity_score)).where(APIAuditLog.cache_hit == True)
        )
        avg_sim_score = avg_sim_query.scalar() or 0.0

        # Total Tokens Saved via Cache Hits
        tokens_saved_query = await db.execute(
            select(func.sum(APIAuditLog.total_tokens)).where(APIAuditLog.cache_hit == True)
        )
        total_tokens_saved = tokens_saved_query.scalar() or 0

        return DashboardMetrics(
            total_requests=total_requests,
            requests_today=requests_today,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            hit_rate_percentage=round(hit_rate, 2),
            total_cost_spent_usd=round(total_cost_spent, 4),
            total_cost_saved_usd=round(total_cost_saved, 4),
            avg_latency_hit_ms=round(avg_latency_hit, 2),
            avg_latency_miss_ms=round(avg_latency_miss, 2),
            average_similarity_score=round(avg_sim_score, 4),
            total_tokens_saved=int(total_tokens_saved),
            cache_size_vectors=cache_size,
        )

    async def get_recent_logs(self, db: AsyncSession, limit: int = 50) -> List[AuditLogResponse]:
        """Retrieves recent audit transactions for the real-time request feed."""
        stmt = select(APIAuditLog).order_by(APIAuditLog.timestamp.desc()).limit(limit)
        result = await db.execute(stmt)
        logs = result.scalars().all()
        return [AuditLogResponse.model_validate(log) for log in logs]


# Singleton Service Instance
audit_service = AuditService()