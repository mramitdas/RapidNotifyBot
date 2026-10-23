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

## How your API key is protected

Storage model: `sha256(KEY_PEPPER + raw_key)` — the raw key is never
persisted; only the hash is stored, so a key can be shown exactly once
(at `/subscribe` or key rotation).

Why no per-key salt?

- **Salts defend against precomputation and password reuse.** They matter
  for low-entropy secrets (passwords). RapidNotify keys are 192-bit random
  tokens (`rn_` + 32 urlsafe chars); each key is already high-entropy, so
  rainbow tables and credential-stuffing attacks do not apply.
- **Point lookup requires a deterministic global hash.** Auth computes one
  hash of the presented key and does an indexed lookup. A per-key salt
  cannot be applied before the key is known — lookups would degrade into
  scans or require an auxiliary salt→key mapping.

Why a pepper at all? The pepper lives in the environment (`KEY_PEPPER`),
not in the database:

- **DB leak alone** → attacker gets SHA-256 hashes of 192-bit random keys;
  brute force is computationally infeasible (~2^192), pepper makes
  precomputation impossible too.
- **ENV leak alone** → no hashes at all to attack.
- **Both leak together** → reversing hashes still requires brute-forcing a
  192-bit key. Practical risk is negligible.

Threat-model boundaries (what this design does *not* claim):

- If an attacker obtains a valid raw key itself (e.g., from your logs or
  chat history), hashing does not help — treat keys like passwords: log
  them nowhere, share over no chat.
- `KEY_PEPPER` staying constant means no re-hash on restart; changing it
  invalidates every stored key hash (documented in installation.md).
- A slow KDF (argon2id/HMAC upgrade) was evaluated and deliberately
  skipped: it complicates point lookups for negligible gain at this key
  entropy. Revisit if the key format ever becomes human-chosen.
