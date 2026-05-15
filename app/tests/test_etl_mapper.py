from datetime import datetime

from app.services.etl_mapper import (
    map_agent,
    map_agent_metric,
    map_agent_performance,
    map_channel,
)


class TestMapAgent:
    def test_basic(self):
        raw = {
            "id": "ag_123",
            "name": "Alice",
            "email": "alice@example.com",
            "role": "ADMIN",
            "queues": ["sales", "support"],
        }
        result = map_agent(raw)
        assert result["id"] == "ag_123"
        assert result["name"] == "Alice"
        assert result["email"] == "alice@example.com"
        assert result["role"] == "ADMIN"
        assert result["queues"] == ["sales", "support"]

    def test_missing_fields(self):
        raw = {"id": "ag_456"}
        result = map_agent(raw)
        assert result["name"] is None
        assert result["queues"] == []


class TestMapChannel:
    def test_basic(self):
        raw = {"id": "ch_1", "name": "WhatsApp", "platform": "whatsapp", "active": True}
        result = map_channel(raw)
        assert result["id"] == "ch_1"
        assert result["active"] is True

    def test_default_active(self):
        raw = {"id": "ch_2", "name": "Web"}
        result = map_channel(raw)
        assert result["active"] is False


class TestMapAgentPerformance:
    def test_basic(self):
        raw = {
            "agentEmail": "bob@example.com",
            "agentName": "Bob",
            "role": "AGENT",
            "queue": ["sales"],
            "state": "Busy",
            "checkin": "2025-01-01T08:00:00.000Z",
            "checkout": "2025-01-01T17:00:00.000Z",
        }
        result = map_agent_performance(raw)
        assert result["agent_email"] == "bob@example.com"
        assert result["state"] == "Busy"
        assert isinstance(result["checkin"], datetime)
        assert isinstance(result["checkout"], datetime)
        assert isinstance(result["captured_at"], datetime)
        assert result["queues"] == ["sales"]

    def test_null_dates(self):
        raw = {"agentEmail": "bob@example.com", "state": "Offline"}
        result = map_agent_performance(raw)
        assert result["checkin"] is None
        assert result["checkout"] is None


class TestMapAgentMetric:
    def test_basic(self):
        raw = {
            "sessionId": "sess_1",
            "chatId": "chat_1",
            "agentId": "ag_1",
            "queue": "support",
            "typification": "billing",
            "openSessions": "2",
            "closedSessions": "3",
            "avgAttendingTime": "3358",
            "avgResponseTime": "1500",
        }
        result = map_agent_metric(raw)
        assert result["session_id"] == "sess_1"
        assert result["queue_name"] == "support"
        assert result["openSessions"] == 2
        assert result["closedSessions"] == 3
        assert result["avg_session_attending_time"] == 3358.0
        assert result["avg_agent_response_time"] == 1500.0
        assert isinstance(result["last_updated_at"], datetime)

    def test_string_to_int_conversion(self):
        raw = {
            "sessionId": "sess_2",
            "agentId": "ag_2",
            "operatorResponses": "5",
            "onHold": "1",
            "sessionTransferIn": "0",
        }
        result = map_agent_metric(raw)
        assert result["total_agent_responses"] == 5
        assert result["on_hold_count"] == 1
        assert result["transfers_in"] == 0

    def test_none_fields_default_to_zero(self):
        raw = {"sessionId": "sess_3", "agentId": "ag_3"}
        result = map_agent_metric(raw)
        assert result["openSessions"] == 0
        assert result["total_agent_responses"] == 0
        assert result["avg_session_attending_time"] == 0.0
        assert result["created_at"] is None
        assert result["closed_at"] is None
