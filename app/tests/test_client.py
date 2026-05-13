from unittest.mock import AsyncMock, patch

import pytest

from app.clients.botmaker_client import BotmakerClient


@pytest.fixture
def client():
    return BotmakerClient()


@pytest.mark.asyncio
async def test_list_agents_returns_items(client):
    mock_resp = {"items": [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_resp

        result = await client.list_agents()
        assert len(result) == 2
        assert result[0]["id"] == "1"


@pytest.mark.asyncio
async def test_list_agents_handles_pagination(client):
    page1 = {"nextPage": "token2", "items": [{"id": "1"}]}
    page2 = {"nextPage": None, "items": [{"id": "2"}]}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [page1, page2]

        result = await client.list_agents()
        assert len(result) == 2
        assert mock_request.call_count == 2


@pytest.mark.asyncio
async def test_list_channels_filters_active(client):
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"items": []}

        await client.list_channels(active=True)
        _, kwargs = mock_request.call_args
        params = kwargs.get("params", {})
        assert params.get("active") == "true"


@pytest.mark.asyncio
async def test_list_channels_non_paginated(client):
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"items": [{"id": "ch_1"}]}

        result = await client.list_channels()
        assert result == [{"id": "ch_1"}]


@pytest.mark.asyncio
async def test_list_agent_metrics_passes_dates(client):
    from datetime import datetime, timezone

    dt_from = datetime(2025, 1, 1, tzinfo=timezone.utc)
    dt_to = datetime(2025, 1, 2, tzinfo=timezone.utc)

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"items": []}

        await client.list_agent_metrics(from_dt=dt_from, to_dt=dt_to, session_status="open")
        _, kwargs = mock_request.call_args
        params = kwargs.get("params", {})
        assert "from" in params
        assert "to" in params
        assert params["from"] == "2025-01-01T00:00:00.000Z"
        assert params["session-status"] == "open"


@pytest.mark.asyncio
async def test_client_raises_auth_error(client):
    from app.clients.exceptions import BotmakerAuthError

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = BotmakerAuthError("Token invalid or expired")

        with pytest.raises(BotmakerAuthError):
            await client.list_agents()


@pytest.mark.asyncio
async def test_client_retries_on_5xx(client):
    from app.clients.exceptions import BotmakerServerError

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = BotmakerServerError("Server error")

        with pytest.raises(BotmakerServerError):
            await client.list_agents()


@pytest.mark.asyncio
async def test_list_agent_performance_default_is_last_hour(client):
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"items": []}

        await client.list_agent_performance(from_dt=None, to_dt=None)
        _, kwargs = mock_request.call_args
        params = kwargs.get("params", {})
        assert "from" not in params
        assert "to" not in params
