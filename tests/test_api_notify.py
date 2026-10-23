"""API tests for POST /api/v1/notify (behavior via FastAPI + mock http)."""

import anyio

from app.core.config import get_settings
from app.core.security import hash_key
from tests.conftest import RecordingTransport, fill_rate_limit


def test_notify_success_forwarded_to_registered_channel(client) -> None:
    http_client, holder = client
    resp = http_client.post(
        "/api/v1/notify",
        json={"channel": "slack", "data": {"service": "api", "state": "down"}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["channel"] == "slack"
    assert body["recipients"] == 1

    transport: RecordingTransport = holder["transport"]
    assert len(transport.requests) == 1
    req = transport.requests[0]
    assert str(req.url) == "https://hooks.slack.com/services/T/B/X"
    content = req.content.decode()
    assert "service: api" in content
    assert "state: down" in content


def test_notify_missing_key_rejected(client) -> None:
    http_client, _holder = client
    http_client.headers.pop("X-API-Key", None)
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
    )
    assert resp.status_code == 401


def test_notify_invalid_api_key_rejected(client) -> None:
    http_client, _holder = client
    http_client.headers.update({"X-API-Key": "rn_totally-invalid-key-value"})
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
    )
    assert resp.status_code == 401


def test_notify_unknown_channel_rejected(client) -> None:
    http_client, _holder = client
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "pagerduty", "data": {"a": 1}}
    )
    assert resp.status_code == 400
    assert "pagerduty" in resp.json()["detail"]


def test_notify_no_registered_channel_404(client) -> None:
    http_client, _holder = client
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "discord", "data": {"a": 1}}
    )
    assert resp.status_code == 404
    assert "discord" in resp.json()["detail"]


def test_notify_all_deliveries_failed_502(client) -> None:
    http_client, holder = client
    assert (
        http_client.post(
            "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
        ).status_code
        == 200
    )
    transport: RecordingTransport = holder["transport"]
    transport.status_by_url["https://hooks.slack.com/services/T/B/X"] = 500
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
    )
    assert resp.status_code == 502


def test_notify_rate_limited_429_with_retry_after(client) -> None:
    http_client, holder = client
    key_hash = hash_key(holder["raw_key"], get_settings().key_pepper)
    limit = get_settings().rate_limit_requests

    async def _fill() -> None:
        await fill_rate_limit(holder["db"], key_hash, limit)

    anyio.run(_fill)

    resp = http_client.post(
        "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
    )
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) >= 1


def test_notify_accepts_bearer_auth(client) -> None:
    http_client, holder = client
    http_client.headers.clear()
    http_client.headers.update({"Authorization": f"Bearer {holder['raw_key']}"})
    resp = http_client.post(
        "/api/v1/notify", json={"channel": "slack", "data": {"a": 1}}
    )
    assert resp.status_code == 200


def test_empty_data_rejected(client) -> None:
    http_client, _holder = client
    resp = http_client.post("/api/v1/notify", json={"channel": "slack", "data": {}})
    assert resp.status_code == 422


def test_nested_data_rendered_flat(client) -> None:
    http_client, holder = client
    resp = http_client.post(
        "/api/v1/notify",
        json={"channel": "slack", "data": {"deploy": {"env": "prod", "by": "amit"}}},
    )
    assert resp.status_code == 200
    req = holder["transport"].requests[0]
    assert "env=prod, by=amit" in req.content.decode()
