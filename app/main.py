"""RapidNotify v2 API application."""

import structlog
from fastapi import FastAPI

from app.api.routes.v1 import api_router

log = structlog.get_logger("app")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RapidNotify",
        version="2.0.0",
        description=(
            "Self-hostable notification relay. Subscribe via the Telegram bot, "
            "then POST messages to /api/v1/notify."
        ),
        docs_url="/",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
