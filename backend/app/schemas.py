from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

# =====================================================================
# 1. Unified Message & Request Models (Provider Agnostic)
# =====================================================================

class ChatMessage(BaseModel):
    """Rich, flexible message model supporting multimodal content and tool calling."""
    role: str = Field(..., description="Message author role: 'system', 'user', 'assistant', 'tool'")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="String text or structured content blocks")
    name: Optional[str] = Field(None, description="Optional author identifier")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool execution payload from assistant")
    tool_call_id: Optional[str] = Field(None, description="Target tool call ID for tool role responses")


class ChatCompletionRequest(BaseModel):
    """Inbound client request compatible with OpenAI SDK but enriched for gateway routing."""
    provider: str = Field("openai", description="Target provider (openai, azure, anthropic, ollama)")
    model: str = Field("gpt-4o-mini", description="Target LLM model ID")
    messages: List[ChatMessage] = Field(..., description="Conversation message history")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None)
    stream: Optional[bool] = Field(False)
    
    # Session & Governance Tracking
    user_id: Optional[str] = Field(None, description="Client user identifier for rate limiting & tracking")
    session_id: Optional[str] = Field(None, description="Client conversation/session UUID")


# =====================================================================
# 2. Metadata & Gateway Diagnostics (Decoupled from Provider Specs)
# =====================================================================

class FirewallMetadata(BaseModel):
    """Enterprise gateway diagnostics injected into headers or administrative wrappers."""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    provider: str = Field(...)
    model: str = Field(...)
    cache_hit: bool = Field(False)
    similarity_score: Optional[float] = Field(None)
    cache_key: Optional[str] = Field(None)
    prompt_hash: str = Field(..., description="SHA-256 hash of normalized user prompt")
    latency_ms: float = Field(0.0, description="Total gateway turnaround time in milliseconds")
    estimated_cost_usd: float = Field(0.0, description="Actual spend for this call")
    estimated_cost_saved_usd: float = Field(0.0, description="Cost avoided via vector cache hit")


# =====================================================================
# 3. Standard OpenAI-Compliant Response Schemas
# =====================================================================

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Optional[float] = Field(0.0, description="Inferred usage cost")


class ChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChoiceMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    """Standard OpenAI-compliant API completion response."""
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: UsageInfo


class GatewayChatCompletionResponse(BaseModel):
    """Enriched wrapper option for clients using native firewall client libraries."""
    response: ChatCompletionResponse
    firewall_metadata: FirewallMetadata


# =====================================================================
# 4. Qdrant Vector Cache Payload Schema
# =====================================================================

class CacheEntry(BaseModel):
    """Full payload stored alongside embeddings inside Qdrant vector database."""
    cache_key: str = Field(..., description="Unique vector point key (e.g., prompt_hash)")
    prompt_hash: str = Field(..., description="SHA-256 hash of normalized input text")
    prompt_text: str = Field(..., description="Original raw prompt text")
    completion_text: str = Field(..., description="Cached LLM output text")
    provider: str = Field(...)
    model: str = Field(...)
    embedding_model: str = Field(...)
    similarity_threshold: float = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="TTL expiration date if configured")


# =====================================================================
# 5. Audit Logging & Observability DTOs
# =====================================================================

class AuditLogResponse(BaseModel):
    """Detailed transaction record for auditing tables and detailed UI deep-dives."""
    request_id: str
    timestamp: datetime
    provider: str
    model_requested: str
    prompt_hash: str
    prompt_text: str
    completion_text: str
    cache_hit: bool
    similarity_score: Optional[float]
    cache_key: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    cost_saved_usd: float
    client_ip: Optional[str]
    user_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DashboardMetrics(BaseModel):
    """Aggregated operational DTO for single-endpoint React dashboard polling."""
    total_requests: int
    requests_today: int
    cache_hits: int
    cache_misses: int
    hit_rate_percentage: float
    total_cost_spent_usd: float
    total_cost_saved_usd: float
    avg_latency_hit_ms: float
    avg_latency_miss_ms: float
    average_similarity_score: float
    total_tokens_saved: int
    cache_size_vectors: int


# =====================================================================
# 6. Standardized Gateway Error Schema
# =====================================================================

class ErrorDetails(BaseModel):
    message: str
    type: str = "gateway_error"
    code: str = "internal_firewall_error"


class GatewayErrorResponse(BaseModel):
    """Standardized error contract for all gateway exceptions."""
    error: ErrorDetails
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)