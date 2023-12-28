import logging
import os

from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes

from info import bot_welcome, bot_help

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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


def main() -> None:
    load_dotenv()
    bot_key = os.environ.get("BOT_KEY")

    application = Application.builder().token(bot_key).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
