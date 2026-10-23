"""Channel-registration web page (token-gated) and form handling.

Flow: user asks the Telegram bot for a registration link; the bot stores a
hashed short-lived token, shows the raw token in
/api/channels/entry?t=<raw>. The page lets the user paste Slack/Discord
webhook URLs; generic webhooks too. Token is single-use.
"""

from pathlib import Path

import structlog
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBSession
from app.api.schemas import SUPPORTED_CHANNELS
from app.core.config import get_settings
from app.core.security import generate_registration_token, hash_key, is_ssrf_safe_url
from app.db.models import Channel, RegistrationToken, User, utcnow

log = structlog.get_logger("pages")

router = APIRouter(tags=["registration"])

_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Channels configurable from the page (telegram is implicit via /subscribe)
PAGE_CHANNELS = ("slack", "discord", "webhook")

TOKEN_TTL_MINUTES = 15


async def issue_registration_token(session: AsyncSession, telegram_user_id: int) -> str:
    raw = generate_registration_token()
    session.add(
        RegistrationToken(token_hash=hash_key(raw), telegram_user_id=telegram_user_id)
    )
    await session.commit()
    return raw


async def consume_token(session: AsyncSession, raw_token: str) -> int | None:
    """Return telegram_user_id if valid, unused, unexpired; else None."""
    token_hash = hash_key(raw_token)
    token = await session.scalar(
        select(RegistrationToken).where(
            RegistrationToken.token_hash == token_hash,
            RegistrationToken.used.is_(False),
        )
    )
    if token is None:
        return None
    created = token.created_at
    if created.tzinfo is None:  # SQLite stores naive UTC timestamps
        from datetime import timezone

        created = created.replace(tzinfo=timezone.utc)
    age_minutes = (utcnow() - created).total_seconds() / 60
    if age_minutes > TOKEN_TTL_MINUTES:
        return None
    token.used = True
    await session.commit()
    return token.telegram_user_id


def _base_url(request: Request) -> str:
    return get_settings().public_base_url.rstrip("/")


@router.get("/channels/entry/{raw_token}", response_class=HTMLResponse)
async def channel_page(
    request: Request, raw_token: str, session: DBSession
) -> HTMLResponse:
    telegram_user_id = await consume_token(session, raw_token)
    if telegram_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Registration link expired"
        )
    return _templates.TemplateResponse(
        request,
        "channels.html",
        {
            "telegram_user_id": telegram_user_id,
            "channels": PAGE_CHANNELS,
            "supported": ", ".join(SUPPORTED_CHANNELS[:-1]) + " and webhook",
            "base_url": _base_url(request),
        },
    )


@router.post("/channels/save", response_class=HTMLResponse)
async def channel_save(
    request: Request,
    session: DBSession,
    telegram_user_id: int = Form(...),
    channel: str = Form(...),
    webhook_url: str = Form(""),
) -> HTMLResponse:
    if channel not in PAGE_CHANNELS:
        return _templates.TemplateResponse(
            request,
            "result.html",
            {"ok": False, "message": "Unknown channel"},
        )
    if not webhook_url:
        return _templates.TemplateResponse(
            request,
            "result.html",
            {"ok": False, "message": "Webhook URL required"},
        )
    if not is_ssrf_safe_url(webhook_url, allow_http=True):
        return _templates.TemplateResponse(
            request,
            "result.html",
            {"ok": False, "message": "Blocked: private or non-http(s) URL"},
        )

    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if user is None:
        return _templates.TemplateResponse(
            request, "result.html", {"ok": False, "message": "Unknown user"}
        )
    existing = await session.scalar(
        select(Channel).where(Channel.user_id == user.id, Channel.type == channel)
    )
    if existing is not None:
        existing.config = {"webhook_url": webhook_url}
        existing.enabled = True
    else:
        session.add(
            Channel(
                user_id=user.id,
                type=channel,
                config={"webhook_url": webhook_url},
            )
        )
    await session.commit()
    await log.ainfo("channel registered", channel=channel, user_id=user.id)
    return _templates.TemplateResponse(
        request,
        "result.html",
        {"ok": True, "message": f"{channel.capitalize()} channel saved"},
    )
