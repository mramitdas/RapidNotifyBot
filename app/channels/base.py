"""Common channel adapter interface and result types.

Adapters accept extra keyword args (e.g. ``token``, ``client``) and may
ignore those that do not apply.
"""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class SendResult:
    ok: bool
    detail: str


class ChannelAdapter(Protocol):
    """A notification channel must implement send()."""

    channel_type: str

    async def send(
        self,
        config: dict[str, Any],
        user_id: int,
        message: str,
        **kwargs: Any,
    ) -> SendResult: ...
