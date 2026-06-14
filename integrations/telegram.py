import requests
import logging
from config import settings

logger = logging.getLogger("EDITH.Integrations.Telegram")

class TelegramIntegration:
    def __init__(self, brain) -> None:
        self.brain = brain
        self.bot_token = settings.TELEGRAM_BOT_TOKEN

    def send_message(self, chat_id: str, message: str) -> bool:
        """Transmits message payload to Telegram chat."""
        if not self.bot_token:
            logger.warning("Telegram token missing. Logging mock message transmission.")
            logger.info(f"Mock Telegram to {chat_id}: '{message}'")
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            resp = requests.post(url, json=payload, timeout=5.0)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to post telegram payload: {e}")
            return False
            
    def get_updates(self) -> list:
        """Collects incoming update payloads."""
        if not self.bot_token:
            return []
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        try:
            resp = requests.get(url, timeout=5.0)
            return resp.json().get("result", []) if resp.status_code == 200 else []
        except Exception:
            return []
