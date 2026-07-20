from typing import AsyncGenerator
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# Initialize Async Engine with connection pooling settings
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True if "postgresql" in settings.DATABASE_URL else False,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for yielding transactional async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session rollback due to error: {exc}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Creates database tables if they do not exist (for dev setup)."""
    async with engine.begin() as conn:
        logger.info("Initializing relational database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables successfully created/verified.")