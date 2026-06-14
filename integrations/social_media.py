import logging

logger = logging.getLogger("EDITH.Integrations.SocialMedia")

class SocialMediaIntegration:
    def __init__(self, brain) -> None:
        self.brain = brain

    def post_status(self, platform: str, message: str) -> bool:
        """Publishes updates. ALWAYS requests Boss's permission before posting."""
        action_msg = f"Post to {platform}: '{message}'"
        
        if not self.brain.request_permission(action_msg):
            logger.warning(f"Social post on {platform} aborted by Boss.")
            return False

        logger.info(f"Published status to {platform}: '{message}'")
        return True
