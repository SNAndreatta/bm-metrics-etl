class BotmakerAuthError(Exception):
    """Raised on 401 — token invalid or expired."""


class BotmakerRateLimitError(Exception):
    """Raised on 429 — rate limited."""


class BotmakerServerError(Exception):
    """Raised on 5xx — transient server error."""
