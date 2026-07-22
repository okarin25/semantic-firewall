import asyncio
import hashlib
from datetime import datetime
from typing import Optional, Tuple
from fastembed import TextEmbedding
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.schemas import CacheEntry


class CacheService:
    """Manages vector embeddings and Qdrant semantic caching operations."""

    def __init__(self):
        try:
            logger.info(f"Connecting to Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2.0)
            # Test connection
            self.client.get_collections()
        except Exception as e:
            logger.warning(f"Qdrant server unavailable ({e}). Falling back to local embedded Qdrant storage.")
            self.client = QdrantClient(path="./local_qdrant_storage")
        
        logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL}")
        self.embed_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        
        # Collection vector dimension for BAAI/bge-small-en-v1.5 is 384
        self.vector_size = 384
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Creates the Qdrant vector collection if it does not already exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if settings.QDRANT_COLLECTION not in collections:
                logger.info(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION}")
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
        except Exception as exc:
            logger.error(f"Failed to initialize Qdrant collection: {exc}")
            raise

    @staticmethod
    def generate_prompt_hash(prompt_text: str) -> str:
        """Generates a deterministic SHA-256 hash of normalized prompt text."""
        normalized_prompt = prompt_text.strip().lower()
        return hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest()

    async def _get_embedding(self, text: str) -> list[float]:
        """Runs FastEmbed CPU embedding in a thread pool to avoid blocking the async event loop."""
        def _embed():
            generators = list(self.embed_model.embed([text]))
            return generators[0].tolist()

        return await asyncio.to_thread(_embed)

    async def search_cache(
        self, prompt_text: str, threshold: Optional[float] = None
    ) -> Optional[Tuple[CacheEntry, float]]:
        """Searches Qdrant for a semantically similar cached response."""
        similarity_cutoff = threshold or settings.SIMILARITY_THRESHOLD
        query_vector = await self._get_embedding(prompt_text)

        def _search():
            response = self.client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_vector,
                limit=1,
                with_payload=True,
            )
            return response.points

        results = await asyncio.to_thread(_search)

        if not results:
            return None

        best_match = results[0]
        score = float(best_match.score)

        if score >= similarity_cutoff:
            logger.info(f"🎯 Cache HIT! Similarity score: {score:.4f} >= Threshold: {similarity_cutoff}")
            payload = best_match.payload
            cache_entry = CacheEntry(**payload)
            return cache_entry, score

        logger.info(f"❄️ Cache MISS. Best similarity score: {score:.4f} < Threshold: {similarity_cutoff}")
        return None

    async def save_cache(
        self,
        prompt_text: str,
        completion_text: str,
        provider: str,
        model: str,
        prompt_hash: str,
    ) -> CacheEntry:
        """Stores a prompt-completion pair in Qdrant vector database."""
        vector = await self._get_embedding(prompt_text)
        cache_key = f"cache-{prompt_hash[:16]}"

        cache_entry = CacheEntry(
            cache_key=cache_key,
            prompt_hash=prompt_hash,
            prompt_text=prompt_text,
            completion_text=completion_text,
            provider=provider,
            model=model,
            embedding_model=settings.EMBEDDING_MODEL,
            similarity_threshold=settings.SIMILARITY_THRESHOLD,
            created_at=datetime.utcnow(),
        )

        point = PointStruct(
            id=cache_key,
            vector=vector,
            payload=cache_entry.model_dump(mode="json"),
        )

        def _upsert():
            self.client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=[point],
            )

        await asyncio.to_thread(_upsert)
        logger.info(f"💾 Saved new entry to Qdrant cache key: {cache_key}")
        return cache_entry

    def get_collection_size(self) -> int:
        """Returns total vector count in cache."""
        try:
            info = self.client.get_collection(collection_name=settings.QDRANT_COLLECTION)
            return info.points_count or 0
        except Exception:
            return 0


# Singleton Service Instance
cache_service = CacheService()