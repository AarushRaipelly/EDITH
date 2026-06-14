from typing import List

class GuestPermissionsManager:
    def __init__(self) -> None:
        self.whitelisted_topics = ["general", "canteen", "weather"]
        self.blacklisted_actions = ["delete_file", "send_message", "make_payment", "open_camera"]

    def is_action_allowed(self, action_name: str) -> bool:
        """Determines if a guest user is whitelisted for a specific command."""
        return action_name not in self.blacklisted_actions

    def is_topic_allowed(self, topic: str) -> bool:
        """Determines if guest can access memory topics."""
        return topic in self.whitelisted_topics
