"""Tests for timestamp manager utilities."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.core.timestamp_manager import (
    parse_timestamp,
    serialize_timestamp,
    update_last_sync_timestamp,
    get_last_sync_timestamp,
)


class TestParseTimestamp:
    """Test parsing ISO 8601 timestamps to datetime objects."""

    def test_parse_valid_iso8601_timestamp(self):
        """Parse valid ISO 8601 timestamp string."""
        ts_str = "2025-05-17T10:30:45.123456Z"
        result = parse_timestamp(ts_str)
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.tzinfo == timezone.utc

    def test_parse_none_returns_none(self):
        """Return None for None input."""
        result = parse_timestamp(None)
        assert result is None

    def test_parse_invalid_format_returns_none(self):
        """Return None for invalid timestamp format."""
        result = parse_timestamp("not-a-timestamp")
        assert result is None


class TestSerializeTimestamp:
    """Test serializing datetime objects to ISO 8601 strings."""

    def test_serialize_datetime_to_iso8601(self):
        """Serialize datetime to ISO 8601 format."""
        dt = datetime(2025, 5, 17, 10, 30, 45, 123456, tzinfo=timezone.utc)
        result = serialize_timestamp(dt)
        assert result == "2025-05-17T10:30:45.123456+00:00"

    def test_serialize_none_returns_none(self):
        """Return None for None input."""
        result = serialize_timestamp(None)
        assert result is None


class TestGetLastSyncTimestamp:
    """Test retrieving last sync timestamp from database."""

    @pytest.mark.asyncio
    async def test_get_valid_timestamp_from_db(self):
        """Retrieve valid timestamp from database."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = "2025-05-17T10:30:45+00:00"
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        result = await get_last_sync_timestamp(mock_db)
        assert result is not None
        assert isinstance(result, datetime)

    @pytest.mark.asyncio
    async def test_get_none_when_timestamp_not_set(self):
        """Return None when timestamp is not set in database."""
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        result = await get_last_sync_timestamp(mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_timestamp_handles_db_error(self):
        """Handle gracefully if database query fails."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=Exception("DB error"))
        
        result = await get_last_sync_timestamp(mock_db)
        assert result is None


class TestUpdateLastSyncTimestamp:
    """Test updating last sync timestamp in database."""

    @pytest.mark.asyncio
    async def test_update_timestamp_writes_to_db(self):
        """Write new timestamp to database."""
        now = datetime.now(timezone.utc)
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        
        await update_last_sync_timestamp(mock_db, now)
        
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_timestamp_handles_db_error(self):
        """Handle gracefully if write fails."""
        now = datetime.now(timezone.utc)
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=Exception("Write error"))
        mock_db.rollback = AsyncMock()
        
        await update_last_sync_timestamp(mock_db, now)
        
        mock_db.rollback.assert_called()
