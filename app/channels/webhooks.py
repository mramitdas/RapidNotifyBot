"""Slack and Discord incoming-webhook adapters."""

from typing import Any

import httpx

from app.channels.base import SendResult


class SlackAdapter:
    channel_type = "slack"

    def build_payload(self, config: dict[str, Any], message: str) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": message[:39000]}
        if config.get("blocks"):
            payload["blocks"] = config["blocks"]
        return payload

    async def send(
        self,
        config: dict[str, Any],
        user_id: int,
        message: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> SendResult:
        webhook_url = str(config.get("webhook_url", ""))
        if not webhook_url:
            return SendResult(ok=False, detail="missing webhook_url")
        payload = self.build_payload(config, message)
        try:
            return await self._post(webhook_url, payload, client)
        except httpx.HTTPError as exc:
            return SendResult(ok=False, detail=f"http error: {exc}")

    @staticmethod
    async def _post(
        url: str, payload: dict[str, Any], client: httpx.AsyncClient | None
    ) -> SendResult:
        if client is None:
            async with httpx.AsyncClient(timeout=30.0) as own_client:
                resp = await own_client.post(url, json=payload, follow_redirects=False)
        else:
            resp = await client.post(url, json=payload, follow_redirects=False)
        if resp.status_code == 200:
            return SendResult(ok=True, detail="sent")
        return SendResult(ok=False, detail=f"slack webhook {resp.status_code}")


class DiscordAdapter:
    channel_type = "discord"

    def build_payload(self, config: dict[str, Any], message: str) -> dict[str, Any]:
        return {
            "content": message[:2000],
            "username": config.get("username", "RapidNotify"),
        }

    async def send(
        self,
        config: dict[str, Any],
        user_id: int,
        message: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> SendResult:
        webhook_url = str(config.get("webhook_url", ""))
        if not webhook_url:
            return SendResult(ok=False, detail="missing webhook_url")
        payload = self.build_payload(config, message)
        try:
            if client is None:
                async with httpx.AsyncClient(timeout=30.0) as own_client:
                    resp = await own_client.post(
                        webhook_url, json=payload, follow_redirects=False
                    )
            else:
                resp = await client.post(
                    webhook_url, json=payload, follow_redirects=False
                )
            if resp.status_code in (200, 204):
                return SendResult(ok=True, detail="sent")
            return SendResult(ok=False, detail=f"discord webhook {resp.status_code}")
        except httpx.HTTPError as exc:
            return SendResult(ok=False, detail=f"http error: {exc}")


slack_adapter = SlackAdapter()
discord_adapter = DiscordAdapter()
