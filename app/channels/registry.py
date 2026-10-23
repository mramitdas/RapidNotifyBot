"""Registry mapping channel types to adapter singletons."""

from typing import Any

import httpx

from app.channels.base import SendResult
from app.channels.telegram import adapter as _telegram_adapter
from app.channels.webhook import adapter as _webhook_adapter
from app.channels.webhooks import discord_adapter, slack_adapter

ADAPTERS: dict[str, Any] = {
    _telegram_adapter.channel_type: _telegram_adapter,
    _webhook_adapter.channel_type: _webhook_adapter,
    slack_adapter.channel_type: slack_adapter,
    discord_adapter.channel_type: discord_adapter,
}


def get_adapter(channel_type: str) -> Any:
    return ADAPTERS.get(channel_type)


def supported_channels() -> list[str]:
    return sorted(ADAPTERS)


async def send_to(
    channel_type: str,
    config: dict[str, Any],
    user_id: int,
    message: str,
    client: httpx.AsyncClient | None = None,
    token: str = "",
) -> SendResult:
    """Dispatch a message through the registered adapter, or fail cleanly."""
    adapter = get_adapter(channel_type)
    if adapter is None:
        return SendResult(ok=False, detail=f"unknown channel: {channel_type}")
    return await adapter.send(config, user_id, message, client=client, token=token)
