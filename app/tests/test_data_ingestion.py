"""Tests for data ingestion logic, including upsert and session-status handling."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.etl_mapper import map_agent_metric


class TestMapAgentMetricSessionStatus:
    """Test that map_agent_metric correctly sets is_session_opened based on session_status."""
    
    def test_maps_is_session_opened_true_for_open_status(self):
        raw = {
            "sessionId": "sess_1",
            "agentId": "ag_1",
            "openSessions": "1",
        }
        result = map_agent_metric(raw, session_status="open")
        assert result["is_session_open"] is True
    
    def test_maps_is_session_opened_false_for_closed_status(self):
        raw = {
            "sessionId": "sess_1",
            "agentId": "ag_1",
            "openSessions": "0",
            "closedSessions": "1",
        }
        result = map_agent_metric(raw, session_status="closed")
        assert result["is_session_open"] is False
    
    def test_defaults_to_open_status(self):
        raw = {
            "sessionId": "sess_1",
            "agentId": "ag_1",
        }
        result = map_agent_metric(raw)  # No session_status provided
        assert result["is_session_open"] is True


class TestUpsertAgentMetricsBasicUpsert:
    """Test that upsert_agent_metrics correctly builds SQL queries for upsert."""
    
    @pytest.mark.asyncio
    async def test_upsert_calls_execute_with_on_conflict_update(self):
        """
        Verify that upsert_agent_metrics creates proper on_conflict_do_update statements
        for duplicate (session_id, agent_id) pairs.
        """
        mock_db = AsyncMock()
        
        items = [
            {
                "sessionId": "sess_1",
                "chatId": "chat_1",
                "agentId": "ag_1",
                "queue": "support",
                "openSessions": "5",
                "closedSessions": "0",
                "operatorResponses": "10",
            }
        ]
        
        with patch("app.services.data_ingestion.pg_insert") as mock_insert:
            # Mock the insert statement
            mock_stmt = MagicMock()
            mock_insert.return_value.values.return_value.on_conflict_do_update.return_value = mock_stmt
            
            from app.services.data_ingestion import upsert_agent_metrics
            count = await upsert_agent_metrics(mock_db, items, session_status="open")
            
            assert count == 1
            # Verify execute was called
            assert mock_db.execute.called
            # Verify commit was called
            assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_upsert_with_closed_status_first_updates_all_sessions(self):
        """
        Verify that when session_status='closed', the code first executes
        an UPDATE query to mark all records with matching session_ids as closed.
        """
        mock_db = AsyncMock()
        
        items = [
            {
                "sessionId": "sess_1",
                "agentId": "ag_b",
                "closedSessions": "1",
            },
            {
                "sessionId": "sess_2",
                "agentId": "ag_a",
                "closedSessions": "1",
            },
        ]
        
        with patch("app.services.data_ingestion.pg_insert") as mock_insert:
            mock_stmt = MagicMock()
            mock_insert.return_value.values.return_value.on_conflict_do_update.return_value = mock_stmt
            
            from app.services.data_ingestion import upsert_agent_metrics
            count = await upsert_agent_metrics(mock_db, items, session_status="closed")
            
            assert count == 2
            # When closed status, execute should be called multiple times:
            # 1. For UPDATE query to mark sessions as closed
            # 2. For each INSERT...ON CONFLICT
            assert mock_db.execute.call_count >= 3


class TestUpsertAgentMetricsSessionStatusHandling:
    """Test that upsert_agent_metrics correctly handles session status transitions."""
    
    @pytest.mark.asyncio
    async def test_closed_status_triggers_update_query(self):
        """
        Verify that when closing sessions, an UPDATE query is executed
        before the upsert, to mark all related sessions as closed.
        """
        mock_db = AsyncMock()
        
        # Simulate a closed session arriving
        items = [
            {
                "sessionId": "sess_1",
                "agentId": "ag_b",
                "closedSessions": "1",
            }
        ]
        
        with patch("app.services.data_ingestion.pg_insert") as mock_insert:
            mock_stmt = MagicMock()
            mock_insert.return_value.values.return_value.on_conflict_do_update.return_value = mock_stmt
            
            from app.services.data_ingestion import upsert_agent_metrics
            
            await upsert_agent_metrics(mock_db, items, session_status="closed")
            
            # Execute should have been called at least twice:
            # 1. For UPDATE query to mark all sessions as closed
            # 2. For the upsert INSERT...ON CONFLICT
            assert mock_db.execute.call_count >= 2
            # Verify commit was called
            assert mock_db.commit.called


class TestMapAgentMetricSessionStatusTransitions:
    """Test session status transitions and edge cases."""
    
    def test_open_status_with_updated_metrics(self):
        """Verify open sessions preserve all metric data."""
        raw = {
            "sessionId": "sess_1",
            "agentId": "ag_1",
            "queue": "support",
            "openSessions": "5",
            "closedSessions": "0",
            "operatorResponses": "12",
            "avgResponseTime": "1500",
        }
        result = map_agent_metric(raw, session_status="open")
        
        assert result["is_session_open"] is True
        assert result["openSessions"] == 5
        assert result["closedSessions"] == 0
        assert result["total_agent_responses"] == 12
        assert result["avg_agent_response_time"] == 1500.0
    
    def test_closed_status_with_final_metrics(self):
        """Verify closed sessions properly record final state."""
        raw = {
            "sessionId": "sess_1",
            "agentId": "ag_b",
            "queue": "sales",
            "openSessions": "0",
            "closedSessions": "1",
            "operatorResponses": "8",
            "closedTime": "2025-01-15T10:30:00.000Z",
        }
        result = map_agent_metric(raw, session_status="closed")
        
        assert result["is_session_open"] is False
        assert result["closedSessions"] == 1
        assert result["total_agent_responses"] == 8
        assert result["closed_at"] is not None



