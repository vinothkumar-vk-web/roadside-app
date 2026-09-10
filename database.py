"""
Database & Cache Connection Pool Setup
Engineered for non-blocking async operations.
Supports PostgreSQL (PostGIS) in production, with seamless local SQLite (aiosqlite) fallback.
"""
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
logger = logging.getLogger("database")


# Environment Variable or SQLite Fallback
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Local resilient async SQLite database for zero-friction setup
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "roadside_app.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
    logger.info(f"Using local async SQLite DB at {DB_PATH}")

# Connection Pool Settings
if "sqlite" in DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=30,
        max_overflow=20,
        pool_pre_ping=True
    )

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
