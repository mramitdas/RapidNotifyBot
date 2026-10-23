"""Telegram adapter — direct Bot API sendMessage call (JSON body)."""

from typing import Any

import httpx

from app.channels.base import SendResult


class TelegramAdapter:
    channel_type = "telegram"

    def url_for(self, token: str) -> str:
        return f"https://api.telegram.org/bot{token}/sendMessage"

    def build_payload(
        self, config: dict[str, Any], user_id: int, message: str
    ) -> dict[str, Any]:
        chat_id = int(config.get("chat_id", user_id))
        return {"chat_id": chat_id, "text": message[:4096]}

    async def send(
        self,
        config: dict[str, Any],
        user_id: int,
        message: str,
        token: str = "",
        client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> SendResult:
        payload = self.build_payload(config, user_id, message)
        try:
            if client is None:
                async with httpx.AsyncClient(timeout=30.0) as own_client:
                    resp = await own_client.post(
                        self.url_for(token), json=payload, follow_redirects=False
                    )
            else:
                resp = await client.post(
                    self.url_for(token), json=payload, follow_redirects=False
                )
            if resp.status_code == 200 and resp.json().get("ok"):
                return SendResult(ok=True, detail="sent")
            return SendResult(ok=False, detail=f"telegram api {resp.status_code}")
        except httpx.HTTPError as exc:
            return SendResult(ok=False, detail=f"http error: {exc}")


adapter = TelegramAdapter()
