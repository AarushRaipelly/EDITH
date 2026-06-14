# EDITH Integration API Docs 🔌

This guide covers outbound connections and webhooks.

## 1. Outbound REST Connector
Modules invoke the generic `APIConnector` class inside `integrations/api_connector.py` for REST calls:

```python
from integrations.api_connector import APIConnector

conn = APIConnector()
response = conn.call_rest_api(
    method="GET",
    url="https://api.github.com/users/octocat"
)
```

## 2. Webhooks
Send notifications to secondary automation tasks:
```python
payload = {"alert": "Study Mode Activated", "status": "Busy"}
conn.trigger_webhook(
    webhook_url="https://make.com/incoming/webhook-id",
    payload=payload
)
```

## 3. Telegram Updates
Checks chat triggers on the bot webhook:
```python
from integrations.telegram import TelegramIntegration
tg = TelegramIntegration(brain)
tg.send_message(chat_id="12345678", message="Class alert, Boss!")
```
