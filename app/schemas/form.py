from pydantic import BaseModel


class FormInput(BaseModel):
    """
    Pydantic model representing the input data for notifyme endpoint.

    Attributes:
        bot_key (str): The key identifying the bot.
        data (dict): A dictionary containing the data associated with the bot.

    Example:
        Example usage of this model in a FastAPI endpoint:

        ```python
        from fastapi import FastAPI
        from .your_module import FormInput

        app = FastAPI()

        @app.post("/your_endpoint")
        async def your_endpoint(input_data: FormInput):
            # Access input_data.bot_key and input_data.data here
            return {"message": "Data received successfully"}
        ```
    """

    bot_key: str
    data: dict
