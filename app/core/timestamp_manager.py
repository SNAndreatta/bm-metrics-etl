"""Timestamp management utilities for sync window tracking."""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

LAST_SYNC_KEY = "last_sync_timestamp"


def parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 timestamp string to datetime object.
    
    Args:
        timestamp_str: ISO 8601 formatted timestamp string (e.g., '2025-05-17T10:30:45Z')
        
    Returns:
        datetime object in UTC timezone, or None if parsing fails
    """
    if not timestamp_str:
        return None
    
    try:
        # Try parsing with fromisoformat (handles most ISO 8601 formats)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        # Ensure UTC timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        logger.debug("Failed to parse timestamp: %s", timestamp_str)
        return None


def serialize_timestamp(dt: Optional[datetime]) -> Optional[str]:
    """
    Serialize datetime object to ISO 8601 string.
    
    Args:
        dt: datetime object to serialize
        
    Returns:
        ISO 8601 formatted timestamp string, or None if input is None
    """
    if dt is None:
        return None
    
    try:
        # Use isoformat to preserve timezone info
        return dt.isoformat()
    except (AttributeError, TypeError):
        logger.debug("Failed to serialize timestamp: %s", dt)
        return None


async def get_last_sync_timestamp(db: AsyncSession) -> Optional[datetime]:
    """
    Retrieve last sync timestamp from database.
    
    Args:
        db: AsyncSession database connection
    
    Returns:
        datetime object of last sync, or None if not set or invalid
    """
    try:
        from app.models.sync_metadata import SyncMetadata
        
        stmt = select(SyncMetadata.value).where(SyncMetadata.key == LAST_SYNC_KEY)
        result = await db.execute(stmt)
        timestamp_str = result.scalar()
        
        if timestamp_str is None:
            return None
        
        return parse_timestamp(timestamp_str)
    except Exception as e:
        logger.error("Error retrieving last sync timestamp from database: %s", e)
        return None


async def update_last_sync_timestamp(db: AsyncSession, dt: datetime) -> None:
    """
    Update last sync timestamp in database.
    
    Args:
        db: AsyncSession database connection
        dt: datetime object to store as last sync timestamp
    """
    try:
        from app.models.sync_metadata import SyncMetadata
        
        timestamp_str = serialize_timestamp(dt)
        if timestamp_str is None:
            logger.error("Failed to serialize timestamp for update")
            return
        
        # Use upsert pattern for reliability
        stmt = (
            insert(SyncMetadata)
            .values(key=LAST_SYNC_KEY, value=timestamp_str)
            .on_conflict_do_update(
                index_elements=[SyncMetadata.key],
                set_={"value": timestamp_str},
            )
        )
        
        await db.execute(stmt)
        await db.commit()
        
        logger.info("Updated last sync timestamp to %s", timestamp_str)
    except Exception as e:
        logger.error("Failed to update last sync timestamp in database: %s", e)
        await db.rollback()
