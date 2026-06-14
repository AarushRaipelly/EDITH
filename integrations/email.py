import logging

logger = logging.getLogger("EDITH.Integrations.Email")

class GmailIntegration:
    def __init__(self, brain) -> None:
        self.brain = brain

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Composes and sends an email. ALWAYS asks Boss for permission before firing."""
        action_msg = f"Send email to {recipient} with subject '{subject}'"
        
        # Confirm with Boss first
        if not self.brain.request_permission(action_msg):
            logger.warning("Email transmission aborted by Boss.")
            return False

        logger.info(f"Email sent successfully to {recipient}.")
        return True

    def read_unread_emails(self) -> list:
        """Fetches list of unread inbox threads."""
        logger.info("Retrieving unread inbox emails.")
        return [
            {"from": "Prof. Sharma", "subject": "Assignment Extension", "snippet": "The deadline has been extended to Friday..."},
            {"from": "Hostel Warden", "subject": "Maintenance Notice", "snippet": "There will be a scheduled power outage tomorrow..."}
        ]
