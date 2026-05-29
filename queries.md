# En línea
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "En línea"
FROM latest_per_agent
WHERE state = 'online' AND role = 'OPERATOR';
```

---

# En línea (No disponible)
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "En línea no disponible"
FROM latest_per_agent
WHERE state = 'online_not_available' AND role = 'OPERATOR';
```

---

# Ocupado
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "Ocupado"
FROM latest_per_agent
WHERE state = 'busy' AND role = 'OPERATOR';
```

---

# Break
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "Break"
FROM latest_per_agent
WHERE state = 'break' AND role = 'OPERATOR';
```

---

# Coach
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "Coach"
FROM latest_per_agent
WHERE state = 'coach' AND role = 'OPERATOR';
```

---

# Almorzando
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "Almuerzo"
FROM latest_per_agent
WHERE state = 'lunch' AND role = 'OPERATOR';
```

---

# Desconectado
```SQL
WITH latest_per_agent AS (
    SELECT DISTINCT ON (agent_email)
        agent_email,
        state,
        checkin,
        checkout,
		role
    FROM agent_performance_snapshots
    ORDER BY agent_email, checkin DESC
)

SELECT COUNT(*) AS "Offline"
FROM latest_per_agent
WHERE checkout IS NOT NULL AND role = 'OPERATOR';
```

---

# Conversaciones en curso
```SQL
SELECT
    SUM(agent_metrics."openSessions") AS "Conversaciones en curso"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Conversaciones cerradas
```SQL
SELECT
    SUM(agent_metrics."closedSessions") AS "Conversaciones cerradas"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Duración media de sesión
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Duración media de sesión"
FROM (
    SELECT AVG(avg_session_attending_time)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Espera en cola
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Espera en cola"
FROM (
    SELECT AVG(wait_time_in_queue)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Espera en cola + Espera agente
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Espera en cola + agente"
FROM (
    SELECT AVG(wait_time_total_to_first_response)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Tiempo promedio primer respuesta
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Tiempo promedio primera respuesta"
FROM (
    SELECT AVG(agent_reaction_time_to_first_message)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Duración promedio de atención
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Duración promedio de atención"
FROM (
    SELECT AVG(agent_active_duration_to_close)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Tiempo promedio de respuesta
```SQL
SELECT
    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS "Tiempo promedio de respuesta"
FROM (
    SELECT AVG(avg_agent_response_time)::bigint AS avg_seconds
    FROM agent_metrics
    WHERE created_at >= CURRENT_DATE
) t;
```

---

# Cantidad promedio de respuestas
```SQL
SELECT
    ROUND(AVG(total_agent_responses)) AS "Cantidad promedio de respuestas"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Usuarios esperando respuesta
```SQL
SELECT
    COUNT(*) AS "Usuarios esperando respuesta"
FROM agent_metrics
WHERE is_session_open = true
AND (
    agent_reaction_time_to_first_message IS NULL
    OR agent_reaction_time_to_first_message = 0
);
```

---

# Transferencias totales
```SQL
SELECT
    SUM(transfers_in + transfers_out) AS "Transferencias"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Transferencias sin mensajes
```SQL
SELECT
    SUM(transfers_out_no_messages) AS "Transferencias sin mensajes"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Sesiones cerradas sin mensajes
```SQL
SELECT
    SUM(closed_without_messages) AS "Cerradas sin mensajes"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Timeouts de agente
```SQL
SELECT
    SUM(agent_timeout_count) AS "Timeouts agente"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Timeouts de usuario
```SQL
SELECT
    SUM(user_timeout_count) AS "Timeouts usuario"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Timeouts generales
```SQL
SELECT
    SUM(general_session_timeout) AS "Timeouts generales"
FROM agent_metrics
WHERE created_at >= CURRENT_DATE;
```

---

# Sesiones abiertas actuales
```SQL
SELECT
    COUNT(*) AS "Sesiones abiertas"
FROM agent_metrics
WHERE is_session_open = true;
```

---

# Métricas por cola
```SQL
SELECT
    queue_name AS "Cola",

    SUM(agent_metrics."openSessions") AS "Conv. en curso",

    SUM(agent_metrics."closedSessions") AS "Conv. cerradas",

    COUNT(
        CASE
            WHEN is_session_open = true
            THEN 1
        END
    ) AS "Usuarios esperando respuesta",

    AVG(avg_agent_response_time) AS "Tiempo medio de respuesta",

    SUM(total_agent_responses) AS "Cantidad de respuestas"

FROM agent_metrics

WHERE created_at >= CURRENT_DATE

GROUP BY queue_name

ORDER BY "Conv. en curso" DESC;
```

---

# Top agentes por respuestas
```SQL
SELECT
    a.name AS agente,
    SUM(am.total_agent_responses) AS respuestas
FROM agent_metrics am
JOIN agents a
    ON am.agent_id = a.id
WHERE am.created_at >= CURRENT_DATE
GROUP BY a.name
ORDER BY respuestas DESC
LIMIT 10;
```

---

# Top agentes más lentos
```SQL
SELECT
    agente,

    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS tiempo_respuesta

FROM (
    SELECT
        a.name AS agente,
        AVG(am.avg_agent_response_time)::bigint AS avg_seconds

    FROM agent_metrics am

    JOIN agents a
        ON am.agent_id = a.id

    WHERE am.created_at >= CURRENT_DATE

    GROUP BY a.name
) t

ORDER BY avg_seconds DESC

LIMIT 10;
```

---

# Colas más lentas
```SQL
SELECT
    queue_name,

    TRIM(
        CONCAT(
            CASE
                WHEN avg_seconds >= 3600
                THEN FLOOR(avg_seconds / 3600)::int || 'h '
                ELSE ''
            END,

            CASE
                WHEN FLOOR((avg_seconds % 3600) / 60) > 0
                THEN FLOOR((avg_seconds % 3600) / 60)::int || 'm '
                ELSE ''
            END,

            CASE
                WHEN FLOOR(avg_seconds % 60) > 0
                     OR avg_seconds = 0
                THEN FLOOR(avg_seconds % 60)::int || 's'
                ELSE ''
            END
        )
    ) AS tiempo_respuesta

FROM (
    SELECT
        queue_name,
        AVG(avg_agent_response_time)::bigint AS avg_seconds

    FROM agent_metrics

    WHERE created_at >= CURRENT_DATE

    GROUP BY queue_name
) t

ORDER BY avg_seconds DESC;
```

---

# Volumen de conversaciones por hora
```SQL
SELECT
    TO_CHAR(
        DATE_TRUNC('hour', created_at),
        'HH24:00'
    ) AS hora,

    COUNT(*) AS conversaciones

FROM agent_metrics

WHERE created_at >= CURRENT_DATE

GROUP BY 1

ORDER BY 1;
```