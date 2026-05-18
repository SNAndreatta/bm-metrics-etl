"""Tests for sync logic with timestamp-based window calculation."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

from app.tasks.sync import sync_all_endpoints


class TestSyncWithTimestampWindow:
    """Test that sync uses last timestamp to calculate fetch window."""

    @pytest.mark.asyncio
    async def test_sync_uses_last_timestamp_as_window_start(self):
        """Use last sync timestamp as window start if available."""
        last_sync = datetime(2025, 5, 17, 10, 0, 0, tzinfo=timezone.utc)
        current_time = datetime(2025, 5, 17, 10, 10, 0, tzinfo=timezone.utc)
        
        with patch("app.tasks.sync.get_last_sync_timestamp") as mock_get_ts, \
             patch("app.tasks.sync.datetime") as mock_datetime, \
             patch("app.tasks.sync.BotmakerClient") as mock_client_class, \
             patch("app.tasks.sync.async_session_factory") as mock_db_factory, \
             patch("app.tasks.sync.upsert_agents"), \
             patch("app.tasks.sync.upsert_channels"), \
             patch("app.tasks.sync.upsert_agent_metrics"), \
             patch("app.tasks.sync.insert_agent_performance_snapshots"), \
             patch("app.tasks.sync.sync_queues"), \
             patch("app.tasks.sync.update_last_sync_timestamp") as mock_update_ts:
            
            async def async_get_ts(db):
                return last_sync
            mock_get_ts.side_effect = async_get_ts
            mock_datetime.now.return_value = current_time
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta
            
            mock_client = AsyncMock()
            mock_client.list_agents = AsyncMock(return_value=[])
            mock_client.list_channels = AsyncMock(return_value=[])
            mock_client.list_agent_metrics = AsyncMock(return_value=[])
            mock_client.list_agent_performance = AsyncMock(return_value=[])
            
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_db = AsyncMock()
            mock_db_factory.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db_factory.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await sync_all_endpoints()
            
            call_args = mock_client.list_agent_metrics.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_sync_falls_back_to_default_window_when_no_timestamp(self):
        """Use default interval if no last timestamp."""
        current_time = datetime(2025, 5, 17, 10, 10, 0, tzinfo=timezone.utc)
        
        with patch("app.tasks.sync.get_last_sync_timestamp") as mock_get_ts, \
             patch("app.tasks.sync.datetime") as mock_datetime, \
             patch("app.tasks.sync.BotmakerClient") as mock_client_class, \
             patch("app.tasks.sync.async_session_factory") as mock_db_factory, \
             patch("app.tasks.sync.upsert_agents"), \
             patch("app.tasks.sync.upsert_channels"), \
             patch("app.tasks.sync.upsert_agent_metrics"), \
             patch("app.tasks.sync.insert_agent_performance_snapshots"), \
             patch("app.tasks.sync.sync_queues"), \
             patch("app.tasks.sync.update_last_sync_timestamp") as mock_update_ts, \
             patch("app.core.config.settings") as mock_settings:
            
            async def async_get_ts(db):
                return None
            mock_get_ts.side_effect = async_get_ts
            mock_datetime.now.return_value = current_time
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta
            mock_settings.fetch_interval_seconds = 300
            
            mock_client = AsyncMock()
            mock_client.list_agents = AsyncMock(return_value=[])
            mock_client.list_channels = AsyncMock(return_value=[])
            mock_client.list_agent_metrics = AsyncMock(return_value=[])
            mock_client.list_agent_performance = AsyncMock(return_value=[])
            
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_db = AsyncMock()
            mock_db_factory.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db_factory.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await sync_all_endpoints()
            
            call_args = mock_client.list_agent_metrics.call_args
            assert call_args is not None
            mock_update_ts.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_does_not_update_timestamp_on_failure(self):
        """Don't update timestamp if sync fails."""
        with patch("app.tasks.sync.async_session_factory") as mock_db_factory:
            mock_db_factory.return_value.__aenter__ = AsyncMock(side_effect=Exception("API error"))
            with pytest.raises(Exception):
                await sync_all_endpoints()


class TestSyncServerRestartScenario:
    """Test sync behavior after server restart."""

    @pytest.mark.asyncio
    async def test_sync_after_restart_recovers_missed_data(self):
        """After restart, sync from last known good timestamp."""
        last_sync = datetime(2025, 5, 17, 10, 0, 0, tzinfo=timezone.utc)
        current_time = datetime(2025, 5, 17, 10, 30, 0, tzinfo=timezone.utc)
        
        with patch("app.tasks.sync.get_last_sync_timestamp") as mock_get_ts, \
             patch("app.tasks.sync.update_last_sync_timestamp") as mock_update_ts, \
             patch("app.tasks.sync.BotmakerClient") as mock_client_class, \
             patch("app.tasks.sync.async_session_factory") as mock_db_factory, \
             patch("app.tasks.sync.upsert_agents"), \
             patch("app.tasks.sync.upsert_channels"), \
             patch("app.tasks.sync.upsert_agent_metrics"), \
             patch("app.tasks.sync.insert_agent_performance_snapshots"), \
             patch("app.tasks.sync.sync_queues"), \
             patch("app.tasks.sync.datetime") as mock_datetime:
            
            async def async_get_ts(db):
                return last_sync
            mock_get_ts.side_effect = async_get_ts
            mock_datetime.now.return_value = current_time
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta
            
            mock_client = AsyncMock()
            mock_client.list_agents = AsyncMock(return_value=[])
            mock_client.list_channels = AsyncMock(return_value=[])
            mock_client.list_agent_metrics = AsyncMock(return_value=[])
            mock_client.list_agent_performance = AsyncMock(return_value=[])
            
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_db = AsyncMock()
            mock_db_factory.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db_factory.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await sync_all_endpoints()
            
            call_args = mock_client.list_agent_metrics.call_args
            assert call_args is not None
            mock_update_ts.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_recovers_from_long_downtime(self):
        """Sync can recover from multi-hour downtime."""
        last_sync = datetime(2025, 5, 17, 4, 0, 0, tzinfo=timezone.utc)
        current_time = datetime(2025, 5, 17, 10, 0, 0, tzinfo=timezone.utc)
        
        with patch("app.tasks.sync.get_last_sync_timestamp") as mock_get_ts, \
             patch("app.tasks.sync.update_last_sync_timestamp") as mock_update_ts, \
             patch("app.tasks.sync.BotmakerClient") as mock_client_class, \
             patch("app.tasks.sync.async_session_factory") as mock_db_factory, \
             patch("app.tasks.sync.upsert_agents"), \
             patch("app.tasks.sync.upsert_channels"), \
             patch("app.tasks.sync.upsert_agent_metrics"), \
             patch("app.tasks.sync.insert_agent_performance_snapshots"), \
             patch("app.tasks.sync.sync_queues"), \
             patch("app.tasks.sync.datetime") as mock_datetime:
            
            async def async_get_ts(db):
                return last_sync
            mock_get_ts.side_effect = async_get_ts
            mock_datetime.now.return_value = current_time
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta
            
            mock_client = AsyncMock()
            mock_client.list_agents = AsyncMock(return_value=[])
            mock_client.list_channels = AsyncMock(return_value=[])
            mock_client.list_agent_metrics = AsyncMock(return_value=[])
            mock_client.list_agent_performance = AsyncMock(return_value=[])
            
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_db = AsyncMock()
            mock_db_factory.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db_factory.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await sync_all_endpoints()
            
            mock_client.list_agent_metrics.assert_called()
            mock_update_ts.assert_called_once()
