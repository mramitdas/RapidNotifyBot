"""Per-key sliding-window rate limiter backed by Postgres (or test DB)."""

from datetime import timedelta

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import RateLimitHit, utcnow


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"rate limit exceeded, retry in {retry_after}s")


async def check_and_record(
    session: AsyncSession,
    api_key_hash: str,
    limit: int | None = None,
    window_seconds: int | None = None,
) -> None:
    """Count hits inside the window; raise if at the limit, else record one."""
    settings = get_settings()
    max_requests = limit if limit is not None else settings.rate_limit_requests
    window = timedelta(
        seconds=(
            window_seconds
            if window_seconds is not None
            else settings.rate_limit_window_seconds
        )
    )
    now = utcnow()

    count = await session.scalar(
        select(func.count())
        .select_from(RateLimitHit)
        .where(RateLimitHit.api_key_hash == api_key_hash)
        .where(RateLimitHit.ts > now - window)
    )
    if count is not None and count >= max_requests:
        raise RateLimitExceeded(retry_after=int(window.total_seconds()))

    await session.execute(
        delete(RateLimitHit).where(RateLimitHit.ts < now - window - timedelta(days=7))
    )
    await session.execute(
        insert(RateLimitHit).values(api_key_hash=api_key_hash, ts=now)
    )
    await session.commit()
