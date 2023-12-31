"""
rapidNotifyBot Module

This module provides the necessary components for a Telegram bot application. It includes
functionality for handling commands such as /start, /help, and /subscribe. The bot interacts
with a MongoDB database for user subscriptions and retrieves configuration settings from
environment variables using the `Config` class.

Module Components:
- Logging: Configures logging for the bot with INFO level.
- UUID: Utilizes the `uuid` module for generating unique identifiers.
- Typing: Defines optional and tuple types for type hints.
- Telegram: Imports necessary classes and constants from the `telegram` library.
- Telegram.ext: Imports `Application`, `CommandHandler`, and `ContextTypes` from the
  `telegram.ext` module.

Database Interaction:
- Imports the `DataBase` class and related configurations from the `app.db.mongo` module.
- Initializes a `db` instance for database interactions.
- Defines the schema for the `rapidBotDB` (MongoDB) containing database and table names.

Bot Functions:
- `bot_help`, `bot_subscribe`, and `bot_welcome`: Functions providing formatted messages
  for user interaction.

Configuration:
- Retrieves bot key, database URL, database name, and table name from environment variables
  using the `Config` class, which loads values from environment variables.
"""
import logging
import uuid
from typing import Optional, Tuple

from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config.config import Config
from app.db.mongo import (DataBase, MongoDbClientConfig, QueryDataInput,
                          UploadDataInput)

from .info import bot_help as bot_help_msg
from .info import bot_subscribe, bot_welcome

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rapidNotifyBot.log", mode="a"),
        logging.StreamHandler(),
    ],
)
db = DataBase(MongoDbClientConfig(**{"db_url": Config.DB_URL}))
rapidBotDB = {"db_name": Config.DB_NAME, "table_name": Config.TABLE_NAME}

logger = logging.getLogger("rapidNotifyBot")

db = DataBase(MongoDbClientConfig(**{"db_url": Config.DB_URL}))
rapidBotDB = {"db_name": Config.DB_NAME, "table_name": Config.TABLE_NAME}


async def common_args(update: Update) -> Tuple[int, str, Optional[str]]:
    """
    Extracts common user information from a Telegram update in a private chat.

    Parameters:
    - update (Update): The Telegram update object.

    Returns:
    Tuple[int, str, Optional[str]]: A tuple containing user information.
        - int: User ID.
        - str: User's first name.
        - Optional[str]: User's username (or None if not available).
    """
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        name = update.message.from_user.first_name
        username = update.message.from_user.username

        return user_id, name, username


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command in Telegram. Sends a welcome message in private chats.

    Parameters:
    - update (Update): The Telegram update object.
    - context (ContextTypes.DEFAULT_TYPE): The Telegram context object.

    Returns:
    None

    Raises:
    Exception: If an error occurs during the execution of the function.
    """
    # Extract common user information
    _, name, _ = await common_args(update)

    # Determine the chat type (group or private)
    chat_type = update.message.chat.type

    if chat_type == "private":
        try:
            # Typing Action
            await context.bot.send_chat_action(
                update.effective_chat.id, action=constants.ChatAction.TYPING
            )

            # User welcome message
            await update.message.reply_text(
                text=bot_welcome(name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        # Handle the case if the user stops the bot
        except Exception as e:
            logger.error(e)


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /help command in Telegram. Sends a help message in private chats.

    Parameters:
    - update (Update): The Telegram update object.
    - context (ContextTypes.DEFAULT_TYPE): The Telegram context object.

    Returns:
    None

    Raises:
    Exception: If an error occurs during the execution of the function.
    """
    # Extract common user information
    _, name, _ = await common_args(update)

    # Determine the chat type (group or private)
    chat_type = update.message.chat.type

    if chat_type == "private":
        try:
            # Typing Action
            await context.bot.send_chat_action(
                update.effective_chat.id, action=constants.ChatAction.TYPING
            )

            # User help message
            await update.message.reply_text(
                text=bot_help_msg(name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        # Handle the case if the user stops the bot
        except Exception as e:
            logger.error(e)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /subscribe command in Telegram. Manages user subscriptions in private chats.

    Parameters:
    - update (Update): The Telegram update object.
    - context (ContextTypes.DEFAULT_TYPE): The Telegram context object.

    Returns:
    None

    Raises:
    Exception: If an error occurs during the execution of the function.

    Database:
    This function interacts with a database to check and update user subscriptions.
    It uses the `db` instance to query and update user data. The database schema is expected
    to contain a collection or table named `rapidBotDB`, and the data structure is assumed
    to include at least the following fields:
        - "_id": User ID
        - "api_key": Unique API key for user subscription
    """
    # Extract common user information
    user_id, name, _ = await common_args(update)

    # Determine the chat type (group or private)
    chat_type = update.message.chat.type

    if chat_type == "private":
        try:
            # Prepare data for database query
            data = {"data": {"_id": user_id}}
            data.update(rapidBotDB)

            # Query the database for user subscription
            query_result = db.query(QueryDataInput(**data))

            # If user is not subscribed, generate API key and store in the database
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

            # Send user subscription message
            await update.message.reply_text(
                text=bot_subscribe(name, api_key),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        # Handle the case if an error occurs
        except Exception as e:
            logger.error(e)


def main() -> None:
    """
    Entry point for the Telegram bot application.

    Returns:
    None

    Configuration:
    This function retrieves the bot key from the Config.BOT_KEY attribute.

    Telegram Bot Initialization:
    The function initializes a Telegram bot using the `Application` class from the
    underlying framework. The bot is configured with the retrieved bot key.

    Command Handlers:
    The function adds command handlers for the /start, /help, and /subscribe commands,
    linking them to the corresponding functions: `start`, `help`, and `subscribe`.

    Polling:
    The function starts the bot's polling mechanism with `application.run_polling`,
    allowing the bot to actively listen for incoming updates. The `allowed_updates`
    parameter is set to `Update.ALL_TYPES` to receive updates of all types.
    """
    bot_key = Config.BOT_KEY

    # Initialize the Telegram bot application
    application = Application.builder().token(bot_key).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", bot_help))
    application.add_handler(CommandHandler("subscribe", subscribe))

    # Start bot polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    """
    Main entry point for executing the Telegram bot application.

    The script runs the `main` function to initialize and start the Telegram bot.

    Usage:
    The script is typically executed directly. Ensure that the `main` function contains
    the necessary configuration and command handlers for the bot.
    """
    main()
