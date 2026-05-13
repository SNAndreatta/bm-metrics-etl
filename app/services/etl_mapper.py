from datetime import datetime, timezone
from typing import Any


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def map_agent(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "email": item.get("email"),
        "role": item.get("role"),
        "queues": item.get("queues") or [],
        "raw_json": item,
    }


def map_channel(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "platform": item.get("platform"),
        "active": item.get("active", False),
        "raw_json": item,
    }


def map_agent_performance(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_email": item.get("agentEmail"),
        "agent_name": item.get("agentName"),
        "role": item.get("role"),
        "queues": item.get("queue") or [],
        "state": item.get("state"),
        "checkin": _parse_dt(item.get("checkin")),
        "checkout": _parse_dt(item.get("checkout")),
        "captured_at": datetime.now(timezone.utc),
        "raw_json": item,
    }


def map_agent_metric(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "session_id": item.get("sessionId"),
        "chat_id": item.get("chatId"),
        "agent_id": item.get("agentId"),
        "queue_name": item.get("queue"),
        "typification": item.get("typification"),
        "openSessions": _safe_int(item.get("openSessions")),
        "closedSessions": _safe_int(item.get("closedSessions")),
        "total_agent_responses": _safe_int(item.get("operatorResponses")),
        "on_hold_count": _safe_int(item.get("onHold")),
        "transfers_in": _safe_int(item.get("sessionTransferIn")),
        "transfers_out": _safe_int(item.get("sessionTransferOut")),
        "transfers_out_no_messages": _safe_int(item.get("sessionTransferOutNoMessages")),
        "closed_without_messages": _safe_int(item.get("closedWithNoMessages")),
        "timeout_no_messages": _safe_int(item.get("timeoutNoMessages")),
        "agent_timeout_count": _safe_int(item.get("agentTimeout")),
        "user_timeout_count": _safe_int(item.get("userTimeout")),
        "general_session_timeout": _safe_int(item.get("sessionTimeout")),
        "avg_session_attending_time": _safe_float(item.get("avgAttendingTime")),
        "avg_agent_response_time": _safe_float(item.get("avgResponseTime")),
        "total_agent_reaction_time": _safe_float(item.get("opResponseTime")),
        "wait_time_in_queue": _safe_float(item.get("fromQueueAsignToOpAssigned")),
        "wait_time_total_to_first_response": _safe_float(item.get("fromQueueAsignToOpFirstResponse")),
        "agent_reaction_time_to_first_message": _safe_float(item.get("fromOpAssignedToOpFirstResponse")),
        "total_duration_from_start_to_first_response": _safe_float(item.get("fromSessionStartToOpFirstResponse")),
        "total_duration_from_queue_to_close": _safe_float(item.get("fromQueueAsignToSessionClosed")),
        "agent_active_duration_to_close": _safe_float(item.get("fromOpAssignationToSessionClosed")),
        "created_at": _parse_dt(item.get("sessionCreationTime")),
        "closed_at": _parse_dt(item.get("closedTime")),
        "last_updated_at": datetime.now(timezone.utc),
        "raw_json": item,
    }
