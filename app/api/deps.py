"""FastAPI dependencies: API-key auth and shared httpx client."""

from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_key
from app.db.engine import get_session
from app.db.models import User

DBSession = Annotated[AsyncSession, Depends(get_session)]


async def parse_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[len("Bearer ") :]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API key (X-API-Key or Authorization: Bearer)",
    )


ApiKeyRaw = Annotated[str, Depends(parse_api_key)]


async def get_user(raw_key: ApiKeyRaw, session: DBSession) -> User:
    key_hash = hash_key(raw_key, get_settings_pepper())
    user = await session.scalar(select(User).where(User.api_key_hash == key_hash))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return user


def get_settings_pepper() -> str:
    from app.core.config import get_settings

    return get_settings().key_pepper


CurrentUser = Annotated[User, Depends(get_user)]


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Outbound client; overridden in tests with a mock transport."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        yield client


Http = Annotated[httpx.AsyncClient, Depends(get_http_client)]
