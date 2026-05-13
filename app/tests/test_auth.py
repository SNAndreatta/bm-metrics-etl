import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.clients.botmaker_client import _decode_jwt_payload, _token_expired
from app.clients.exceptions import BotmakerAuthError


def _make_jwt(exp: int | None = None) -> str:
    import base64, json

    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).rstrip(b"=").decode()
    payload_data = {"sub": "test"}
    if exp:
        payload_data["exp"] = exp
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).rstrip(b"=").decode()
    sig = base64.urlsafe_b64encode(b"sig").rstrip(b"=").decode()
    return f"{header}.{payload}.{sig}"


class TestDecodeJwt:
    def test_valid_token(self):
        token = _make_jwt(exp=9999999999)
        payload = _decode_jwt_payload(token)
        assert payload is not None
        assert payload["exp"] == 9999999999

    def test_malformed_token(self):
        assert _decode_jwt_payload("not.a.token") is None
        assert _decode_jwt_payload("") is None

    def test_no_exp_claim(self):
        token = _make_jwt()
        payload = _decode_jwt_payload(token)
        assert payload is not None
        assert "exp" not in payload


class TestTokenExpired:
    def test_expired_token(self):
        token = _make_jwt(exp=1)
        assert _token_expired(token) is True

    def test_future_token(self):
        far_future = int(time.time()) + 999999
        token = _make_jwt(exp=far_future)
        assert _token_expired(token) is False

    def test_none_token(self):
        assert _token_expired(None) is True

    def test_empty_token(self):
        assert _token_expired("") is True

    def test_malformed_token(self):
        assert _token_expired("bad.token.here") is True


@pytest.mark.asyncio
async def test_refresh_token_updates_header_and_env():
    from app.clients.botmaker_client import BASE_URL, BotmakerClient

    client = BotmakerClient()
    new_token = "new.jwt.token.here"

    with patch("app.clients.botmaker_client.httpx.AsyncClient") as mock_http_cls:
        mock_http = AsyncMock()
        mock_http.__aenter__.return_value = mock_http
        mock_http_cls.return_value = mock_http

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"accessToken": new_token}
        mock_http.post = AsyncMock(return_value=resp)

        with patch("app.clients.botmaker_client.set_key") as mock_set_key:
            result = await client._refresh_token()
            assert result == new_token
            assert client._token == new_token
            assert client._client.headers["access-token"] == new_token
            mock_set_key.assert_called_once()

            mock_http.post.assert_called_once()
            url = mock_http.post.call_args[0][0]
            assert url == f"{BASE_URL}/auth/credentials"


@pytest.mark.asyncio
async def test_refresh_token_fails_without_credentials():
    from app.clients.botmaker_client import BotmakerClient
    from app.core.config import settings

    client = BotmakerClient()

    with patch.object(settings, "client_id", ""), patch.object(settings, "secret_id", ""):
        with pytest.raises(BotmakerAuthError, match="Missing clientId"):
            await client._refresh_token()


@pytest.mark.asyncio
async def test_401_triggers_refresh_and_retry():
    from app.clients.botmaker_client import BotmakerClient

    client = BotmakerClient()

    with patch.object(client, "_ensure_token", return_value=None), \
         patch.object(client, "_refresh_token", new_callable=AsyncMock) as mock_refresh:
        mock_refresh.return_value = "new.token"

        resp_401 = AsyncMock()
        resp_401.status_code = 401
        resp_200 = AsyncMock()
        resp_200.status_code = 200
        resp_200.json = MagicMock(return_value={"items": [{"id": "1"}]})

        client._client.request = AsyncMock(side_effect=[resp_401, resp_200])

        result = await client._request("GET", "/agents")
        assert result == {"items": [{"id": "1"}]}
        assert mock_refresh.called
