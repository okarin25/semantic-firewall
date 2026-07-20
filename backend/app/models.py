from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class APIAuditLog(Base):
    """Stores high-fidelity audit records for all intercepted API completion requests."""

    __tablename__ = "api_audit_logs"

    # Correlation Identifiers
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Matches request_id
    request_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Provider & Model Metadata
    provider: Mapped[str] = mapped_column(String(50), default="openai", nullable=False)
    model_requested: Mapped[str] = mapped_column(String(100), nullable=False)

    # Prompt Hashing & Payload
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cache Performance Metrics
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=True)
    cache_key: Mapped[str] = mapped_column(String(128), nullable=True)

    # Completion Payload & Usage
    completion_text: Mapped[str] = mapped_column(Text, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Latency & Financial Performance
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    cost_saved_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # User & Session Context
    client_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Performance Indexing for Analytics Queries
    __table_args__ = (
        Index("idx_audit_timestamp_provider", "timestamp", "provider"),
        Index("idx_audit_cache_performance", "cache_hit", "latency_ms"),
    )