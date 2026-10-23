"""Generic webhook adapter — POSTs the payload to a user-registered URL.

SSRF-validated at registration time (see app.core.security); sends never
follow redirects.
"""

from typing import Any

import httpx

from app.channels.base import SendResult
from app.core.security import is_ssrf_safe_url


class WebhookAdapter:
    channel_type = "webhook"

    def build_payload(
        self, config: dict[str, Any], user_id: int, message: str
    ) -> dict[str, Any]:
        return {"text": message, "source": config.get("source", "rapidnotify")}

    async def send(
        self,
        config: dict[str, Any],
        user_id: int,
        message: str,
        client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> SendResult:
        target = str(config.get("url", ""))
        if not target:
            return SendResult(ok=False, detail="missing url")
        if not is_ssrf_safe_url(target, allow_http=True):
            return SendResult(ok=False, detail="blocked: unsafe url")
        payload = self.build_payload(config, user_id, message)
        try:
            if client is None:
                async with httpx.AsyncClient(timeout=30.0) as own_client:
                    resp = await own_client.post(
                        target,
                        json=payload,
                        follow_redirects=False,
                        headers=config.get("headers", {}),
                    )
            else:
                resp = await client.post(
                    target,
                    json=payload,
                    follow_redirects=False,
                    headers=config.get("headers", {}),
                )
            if 200 <= resp.status_code < 300:
                return SendResult(ok=True, detail="sent")
            return SendResult(ok=False, detail=f"webhook {resp.status_code}")
        except httpx.HTTPError as exc:
            return SendResult(ok=False, detail=f"http error: {exc}")


adapter = WebhookAdapter()
