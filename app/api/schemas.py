"""Request/response schemas for the v1 API."""

from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

ChannelName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_lower=True),
]

SUPPORTED_CHANNELS = ("telegram", "slack", "discord", "webhook")


class NotifyRequest(BaseModel):
    channel: ChannelName
    data: Annotated[
        dict[str, Any], Field(min_length=1, description="Arbitrary key/values to send")
    ]


class NotifyResponse(BaseModel):
    status: str
    channel: str
    recipients: int


class MeResponse(BaseModel):
    id: int
    telegram_user_id: int
    rate_limit_tier: str
    channels: list[str]


class MessageResponse(BaseModel):
    status: str
    detail: str | None = None
