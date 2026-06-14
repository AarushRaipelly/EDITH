import time
from typing import Dict, List

class EdithRateLimiter:
    def __init__(self, limit_per_minute: int = 10) -> None:
        self.limit_per_minute = limit_per_minute
        # Maps user identifier to timestamps of requests
        self.request_history: Dict[str, List[float]] = {}

    def is_allowed(self, user_id: str, is_boss: bool) -> bool:
        """Determines if the request is permitted. Boss is bypass-gated, unrecognized voices are rate limited."""
        if is_boss:
            return True

        now = time.time()
        if user_id not in self.request_history:
            self.request_history[user_id] = []

        # Retain only the last 60 seconds of history
        self.request_history[user_id] = [t for t in self.request_history[user_id] if now - t < 60.0]

        if len(self.request_history[user_id]) >= self.limit_per_minute:
            return False

        self.request_history[user_id].append(now)
        return True
