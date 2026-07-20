import asyncio
import json
import sys
from pathlib import Path

# Clean path calculation: guarantees backend import resolution regardless of working directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from loguru import logger
from app.config import settings
from app.services.cache_service import cache_service

SEED_DATA_FILE = SCRIPT_DIR / "seed_data.json"


async def seed_semantic_cache() -> None:
    """Reads seed_data.json, vectorizes entries via FastEmbed, and upserts into Qdrant."""
    logger.info("🌱 Starting Qdrant Semantic Cache Seeding Script...")
    logger.info(f"Targeting Qdrant host: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

    if not SEED_DATA_FILE.exists():
        logger.error(f"❌ Seed dataset file not found at: {SEED_DATA_FILE}")
        return

    with open(SEED_DATA_FILE, "r", encoding="utf-8") as f:
        seed_items = json.load(f)

    total_items = len(seed_items)
    inserted_count = 0

    # Provider and model fallback options
    provider = getattr(settings, "DEFAULT_PROVIDER", "openai")
    model = getattr(settings, "DEFAULT_MODEL", "gpt-4o-mini")

    for idx, item in enumerate(seed_items, 1):
        prompt = item["prompt"]
        response = item["response"]

        # 1. Synchronous prompt SHA-256 hash generation
        prompt_hash = cache_service.generate_prompt_hash(prompt)

        # 2. Asynchronous Qdrant vector store upsert
        try:
            await cache_service.save_cache(
                prompt_text=prompt,
                completion_text=response,
                provider=provider,
                model=model,
                prompt_hash=prompt_hash,
            )
            inserted_count += 1
            logger.info(f"[{idx}/{total_items}] Cached: '{prompt[:45]}...'")
        except Exception as exc:
            logger.error(f"Failed to cache prompt '{prompt[:30]}...': {exc}")

    # Synchronous count check
    vector_count = cache_service.get_collection_size()
    logger.success(f"🎉 Successfully seeded {inserted_count}/{total_items} vector cache entries into Qdrant!")
    logger.info(f"Current Qdrant collection size: {vector_count} vectors")


if __name__ == "__main__":
    asyncio.run(seed_semantic_cache())