"""API tests for /me, /key/rotate and the /channels registration page."""

import anyio
from sqlalchemy import select

from app.api.pages import issue_registration_token
from app.db import models as m


def test_me_lists_registered_channels(client) -> None:
    http_client, _holder = client
    resp = http_client.get("/api/v1/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["telegram_user_id"] == 4242
    assert body["channels"] == ["slack"]
    assert body["rate_limit_tier"] == "standard"


def test_me_requires_key(client) -> None:
    http_client, _holder = client
    http_client.headers.pop("X-API-Key", None)
    assert http_client.get("/api/v1/me").status_code == 401


def test_rotate_key_shows_new_key_and_invalidates_old(client) -> None:
    http_client, holder = client
    old_key = holder["raw_key"]

    resp = http_client.post("/api/v1/key/rotate")
    assert resp.status_code == 200
    new_key = resp.json()["detail"]
    assert new_key.startswith("rn_")
    assert new_key != old_key

    http_client.headers.pop("X-API-Key", None)
    http_client.headers.update({"X-API-Key": old_key})
    assert http_client.get("/api/v1/me").status_code == 401

    http_client.headers.update({"X-API-Key": new_key})
    assert http_client.get("/api/v1/me").status_code == 200


def _issue_token(db) -> str:
    async def _do() -> str:
        async with db() as s:
            return await issue_registration_token(s, 4242)

    return anyio.run(_do)


def test_registration_token_page_is_single_use(client) -> None:
    http_client, holder = client
    raw = _issue_token(holder["db"])

    page = http_client.get(f"/api/channels/entry/{raw}")
    assert page.status_code == 200
    assert "Register a notification channel" in page.text

    again = http_client.get(f"/api/channels/entry/{raw}")
    assert again.status_code == 410


def test_garbage_token_page_gone(client) -> None:
    http_client, _holder = client
    assert http_client.get("/api/channels/entry/not-a-real-token").status_code == 410


def test_channels_save_registers_discord_channel(client) -> None:
    http_client, holder = client
    raw = _issue_token(holder["db"])
    assert http_client.get(f"/api/channels/entry/{raw}").status_code == 200

    saved = http_client.post(
        "/api/channels/save",
        data={
            "telegram_user_id": 4242,
            "channel": "discord",
            "webhook_url": "https://discord.com/api/webhooks/1/abc",
        },
    )
    assert saved.status_code == 200
    assert "Discord channel saved" in saved.text

    me = http_client.get("/api/v1/me").json()
    assert me["channels"] == ["discord", "slack"]


def test_channels_save_updates_existing_channel(client) -> None:
    http_client, holder = client
    new_url = "https://hooks.slack.com/services/T2/B2/X2"
    resp = http_client.post(
        "/api/channels/save",
        data={
            "telegram_user_id": 4242,
            "channel": "slack",
            "webhook_url": new_url,
        },
    )
    assert resp.status_code == 200

    db = holder["db"]

    async def _check() -> str:
        async with db() as s:
            user = await s.scalar(select(m.User).where(m.User.telegram_user_id == 4242))
            ch = await s.scalar(
                select(m.Channel).where(
                    m.Channel.user_id == user.id, m.Channel.type == "slack"
                )
            )
            return ch.config["webhook_url"]

    assert anyio.run(_check) == new_url

    me = http_client.get("/api/v1/me").json()
    assert me["channels"] == ["slack"]


def test_channels_save_blocks_private_urls(client) -> None:
    http_client, _holder = client
    resp = http_client.post(
        "/api/channels/save",
        data={
            "telegram_user_id": 4242,
            "channel": "webhook",
            "webhook_url": "https://127.0.0.5/hook",
        },
    )
    assert resp.status_code == 200
    assert "Blocked" in resp.text


def test_channels_save_unknown_channel(client) -> None:
    http_client, _holder = client
    resp = http_client.post(
        "/api/channels/save",
        data={
            "telegram_user_id": 4242,
            "channel": "carrier-pigeon",
            "webhook_url": "https://example.com/h",
        },
    )
    assert "Unknown channel" in resp.text


def test_channels_save_missing_url(client) -> None:
    http_client, _holder = client
    resp = http_client.post(
        "/api/channels/save",
        data={"telegram_user_id": 4242, "channel": "slack", "webhook_url": ""},
    )
    assert "Webhook URL required" in resp.text
