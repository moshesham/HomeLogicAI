from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from core.config import settings

Base = declarative_base()


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite://") or database_url.startswith(
        "postgresql+asyncpg://"
    ):
        return database_url
    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


raw_database_url = settings.database_url
database_url = _normalize_database_url(raw_database_url)
# Treat both "sqlite://" and already-normalised "sqlite+aiosqlite://" URLs as SQLite
is_sqlite = raw_database_url.startswith("sqlite://") or raw_database_url.startswith(
    "sqlite+aiosqlite://"
)

engine_options: dict[str, object] = {}
if is_sqlite:
    engine_options["connect_args"] = {"check_same_thread": False}
    sqlite_test_suffixes = ("/test.db", "/test.sqlite", "/test.sqlite3")
    if raw_database_url.endswith(":memory:") or raw_database_url.endswith(
        sqlite_test_suffixes
    ):
        engine_options["poolclass"] = StaticPool

engine: AsyncEngine = create_async_engine(database_url, **engine_options)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional session and finalize with commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
