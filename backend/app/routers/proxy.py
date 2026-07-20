import time
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, Request, Response, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChoiceMessage,
    FirewallMetadata,
    UsageInfo,
)
from app.services.audit_service import audit_service
from app.services.cache_service import cache_service
from app.services.llm_service import llm_service

router = APIRouter(tags=["Proxy Engine"])


def _extract_prompt_text(request: ChatCompletionRequest) -> str:
    """Extracts and normalizes user prompt text from conversation history."""
    user_messages = [
        msg.content if isinstance(msg.content, str) else str(msg.content)
        for msg in request.messages
        if msg.role == "user"
    ]
    if user_messages:
        return user_messages[-1].strip()
    return str(request.messages[-1].content).strip()


@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
)
async def intercept_chat_completions(
    request_payload: ChatCompletionRequest,
    request: Request,
    response: Response,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Primary interceptor proxy for LLM completion requests."""
    start_time = time.perf_counter()
    request_id = str(uuid4())
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Extract API Key from Header
    api_key = authorization.replace("Bearer ", "") if authorization else ""

    # 1. Normalize Prompt & Generate Hash
    prompt_text = _extract_prompt_text(request_payload)
    prompt_hash = cache_service.generate_prompt_hash(prompt_text)

    logger.info(f"⚡ Intercepted request [{request_id}] | Prompt Hash: {prompt_hash[:8]}...")

    # 2. Check Vector Cache (Qdrant)
    cached_match = await cache_service.search_cache(prompt_text)

    if cached_match:
        # --- CACHE HIT PATH ---
        cache_entry, similarity_score = cached_match
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Estimate Token Counts & Cost Savings
        prompt_tokens = llm_service.count_tokens(prompt_text, request_payload.model)
        completion_tokens = llm_service.count_tokens(
            cache_entry.completion_text, request_payload.model
        )
        saved_cost_usd = llm_service.calculate_cost(prompt_tokens, completion_tokens)

        # Assemble Metadata DTO
        metadata = FirewallMetadata(
            request_id=request_id,
            provider=request_payload.provider,
            model=request_payload.model,
            cache_hit=True,
            similarity_score=similarity_score,
            cache_key=cache_entry.cache_key,
            prompt_hash=prompt_hash,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=0.0,
            estimated_cost_saved_usd=saved_cost_usd,
        )

        # Audit Transaction Async
        await audit_service.log_transaction(
            db=db,
            metadata=metadata,
            prompt_text=prompt_text,
            completion_text=cache_entry.completion_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            client_ip=client_ip,
            user_id=request_payload.user_id,
            session_id=request_payload.session_id,
        )

        # Inject Diagnostic Headers
        response.headers["X-Firewall-Cache-Hit"] = "true"
        response.headers["X-Similarity-Score"] = str(round(similarity_score, 4))
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Latency-MS"] = str(round(elapsed_ms, 2))

        return ChatCompletionResponse(
            id=f"chatcmpl-cache-{request_id[:8]}",
            model=request_payload.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChoiceMessage(role="assistant", content=cache_entry.completion_text),
                    finish_reason="stop",
                )
            ],
            usage=UsageInfo(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=0.0,
            ),
        )

    # --- CACHE MISS PATH ---
    # Forward request upstream to OpenAI
    upstream_response = await llm_service.forward_request(request_payload, api_key)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    completion_text = upstream_response.choices[0].message.content

    # Save output to Qdrant vector database
    new_cache_entry = await cache_service.save_cache(
        prompt_text=prompt_text,
        completion_text=completion_text,
        provider=request_payload.provider,
        model=request_payload.model,
        prompt_hash=prompt_hash,
    )

    # Assemble Metadata DTO
    metadata = FirewallMetadata(
        request_id=request_id,
        provider=request_payload.provider,
        model=request_payload.model,
        cache_hit=False,
        similarity_score=None,
        cache_key=new_cache_entry.cache_key,
        prompt_hash=prompt_hash,
        latency_ms=round(elapsed_ms, 2),
        estimated_cost_usd=upstream_response.usage.estimated_cost_usd or 0.0,
        estimated_cost_saved_usd=0.0,
    )

    # Audit Transaction Async
    await audit_service.log_transaction(
        db=db,
        metadata=metadata,
        prompt_text=prompt_text,
        completion_text=completion_text,
        prompt_tokens=upstream_response.usage.prompt_tokens,
        completion_tokens=upstream_response.usage.completion_tokens,
        client_ip=client_ip,
        user_id=request_payload.user_id,
        session_id=request_payload.session_id,
    )

    # Inject Diagnostic Headers
    response.headers["X-Firewall-Cache-Hit"] = "false"
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Latency-MS"] = str(round(elapsed_ms, 2))

    return upstream_response