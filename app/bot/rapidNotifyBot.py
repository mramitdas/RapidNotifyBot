import logging
import uuid

from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config.config import Config
from app.db.mongo import (DataBase, MongoDbClientConfig, QueryDataInput,
                          UploadDataInput)

from .info import bot_help, bot_subscribe, bot_welcome

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
db = DataBase(MongoDbClientConfig(**{"db_url": Config.DB_URL}))
rapidBotDB = {"db_name": Config.DB_NAME, "table_name": Config.TABLE_NAME}


async def common_args(update: Update):
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        name = update.message.from_user.first_name
        username = update.message.from_user.username

        return user_id, name, username


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, name, username = await common_args(update)

    # chat type (group or private)
    chat_type = update.message.chat.type
    if chat_type == "private":
        try:
            # Typing Action
            await context.bot.send_chat_action(
                update.effective_chat.id, action=constants.ChatAction.TYPING
            )
            # User welcome
            await update.message.reply_text(
                text=bot_welcome(name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        # if user stop the bot
        except Exception as e:
            logging.ERROR(e)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, name, username = await common_args(update)

    # chat type (group or private)
    chat_type = update.message.chat.type
    if chat_type == "private":
        try:
            # Typing Action
            await context.bot.send_chat_action(
                update.effective_chat.id, action=constants.ChatAction.TYPING
            )
            # User Help
            await update.message.reply_text(
                text=bot_help(name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logging.ERROR(e)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, name, username = await common_args(update)

    # chat type (group or private)
    chat_type = update.message.chat.type
    if chat_type == "private":
        try:
            data = {"data": {"_id": user_id}}
            data.update(rapidBotDB)
            query_result = db.query(QueryDataInput(**data))
            if not query_result:
                api_key = str(uuid.uuid4())
                data["data"]["api_key"] = api_key
                db.upload(UploadDataInput(**data))
            else:
                api_key = query_result[0]["api_key"]

            # Typing Action
            await context.bot.send_chat_action(
                update.effective_chat.id, action=constants.ChatAction.TYPING
            )
            # User Subscription
            await update.message.reply_text(
                text=bot_subscribe(name, api_key),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logging.ERROR(e)


def main() -> None:
    bot_key = Config.BOT_KEY

    application = Application.builder().token(bot_key).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("subscribe", subscribe))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
