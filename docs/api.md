# API Reference (v1)

Base path: `/api/v1`. Authentication: `X-API-Key: <key>` header or
`Authorization: Bearer <key>`. Keys are shown once at `/subscribe` (or key
rotation) and stored hashed.

## POST /api/v1/notify

Deliver a notification through a registered channel.

Request:
```json
{
  "channel": "telegram | slack | discord | webhook",
  "data": { "any": "values", "nested": { "arrays": "ok" } }
}
```

Responses:

| Code | Meaning |
|---|---|
| 200 | sent to ≥1 channel → `{"status": "success", "channel": "...", "recipients": N}` |
| 400 | unsupported channel name |
| 401 | missing/invalid key |
| 404 | no enabled channel of that type registered |
| 413 | payload above `MAX_PAYLOAD_BYTES` |
| 429 | rate limit exceeded (has `Retry-After`) |
| 502 | all deliveries failed |

Allowed channels are exactly the registered per-user channel types;
messages are rendered as `key: value` lines (dicts flattened).

## GET /api/v1/me

```json
{"id": 1, "telegram_user_id": 4242, "rate_limit_tier": "standard", "channels": ["slack"]}
```

## POST /api/v1/key/rotate

Generates a replacement key in the response (`detail` field). The old key
stops working immediately. Show it once; we cannot re-show existing keys.

## GET /api/channels/entry/{token} (page)

Single-use, 15-minute token link issued by the bot on `/subscribe`. Lets
the user register/update Slack, Discord and generic webhook channels.
Webhook URLs are SSRF-validated (private IP ranges blocked).

## Rate limiting

Sliding window per API key stored in Postgres (no Redis). Defaults:
`RATE_LIMIT_REQUESTS=60` per `RATE_LIMIT_WINDOW_SECONDS=60`. Tune through
env; `users.rate_limit_tier` exists for future per-plan limits.

## Error shape

FastAPI JSON: `{"detail": "..."}`.
