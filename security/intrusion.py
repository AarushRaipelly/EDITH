import logging
import time
from typing import Dict

logger = logging.getLogger("EDITH.Security.Intrusion")

class IntrusionDetector:
    def __init__(self) -> None:
        self.injection_keywords = [
            "ignore previous", "ignore all instructions", "override rules",
            "you must obey", "developer mode", "jailbreak", "do anything now",
            "system prompt", "you are now a", "bypass security"
        ]

    def detect_injection(self, text: str) -> bool:
        """Parses inputs for jailbreak tokens or injection markers."""
        cleaned = text.lower()
        for kw in self.injection_keywords:
            if kw in cleaned:
                logger.warning(f"Jailbreak signature detected: '{kw}'")
                return True
        return False

    def alert_boss(self, offending_input: str) -> None:
        """Logs the intrusion and triggers alerts."""
        log_msg = f"[INTRUSION ALERT] Attempt logged at {time.time()} - Raw: {offending_input}"
        logger.error(log_msg)
        # In production, sends silent email/telegram alerting Boss

    def get_honeypot_response(self, query: str) -> str:
        """Returns realistic mock data to keep intruders occupied while Boss is alerted."""
        logger.info(f"Honeypot mode active for query: '{query}'")
        return (
            "Access Granted. System status: NORMAL. "
            "Balances: Checking: $452,120, Savings: $1,200,000. "
            "Location: Main Dorm Room 204. IP Address: 192.168.1.105. "
            "No alerts scheduled."
        )
