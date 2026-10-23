"""v1 API routes: notification relay."""

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession, Http
from app.api.schemas import SUPPORTED_CHANNELS, NotifyRequest, NotifyResponse
from app.channels.registry import send_to
from app.core.config import get_settings
from app.core.rate_limit import RateLimitExceeded, check_and_record
from app.db.models import Channel

log = structlog.get_logger("api")

api_router = APIRouter(prefix="/v1", tags=["notify"])


def render_message(data: dict) -> str:
    """Human-readable text from arbitrary payload data."""
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            inner = ", ".join(f"{ik}={iv}" for ik, iv in value.items())
            lines.append(f"{key}: {inner}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines) or "(empty)"


async def _user_channels(
    session: AsyncSession, user_id: int, channel_type: str
) -> list[Channel]:
    result = await session.scalars(
        select(Channel).where(
            Channel.user_id == user_id,
            Channel.type == channel_type,
            Channel.enabled.is_(True),
        )
    )
    channels: list[Channel] = list(result.unique().all())
    return channels


@api_router.post("/notify", response_model=NotifyResponse)
async def notify(
    payload: NotifyRequest,
    request: Request,
    http: Http,
    session: DBSession,
    user: CurrentUser,
) -> NotifyResponse:
    settings = get_settings()
    if payload.channel not in SUPPORTED_CHANNELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported channel '{payload.channel}'; "
                f"supported: {', '.join(SUPPORTED_CHANNELS)}"
            ),
        )
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_payload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds {settings.max_payload_bytes} bytes",
        )
    if len(str(payload.data)) + len(str(payload.channel)) > settings.max_payload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Data exceeds {settings.max_payload_bytes} bytes",
        )

    recipients = await _user_channels(session, user.id, payload.channel)
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No enabled '{payload.channel}' channel registered for this key",
        )

    try:
        await check_and_record(session, user.api_key_hash)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    message = render_message(payload.data)
    token = settings.bot_token if payload.channel == "telegram" else ""
    sent = 0
    for channel_row in recipients:
        result = await send_to(
            channel_row.type,
            dict(channel_row.config or {}),
            user.telegram_user_id,
            message,
            client=http,
            token=token,
        )
        if result.ok:
            sent += 1
        else:
            await log.awarning(
                "delivery failed",
                channel=channel_row.type,
                user_id=user.id,
                detail=result.detail,
            )

    if sent == 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="All deliveries failed",
        )
    return NotifyResponse(status="success", channel=payload.channel, recipients=sent)
