"""
Module: contact_form

This module defines an asynchronous web API endpoint for handling form input related to rapid notifications.

Endpoints:
    - POST /RapidNotify: Receive and process rapid notification form input.

Usage:
    1. Define a FastAPI application.
    2. Import and include this module in the application.

Endpoint Function:
    - register_form_input(data: FormInput): Handles POST requests to the /RapidNotify endpoint.

Functions:
    - _get_user_data(api_key: str): Retrieve existing user data using the provided API key.
    - _send_telegram_message(url: str): Send a Telegram message using the specified URL.

Exceptions:
    - HTTPException: Raised in case of API or Telegram-related errors, providing appropriate status codes and details.

"""
import requests
from config.config import Config
from fastapi import APIRouter, HTTPException
from models.form import FormClass
from schemas.form import FormInput

from .utils import join_dict_values

contact_form = APIRouter()


TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"


@contact_form.post("/RapidNotify")
async def register_form_input(data: FormInput):
    """
    Handles POST requests to the /RapidNotify endpoint for rapid notification form input.

    Args:
        data (FormInput): The input data received from the form.

    Returns:
        str: The text response from the Telegram API after sending the notification.

    Raises:
        HTTPException: Raised in case of API or Telegram-related errors, providing appropriate status codes and details.
    """

    def _get_user_data(api_key: str):
        """
        Retrieve existing user data using the provided API key.

        Args:
            api_key (str): The API key associated with the user.

        Returns:
            dict: The existing user data.

        Raises:
            HTTPException: Raised if there's an error retrieving user data.
        """
        form_instance = FormClass()
        try:
            return form_instance.get(api_key)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve existing user data: {e}"
            ) from e

    def _send_telegram_message(url: str):
        """
        Send a Telegram message using the specified URL.

        Args:
            url (str): The URL for sending the Telegram message.

        Returns:
            requests.Response: The response from the Telegram API.

        Raises:
            HTTPException: Raised if there's an error sending the Telegram message.
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to send Telegram message: {e}"
            ) from e

    try:
        user_dict = data.model_dump(exclude_unset=True)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid filter parameter: {e}"
        ) from e

    api_key = user_dict["api_key"]

    try:
        response = _get_user_data(api_key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve existing user data: {e}"
        ) from e

    if not response:
        return {
            "status": "error",
            "message": "Invalid API key. Please provide a valid API key.",
        }

    uuid = response[0]["_id"]
    message = join_dict_values(user_dict["data"])

    telegram_url = TELEGRAM_API_URL.format(Config.BOT_KEY, uuid, message)
    _send_telegram_message(telegram_url)

    return {"status": "success", "message": "Notification sent successfully."}
