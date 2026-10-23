# Installation

## Prerequisites

- Python 3.12+ (or Docker)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- PostgreSQL 16 (Docker is used locally by docker-compose)

## Option A — Docker (recommended)

```bash
git clone https://github.com/mramitdas/RapidNotifyBot.git
cd RapidNotifyBot
cp .env.example .env        # then edit: BOT_TOKEN, KEY_PEPPER, POSTGRES_PASSWORD
docker compose up --build -d
```

- API docs: http://localhost:8000/ (docs UI at root)
- Bot: send `/subscribe` to your bot on Telegram

Set `public_base_url` to the public address of the API so the bot can link
to the channel-registration page. Stop the stack:
`docker compose down` (keep data: `-v` removes it).

## Option B — manual

```bash
git clone https://github.com/mramitdas/RapidNotifyBot.git
cd RapidNotifyBot
python -m venv venv && source venv/bin/activate
pip install -r requirements/prod.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app          # terminal 1
python -m app.bot.main        # terminal 2
```

## Environment

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | yes | `postgresql+asyncpg://user:pass@host:5432/rapidnotify` |
| `BOT_TOKEN` | yes | Telegram bot token |
| `KEY_PEPPER` | yes | Random ≥32-char string used to hash API keys |
| `RATE_LIMIT_REQUESTS` | no | Max requests per window (default 60) |
| `RATE_LIMIT_WINDOW_SECONDS` | no | Window length (default 60) |
| `MAX_PAYLOAD_BYTES` | no | Notification data cap (default 8192) |
| `public_base_url` | no | Public API base URL used in bot links |

Never commit `.env`. Keep `KEY_PEPPER` constant across restarts — changing
it invalidates every stored key hash.
