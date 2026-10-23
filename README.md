# RapidNotify

[![CI](https://github.com/mramitdas/RapidNotifyBot/actions/workflows/ci.yml/badge.svg)](https://github.com/mramitdas/RapidNotifyBot/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal)](https://fastapi.tiangolo.com)
[![Postgres](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org)

**Self-hostable notification relay: subscribe via a Telegram bot, then send
notifications to Telegram, Slack, Discord, or any webhook with one API
call.**

```
   curl -X POST https://your-host/api/v1/notify \
        -H "X-API-Key: rn_your-key" \
        -H "Content-Type: application/json" \
        -d '{"channel": "slack", "data": {"service": "api", "state": "down"}}'
```

## Highlights

- **Multi-channel** — Telegram, Slack webhooks, Discord webhooks, generic
  webhooks (email is a documented extension point).
- **Commercially usable** — Apache 2.0 licensed, no MongoDB, no Redis, no
  vendor lock-in; single Postgres dependency.
- **Secure by design** — API keys stored hashed (sha256 + pepper), shown
  exactly once; webhook URLs SSRF-validated (private-IP blocking); rate
  limiting per key. See [key protection threat model](docs/api.md#how-your-api-key-is-protected).
- **Production-grade** — async FastAPI + SQLAlchemy 2.x, Alembic migrations,
  structured logs, Docker/compose, full test suite, CI-gated quality (black,
  isort, mypy, flake8, pytest).

## Quickstart (self-host, 3 commands)

```bash
cp .env.example .env          # fill BOT_TOKEN + KEY_PEPPER + POSTGRES_PASSWORD
docker compose up --build -d  # starts postgres → migrations → api + bot
curl http://localhost:8000/   # API docs
```

Then open your bot in Telegram and send `/subscribe` — you'll receive your
API key (shown **once**) and a link to register Slack/Discord/webhook
channels.

## Getting an API key (hosted bot flow)

1. Message [`@rapidnotifybot`](https://t.me/rapidnotifybot) → `/subscribe`
2. Copy the API key you receive (it is shown only once).
3. Follow the registration link to attach Slack/Discord/webhook channels.
4. Send notifications to `/api/v1/notify` with your key.

## API (v1)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/notify` | `POST` | Send a notification: `{"channel": "...", "data": {...}}` |
| `/api/v1/me` | `GET` | Account info: id, channels, rate tier |
| `/api/v1/key/rotate` | `POST` | Rotate your key (old key invalidates instantly) |
| `/api/channels/entry/{token}` | `GET` | Channel registration page (single-use token link) |

Auth: `X-API-Key: <key>` header or `Authorization: Bearer <key>`.
Full reference: [`docs/api.md`](docs/api.md).

Rate limits: sliding window per API key (default 60 requests / 60 s),
stored in Postgres. Response on breach: `429` + `Retry-After`.

## Development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env                 # then fill in values
pytest --cov=app                     # full test suite
black . && isort . && mypy app && flake8 app tests   # quality gates
alembic upgrade head                 # apply migrations
uvicorn app.main:app --reload        # API on :8000
python -m app.bot.main               # Telegram bot (separate terminal)
```

## Architecture

- `app/api/` — FastAPI app, routes, templates (registration page)
- `app/bot/` — Telegram bot process (`/subscribe`, `/help`)
- `app/channels/` — adapters behind a common interface
- `app/db/` — SQLAlchemy models, async engine, Alembic migrations
- `app/core/` — settings, security (key hashing, SSRF guard), rate limiting

Docs: [`docs/installation.md`](docs/installation.md),
[`docs/api.md`](docs/api.md).
Agent conventions for contributors: [`AGENTS.md`](AGENTS.md).

## Contributing

PRs welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) and the
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

Apache License 2.0 — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
