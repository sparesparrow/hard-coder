from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import AsyncGenerator
import logging
from contextlib import asynccontextmanager
import os

from .models.base import Base

logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost/system_monitor"
)

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db() -> None:
    """Initialize database by creating all tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def transaction(session: AsyncSession):
    """Transaction context manager."""
    try:
        async with session.begin():
            yield session
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        await session.rollback()
        raise

class DatabaseManager:
    """Database manager for handling connections and sessions."""
    
    def __init__(self):
        self._engine = engine
        self._session_factory = AsyncSessionLocal
    
    async def health_check(self) -> bool:
        """Check database connection."""
        try:
            async with self._session_factory() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup database connections."""
        try:
            await self._engine.dispose()
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up database connections: {str(e)}")
            raise
    
    @property
    def engine(self) -> AsyncEngine:
        """Get database engine."""
        return self._engine
    
    @property
    def session_factory(self):
        """Get session factory."""
        return self._session_factory

# Create database manager instance
db_manager = DatabaseManager() 