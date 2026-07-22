import time
import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import tiktoken

from app.config import settings
from app.schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChoiceMessage,
    UsageInfo,
)


class LLMService:
    """Handles upstream LLM communication, token counting, and cost estimations."""

    def __init__(self):
        self.http_client = httpx.AsyncClient(
            base_url=settings.UPSTREAM_BASE_URL,
            timeout=httpx.Timeout(30.0, connect=5.0),
            verify=False,  # <-- Bypasses SSL cert verification for local dev/VPNs
        )

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
        """Calculates exact token count using tiktoken encoding."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    @staticmethod
    def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates total cost in USD based on configured token rates."""
        prompt_cost = (prompt_tokens / 1000.0) * settings.PROMPT_TOKEN_COST_PER_1K
        completion_cost = (completion_tokens / 1000.0) * settings.COMPLETION_TOKEN_COST_PER_1K
        return round(prompt_cost + completion_cost, 6)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def forward_request(
        self, request_payload: ChatCompletionRequest, api_key: str
    ) -> ChatCompletionResponse:
        """Forwards completion request upstream to OpenAI with automatic retry logic."""
        headers = {
            "Authorization": f"Bearer {api_key or settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        # Convert Pydantic model to dict, dropping gateway-only fields
        payload = request_payload.model_dump(
            exclude={"provider", "user_id", "session_id"}, exclude_none=True
        )

        logger.info(f"📡 Forwarding request upstream -> {settings.UPSTREAM_BASE_URL}/chat/completions ({request_payload.model})")
        start_time = time.perf_counter()

        response = await self.http_client.post(
            "/chat/completions",
            json=payload,
            headers=headers,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if response.status_code != 200:
            logger.error(f"Upstream provider error [{response.status_code}]: {response.text}")
            response.raise_for_status()

        data = response.json()
        
        # Parse usage stats
        usage_data = data.get("usage", {})
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
        cost_usd = self.calculate_cost(prompt_tokens, completion_tokens)

        choices = [
            ChatCompletionChoice(
                index=c["index"],
                message=ChoiceMessage(
                    role=c["message"]["role"],
                    content=c["message"]["content"]
                ),
                finish_reason=c.get("finish_reason", "stop")
            )
            for c in data.get("choices", [])
        ]

        return ChatCompletionResponse(
            id=data.get("id", "chatcmpl-unknown"),
            created=data.get("created", int(time.time())),
            model=data.get("model", request_payload.model),
            choices=choices,
            usage=UsageInfo(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost_usd,
            ),
        )


# Singleton Service Instance
llm_service = LLMService()