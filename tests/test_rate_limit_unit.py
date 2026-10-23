"""Unit tests for the sliding-window rate limiter."""

import anyio
from sqlalchemy import func, pool, select
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from app.core.config import get_settings
from app.core.rate_limit import RateLimitExceeded, check_and_record
from app.db import models as m
from app.db.engine import Base

compiles(PG_JSONB, "sqlite")(lambda type_, compiler, **kw: "JSON")


def _db(tmp_path):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path}/rl.db", poolclass=pool.NullPool
    )

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    anyio.run(_create)
    return async_sessionmaker(engine, expire_on_commit=False)


async def _raise_if_limited(sm, key):
    async with sm() as session:
        try:
            await check_and_record(session, key)
        except RateLimitExceeded:
            return True
    return False


def test_limiter_allows_up_to_limit_then_raises(tmp_path) -> None:
    sm = _db(tmp_path)
    key = "h" * 64
    limit = get_settings().rate_limit_requests

    async def _run() -> tuple[int, bool]:
        async with sm() as session:
            for _ in range(limit):
                await check_and_record(session, key)
        blocked = await _raise_if_limited(sm, key)
        async with sm() as session:
            hits = await session.scalar(
                select(func.count()).select_from(m.RateLimitHit)
            )
        return hits, blocked

    hits, blocked = anyio.run(_run)
    assert hits == limit
    assert blocked is True


def test_limiter_records_hit_after_success(tmp_path) -> None:
    sm = _db(tmp_path)
    key = "g" * 64

    async def _run() -> int:
        await _raise_if_limited(sm, key)
        async with sm() as session:
            hits = await session.scalar(
                select(func.count()).select_from(m.RateLimitHit)
            )
        return hits

    assert anyio.run(_run) == 1


def test_raise_is_exception_instance() -> None:
    assert isinstance(RateLimitExceeded(5), Exception)
    assert RateLimitExceeded(5).retry_after == 5
