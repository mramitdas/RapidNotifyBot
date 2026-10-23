"""Unit tests for channel adapters and the registry (httpx mock transport)."""

from typing import Any

import httpx
import pytest

from app.channels.base import SendResult
from app.channels.registry import ADAPTERS, get_adapter, send_to, supported_channels


class ListTransport(httpx.MockTransport):
    """Records requests and answers canned responses."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.status = 200
        self.body: dict[str, Any] = {"ok": True}

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return httpx.Response(self.status, json=self.body)

        super().__init__(handler)


@pytest.fixture
def transport() -> ListTransport:
    return ListTransport()


def test_registry_contains_four_channels() -> None:
    assert supported_channels() == ["discord", "slack", "telegram", "webhook"]
    for name in ("slack", "discord", "telegram", "webhook"):
        assert get_adapter(name) is not None
        assert get_adapter(name).channel_type == name
    assert get_adapter("email") is None


async def test_telegram_adapter_payload_and_success(
    transport: ListTransport,
) -> None:
    client = httpx.AsyncClient(transport=transport)
    result = await send_to(
        "telegram",
        {"chat_id": 42},
        user_id=42,
        message="hello",
        client=client,
        token="TOK",
    )
    await client.aclose()
    assert result.ok and result.detail == "sent"
    req = transport.requests[0]
    assert req.url.path.endswith("/botTOK/sendMessage")
    assert b'"chat_id":42' in req.content
    assert b"hello" in req.content


async def test_telegram_adapter_truncates_and_defaults_chat_id(
    transport: ListTransport,
) -> None:
    client = httpx.AsyncClient(transport=transport)
    adapter = get_adapter("telegram")
    payload = adapter.build_payload({}, user_id=7, message="x" * 5000)
    assert payload["chat_id"] == 7
    assert len(payload["text"]) == 4096
    await client.aclose()


async def test_slack_adapter_sends_to_registered_webhook(
    transport: ListTransport,
) -> None:
    client = httpx.AsyncClient(transport=transport)
    url = "https://hooks.slack.com/services/T000/B000/XYZ"
    result = await send_to(
        "slack",
        {"webhook_url": url, "blocks": [{"type": "divider"}]},
        user_id=1,
        message="hi",
        client=client,
    )
    await client.aclose()
    assert result.ok
    req = transport.requests[0]
    assert str(req.url) == url
    assert b'"blocks"' in req.content


async def test_slack_adapter_requires_webhook_url(
    transport: ListTransport,
) -> None:
    client = httpx.AsyncClient(transport=transport)
    result = await send_to("slack", {}, user_id=1, message="hi", client=client)
    await client.aclose()
    assert result.ok is False
    assert "missing webhook_url" in result.detail


async def test_discord_adapter_success_on_204(transport: ListTransport) -> None:
    transport.status = 204
    transport.body = {}
    client = httpx.AsyncClient(transport=transport)
    result = await send_to(
        "discord",
        {"webhook_url": "https://discord.com/api/webhooks/1/2", "username": "Bot"},
        user_id=1,
        message="hi",
        client=client,
    )
    await client.aclose()
    assert result.ok
    req = transport.requests[0]
    assert b'"username":"Bot"' in req.content.replace(b" ", b"")


async def test_webhook_adapter_posts_and_validates_success(
    transport: ListTransport,
) -> None:
    client = httpx.AsyncClient(transport=transport)
    result = await send_to(
        "webhook",
        {"url": "https://example.com/hook", "headers": {"X-Auth": "z"}},
        user_id=5,
        message="payload",
        client=client,
    )
    await client.aclose()
    assert result.ok
    req = transport.requests[0]
    assert req.headers.get("X-Auth") == "z"
    assert b"payload" in req.content


async def test_send_to_unknown_channel_returns_failure() -> None:
    result = await send_to("email", {}, user_id=1, message="m")
    assert isinstance(result, SendResult)
    assert result.ok is False
    assert "unknown channel" in result.detail


def test_adapter_count_matches_expected() -> None:
    assert len(ADAPTERS) == 4
