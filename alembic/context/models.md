# agent_metrics

- `id`
- `session_id`
- `chat_id`
- `agent_id`
- `queue_name`
- `typification`
- `openSessions`
- `closedSessions`
- `total_agent_responses`
- `on_hold_count`
- `transfers_in`
- `transfers_out`
- `transfers_out_no_messages`
- `closed_without_messages`
- `timeout_no_messages`
- `agent_timeout_count`
- `user_timeout_count`
- `general_session_timeout`
- `avg_session_attending_time`
- `avg_agent_response_time`
- `total_agent_reaction_time`
- `wait_time_in_queue`
- `wait_time_total_to_first_response`
- `agent_reaction_time_to_first_message`
- `total_duration_from_start_to_first_response`
- `total_duration_from_queue_to_close`
- `agent_active_duration_to_close`
- `created_at`
- `closed_at`
- `is_session_open`
- `last_updated_at`

---

# agent_performance_snapshots

- `id`
- `agent_email`
- `agent_name`
- `role`
- `queues`
- `state`
- `checkin`
- `checkout`
- `captured_at`

---

# agents

- `id`
- `name`
- `email`
- `role`
- `queues`
- `created_at`
- `updated_at`

---

# alembic_version

- `version_num`

---

# channels

- `id`
- `name`
- `platform`
- `active`
- `created_at`
- `updated_at`

---

# queues

- `name`
- `created_at`

---

# sync_metadata

- `key`
- `value`
- `updated_at`

---