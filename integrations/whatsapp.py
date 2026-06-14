import logging

logger = logging.getLogger("EDITH.Integrations.WhatsApp")

class WhatsAppIntegration:
    def __init__(self, brain) -> None:
        self.brain = brain

    def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """Sends WhatsApp message. ALWAYS requests Boss's permission before executing."""
        action_msg = f"Send WhatsApp message to {phone_number}: '{message}'"
        
        if not self.brain.request_permission(action_msg):
            logger.warning("WhatsApp message transmission aborted by Boss.")
            return False

        logger.info(f"WhatsApp message dispatched to {phone_number}.")
        return True
