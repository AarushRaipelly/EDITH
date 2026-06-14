import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("EDITH.Integrations.API")

class APIConnector:
    def __init__(self) -> None:
        pass

    def call_rest_api(self, method: str, url: str, headers: dict = None, json_data: dict = None) -> Optional[dict]:
        """Dispatches generic REST HTTP requests."""
        logger.info(f"REST API Request: {method} {url}")
        try:
            resp = requests.request(method, url, headers=headers, json=json_data, timeout=5.0)
            if resp.status_code in (200, 201):
                return resp.json()
        except Exception as e:
            logger.error(f"Generic REST call failed: {e}")
        return None

    def trigger_webhook(self, webhook_url: str, payload: dict) -> bool:
        """Sends data webhook payloads to third-party endpoints."""
        logger.info(f"Webhook Trigger: Dispatching payload to: {webhook_url}")
        try:
            resp = requests.post(webhook_url, json=payload, timeout=5.0)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to post webhook payload: {e}")
            return False
