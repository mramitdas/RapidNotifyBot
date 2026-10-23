"""Shared test fixtures: FastAPI + disposable file-based SQLite + mock HTTP."""

from typing import Any, AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import pool
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from app.core.config import get_settings
from app.core.security import generate_api_key, hash_key
from app.db import models as m  # noqa: F401
from app.db.engine import Base

compiles(PG_JSONB, "sqlite")(lambda type_, compiler, **kw: "JSON")

PEPPER = "test-pepper"


class RecordingTransport(httpx.MockTransport):
    """Canned httpx responses; records every request."""

    def __init__(self, default_status: int = 200) -> None:
        self.requests: list[httpx.Request] = []
        self.default_status = default_status
        self.status_by_url: dict[str, int] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            code = self.status_by_url.get(str(request.url), self.default_status)
            if code == 204:
                return httpx.Response(204)
            if code == 200 and "telegram" in str(request.url):
                return httpx.Response(200, json={"ok": True})
            if code == 200:
                return httpx.Response(200, json={})
            return httpx.Response(code, json={"error": "boom"})

        super().__init__(handler)


@pytest_asyncio.fixture(autouse=True)
async def settings_env(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[None, None]:
    monkeypatch.setenv("KEY_PEPPER", PEPPER)
    monkeypatch.setenv("BOT_TOKEN", "TESTBOTTOKEN")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def db(tmp_path: Any):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path}/test.db",
        poolclass=pool.NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, expire_on_commit=False)
    yield sm
    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_user(db) -> tuple[int, str]:
    """Returns (telegram_user_id, raw_api_key) for a user with a slack channel."""
    raw = generate_api_key()
    key_hash = hash_key(raw, PEPPER)
    async with db() as s:
        user = m.User(telegram_user_id=4242, api_key_hash=key_hash)
        s.add(user)
        await s.flush()
        s.add(
            m.Channel(
                user_id=user.id,
                type="slack",
                config={"webhook_url": "https://hooks.slack.com/services/T/B/X"},
            )
        )
        await s.commit()
    return 4242, raw


@pytest_asyncio.fixture
async def client(db, seeded_user) -> AsyncGenerator[tuple[TestClient, Any], None]:
    """TestClient with overridden DB session and a mock-holding http client."""
    from app.api import deps
    from app.main import app

    holder: dict[str, Any] = {"db": db, "raw_key": seeded_user[1]}

    async def override_session():
        async with db() as session:
            yield session

    async def override_http():
        async with httpx.AsyncClient(
            transport=holder_tr, timeout=5.0, follow_redirects=False
        ) as http_client:
            yield http_client

    holder_tr = RecordingTransport()
    holder["transport"] = holder_tr

    app.dependency_overrides[deps.get_session] = override_session
    app.dependency_overrides[deps.get_http_client] = override_http
    with TestClient(app, headers={"X-API-Key": seeded_user[1]}) as http_client:
        yield http_client, holder
    app.dependency_overrides.clear()


async def fill_rate_limit(db, key_hash: str, limit: int) -> None:
    """Insert `limit` recent hits for a key hash (key must exist)."""
    async with db() as s:
        for _ in range(limit):
            s.add(m.RateLimitHit(api_key_hash=key_hash, ts=m.utcnow()))
        await s.commit()
