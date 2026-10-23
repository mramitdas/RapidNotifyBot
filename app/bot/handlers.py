"""Telegram bot command handlers — pure-ish logic, testable without Telegram.

Each function takes a DB session maker and returns reply text; the Telegram
wiring lives in bot/main.py.
"""

from typing import Any

import structlog
from sqlalchemy import select

from app.api.pages import issue_registration_token
from app.channels.registry import supported_channels
from app.core.config import Settings
from app.core.security import generate_api_key, hash_key
from app.db import models as m

log = structlog.get_logger("bot")

WELCOME = (
    "👋 Welcome to RapidNotify!\n\n"
    "Send notifications to your Telegram, Slack, Discord or webhook from "
    "anywhere with a single API call.\n\n"
    "Commands:\n/subscribe — get your API key and channel setup link\n"
    "/help — this message"
)
HELP = WELCOME


async def subscribe(session: Any, settings: Settings, telegram_user_id: int) -> str:
    """Create (or rotate) the API key and return the onboarding message."""
    user = await session.scalar(
        select(m.User).where(m.User.telegram_user_id == telegram_user_id)
    )
    raw_key = generate_api_key()
    if user is None:
        user = m.User(
            telegram_user_id=telegram_user_id,
            api_key_hash=hash_key(raw_key, settings.key_pepper),
        )
        session.add(user)
        await session.flush()
        created = True
    else:
        user.api_key_hash = hash_key(raw_key, settings.key_pepper)
        created = False

    # The Telegram channel is implicit at subscribe time: notify() requires a
    # Channel row per user, so create it (config carries the default chat_id).
    tg_channel = await session.scalar(
        select(m.Channel).where(
            m.Channel.user_id == user.id, m.Channel.type == "telegram"
        )
    )
    if tg_channel is None:
        session.add(
            m.Channel(
                user_id=user.id,
                type="telegram",
                config={"chat_id": telegram_user_id},
            )
        )

    token_raw = await issue_registration_token(session, telegram_user_id)
    link = f"{settings.public_base_url.rstrip('/')}" f"/api/channels/entry/{token_raw}"
    intro = "🔑 Your new API key" if created else "🔑 Your API key (rotated)"
    return (
        f"{intro} — shown only once:\n\n"
        f"`{raw_key}`\n\n"
        "Register Slack, Discord or webhook channels here:\n"
        f"{link}\n\n"
        f"Then POST to {{base}}/api/v1/notify with X-API-Key header. "
        f"Channels supported: {', '.join(supported_channels())}."
    )
