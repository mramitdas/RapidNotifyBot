"""Telegram bot process entry point (long polling, separate process)."""

from typing import Any, cast

import structlog
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from app.bot.handlers import HELP, WELCOME, subscribe
from app.core.config import get_settings
from app.db.engine import SessionLocal

log = structlog.get_logger("bot")


def _msg(update: Update) -> Any:
    return update.message or update.effective_message


async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _msg(update).reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN_V2)


async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _msg(update).reply_text(HELP, parse_mode=ParseMode.MARKDOWN_V2)


async def _cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    telegram_user_id = cast("Any", update.effective_user).id
    async with SessionLocal() as session:
        text = await subscribe(session, settings, telegram_user_id)
        await session.commit()
    await _msg(update).reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


def create_application() -> Application:
    token = get_settings().bot_token
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", _cmd_start))
    app.add_handler(CommandHandler("help", _cmd_help))
    app.add_handler(CommandHandler("subscribe", _cmd_subscribe))
    return app


def main() -> None:
    log.info("starting bot, long polling")
    create_application().run_polling(bootstrap_retries=-1)


if __name__ == "__main__":
    main()
