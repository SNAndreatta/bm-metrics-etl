import asyncio
import base64
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator

import httpx
from dotenv import set_key

from app.clients.exceptions import BotmakerAuthError, BotmakerRateLimitError, BotmakerServerError
from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.botmaker.com/v2.0"
MAX_RETRIES = 3
BASE_DELAY = 1.0
MAX_PAGES = 1000
ENV_PATH = Path(settings.model_config.get("env_file", ".env")).resolve()  # type: ignore[arg-type]


def _decode_jwt_payload(token: str) -> dict[str, Any] | None:
    try:
        payload_b64 = token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        return json.loads(base64.b64decode(payload_b64))
    except (IndexError, ValueError, json.JSONDecodeError):
        return None


def _token_expired(token: str | None) -> bool:
    if not token:
        return True
    payload = _decode_jwt_payload(token)
    if not payload:
        return True
    exp = payload.get("exp", 0)
    if not exp:
        return False
    return datetime.now(timezone.utc).timestamp() > exp - 60


class BotmakerClient:
    _token_lock = asyncio.Lock()

    def __init__(self) -> None:
        self._token = settings.botmaker_access_token
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={
                "access-token": self._token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BotmakerClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _refresh_token(self) -> str:
        if not settings.client_id or not settings.secret_id or not settings.refresh_token:
            raise BotmakerAuthError("Missing clientId, secretId, or refreshToken in .env")

        logger.info("Refreshing Botmaker API token...")
        payload = {
            "clientId": settings.client_id,
            "secretId": settings.secret_id,
            "refreshToken": settings.refresh_token,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "access-token": self._token,
        }

        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(f"{BASE_URL}/auth/credentials", json=payload, headers=headers)

        if resp.status_code != 200:
            raise BotmakerAuthError(
                f"Token refresh failed ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        new_token = data.get("accessToken")
        if not new_token:
            raise BotmakerAuthError("Token refresh response missing accessToken")

        self._token = new_token
        self._client.headers["access-token"] = new_token

        try:
            set_key(str(ENV_PATH), "BOTMAKER_ACCESS_TOKEN", new_token)
        except OSError:
            logger.warning("Could not update .env with new token")

        logger.info("Botmaker API token refreshed successfully")
        return new_token

    async def _ensure_token(self) -> None:
        async with self._token_lock:
            if _token_expired(self._token):
                await self._refresh_token()

    async def _request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        await self._ensure_token()

        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = await self._client.request(method, path, params=params)
            except httpx.TimeoutException as exc:
                if attempt < MAX_RETRIES:
                    wait = BASE_DELAY * (2 ** attempt)
                    logger.warning("Timeout on %s, retrying in %.1fs (attempt %d/%d)", path, wait, attempt + 1, MAX_RETRIES)
                    await asyncio.sleep(wait)
                    continue
                raise BotmakerServerError(f"Timeout after {MAX_RETRIES} retries: {exc}") from exc

            if resp.status_code == 401:
                async with self._token_lock:
                    await self._refresh_token()
                    resp = await self._client.request(method, path, params=params)
                    if resp.status_code == 401:
                        raise BotmakerAuthError("Token invalid or expired after refresh")

            if resp.status_code == 429:
                raise BotmakerRateLimitError("Rate limited")
            if resp.status_code >= 500:
                if attempt < MAX_RETRIES:
                    wait = BASE_DELAY * (2 ** attempt)
                    logger.warning("Server error %s on %s, retrying in %.1fs", resp.status_code, path, wait)
                    await asyncio.sleep(wait)
                    continue
                raise BotmakerServerError(f"Server error {resp.status_code} after {MAX_RETRIES} retries")

            resp.raise_for_status()
            return resp.json()

        raise BotmakerServerError("Unexpected retry exhaustion")

    async def _paginated_get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        current_path = path
        current_params = params
        page_count = 0

        while True:
            data = await self._request("GET", current_path, params=current_params)
            items = data.get("items", data) if isinstance(data, dict) else data

            if isinstance(items, list):
                yield items

            page_count += 1
            if page_count >= MAX_PAGES:
                logger.warning("Reached max page limit (%s) on %s", MAX_PAGES, path)
                break

            next_page = data.get("nextPage") if isinstance(data, dict) else None
            if not next_page:
                break
            
            current_path = next_page
            current_params = None

    async def list_agents(self) -> list[dict[str, Any]]:
        all_items: list[dict[str, Any]] = []
        async for batch in self._paginated_get("/agents"):
            all_items.extend(batch)
        return all_items

    async def list_channels(
        self, active: bool | None = None, platform: str | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = str(active).lower()
        if platform:
            params["platform"] = platform

        all_items: list[dict[str, Any]] = []
        async for batch in self._paginated_get("/channels", params=params):
            all_items.extend(batch)
        return all_items

    async def list_agent_metrics(
        self, from_dt: datetime | None = None, to_dt: datetime | None = None,
        session_status: str = "open",
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"session-status": session_status}
        if from_dt:
            params["from"] = from_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if to_dt:
            params["to"] = to_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        all_items: list[dict[str, Any]] = []
        async for batch in self._paginated_get("/dashboards/agent-metrics", params=params):
            all_items.extend(batch)
        return all_items

    async def list_agent_performance(
        self, from_dt: datetime | None = None, to_dt: datetime | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if from_dt:
            params["from"] = from_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if to_dt:
            params["to"] = to_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        all_items: list[dict[str, Any]] = []
        async for batch in self._paginated_get("/dashboards/agent-performance", params=params):
            all_items.extend(batch)
        return all_items
