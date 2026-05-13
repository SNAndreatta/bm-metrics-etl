from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_botmaker_client():
    """Patch BotmakerClient so no real HTTP calls happen."""
    with patch("app.clients.botmaker_client.BotmakerClient", autospec=True) as mock:
        instance = mock.return_value
        instance.__aenter__.return_value = instance

        instance.list_agents = AsyncMock(return_value=[])
        instance.list_channels = AsyncMock(return_value=[])
        instance.list_agent_metrics = AsyncMock(return_value=[])
        instance.list_agent_performance = AsyncMock(return_value=[])

        yield instance
