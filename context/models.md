# API Models --> PostgreSQL DB

default type: String

## Agent (Agents)
- id (pk)
- name
- email
- role
- **queues** (ARRAY[String]): List of queue names the agent belongs to, from API response.
- raw_json (JSONB)
- created_at (DateTime)
- updated_at (DateTime)

## Queues (dynamically generated)
- name (pk)
- created_at (DateTime)

Populated from unique queue names extracted from Agent.queues arrays on every sync.

## Channel (Channels)
- id (pk)
- name
- platform
- active
- raw_json (JSONB)
- created_at (DateTime)
- updated_at (DateTime)

## AgentPerformanceSnapshot (from List Agents Performance)
- id (BigInt, auto-incremental, pk)
- agent_email (String, indexed)
- agent_name (String)
- role (String)
- **queues** (ARRAY[String]): Queue names from the API response array.
- state (String)
- checkin (DateTime, nullable)
- **checkout (DateTime, nullable)**
- captured_at (DateTime, indexed)
- raw_json (JSONB)

Each 60-second sync appends a new row (append-only, no upsert).

## AgentMetric (from List Agents Metrics)
Upsert key: (session_id, agent_id) — unique constraint enforced at DB level.
- **id** (BigInt, pk, autoincremental)
- **session_id** (String, indexed): The unique identifier for the specific session.
- **chat_id** (String): The identifier for the continuous chat thread.
- **agent_id** (String, FK, indexed): Reference to the assigned agent.
- **queue_name** (String): Name of the department or queue (single string from API).
- **typification** (String, nullable): The category or tag assigned to the session closure.
- **openSessions** (Integer, default 0)
- **closedSessions** (Integer, default 0)
- **total_agent_responses** (Integer, default 0): Total messages sent by the agent (operatorResponses).
- **on_hold_count** (Integer, default 0): Times the session was put on hold.
- **transfers_in** (Integer, default 0): Sessions transferred to this agent/queue.
- **transfers_out** (Integer, default 0): Sessions transferred away from this agent/queue.
- **transfers_out_no_messages** (Integer, default 0): Transfers made without any agent interaction.
- **closed_without_messages** (Integer, default 0): Sessions ended without interaction.
- **timeout_no_messages** (Integer, default 0): Sessions closed due to inactivity without messages.
- **agent_timeout_count** (Integer, default 0): Closures caused by agent inactivity.
- **user_timeout_count** (Integer, default 0): Closures caused by user inactivity.
- **general_session_timeout** (Integer, default 0): Total session-level timeouts.
- **avg_session_attending_time** (Float, default 0.0): Average time spent actively attending (avgAttendingTime).
- **avg_agent_response_time** (Float, default 0.0): General average response time (avgResponseTime).
- **total_agent_reaction_time** (Float, default 0.0): Cumulative time taken for agent responses (opResponseTime).
- **wait_time_in_queue** (Float, default 0.0): Time from user entry to agent assignment (fromQueueAsignToOpAssigned).
- **wait_time_total_to_first_response** (Float, default 0.0): Total user wait time from queue entry to first agent message (fromQueueAsignToOpFirstResponse).
- **agent_reaction_time_to_first_message** (Float, default 0.0): Time from assignment to the first response (fromOpAssignedToOpFirstResponse).
- **total_duration_from_start_to_first_response** (Float, default 0.0): Time from session creation to first response (fromSessionStartToOpFirstResponse).
- **total_duration_from_queue_to_close** (Float, default 0.0): Full session lifecycle from queue entry to closure (fromQueueAsignToSessionClosed).
- **agent_active_duration_to_close** (Float, default 0.0): Time from agent assignment until closure (fromOpAssignationToSessionClosed).
- **created_at** (DateTime, nullable): Original session creation time from Botmaker.
- **closed_at** (DateTime, nullable): Final closure time.
- **last_updated_at** (DateTime): System timestamp of the last fetch.
- raw_json (JSONB)
