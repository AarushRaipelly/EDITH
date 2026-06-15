class RoommateModeManager:
    def __init__(self) -> None:
        self.whitelisted_topics = ["general", "canteen", "weather", "academic_schedule"]
        self.blacklisted_actions = [
            "add_expense", 
            "set_budget_limit", 
            "trigger_sos",
            "open_app", 
            "send_email", 
            "send_whatsapp", 
            "send_telegram",
            "wipe_topic", 
            "record_voice_profile"
        ]

    def is_action_allowed(self, action_name: str) -> bool:
        """Determines if a roommate is permitted to execute a specific action."""
        return action_name not in self.blacklisted_actions

    def is_topic_allowed(self, topic: str) -> bool:
        """Determines if a roommate can access specific memory topics."""
        return topic in self.whitelisted_topics
