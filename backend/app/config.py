from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "Semantic Firewall"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Upstream OpenAI Target
    OPENAI_API_KEY: str = Field(default="", description="Upstream OpenAI API Key")
    UPSTREAM_BASE_URL: str = "https://api.openai.com/v1"

    # Vector Storage (Qdrant)
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "semantic_cache"
    SIMILARITY_THRESHOLD: float = 0.88  # Cosine similarity threshold for cache hits
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"  # FastEmbed ONNX model

    # Relational Storage (PostgreSQL / SQLite fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./semantic_firewall.db"

    # Redis Cache & Rate Limiting
    REDIS_URL: str = "redis://localhost:6379/0"

    # Cost Calculation Constants ($ / 1k tokens - default gpt-4o-mini rates)
    PROMPT_TOKEN_COST_PER_1K: float = 0.00015
    COMPLETION_TOKEN_COST_PER_1K: float = 0.00060

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()