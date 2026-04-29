from __future__ import annotations

# ---------------------------------------------------------------------------
# Set required environment variables BEFORE any backend module is imported.
# ---------------------------------------------------------------------------
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-fake-test-key-for-unit-testing-only")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-characters!!")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("STORAGE_PATH", "/tmp/homelogicai_test_storage")

import pytest_asyncio  # noqa: E402
from pathlib import Path  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.database import Base, get_db  # noqa: E402
import models  # noqa: E402, F401 — registers all ORM models with Base

# ---------------------------------------------------------------------------
# Per-test SQLite DB file — full isolation without pool tricks.
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_engine(tmp_path: Path):
    """Create a fresh SQLite database file for each test."""
    db_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    """Async HTTP client wired to the FastAPI app with the per-test DB."""
    from main import app

    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Convenience fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    reg = await client.post(
        "/auth/register",
        json={
            "email": "fixture@example.com",
            "full_name": "Fixture User",
            "password": "FixturePass1!",
        },
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def project_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post(
        "/projects",
        json={"name": "Test Project"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest_asyncio.fixture
async def room_id(client: AsyncClient, auth_headers: dict, project_id: str) -> str:
    resp = await client.post(
        f"/projects/{project_id}/rooms",
        json={"name": "Kitchen", "display_order": 0},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest_asyncio.fixture
async def category_id(client: AsyncClient, auth_headers: dict, room_id: str) -> str:
    resp = await client.post(
        f"/rooms/{room_id}/categories",
        json={
            "category_slug": "ceiling-fans",
            "display_name": "Ceiling Fans",
            "display_order": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]
