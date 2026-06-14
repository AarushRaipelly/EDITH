import time
from typing import Dict, Any, List

class EdithContext:
    def __init__(self) -> None:
        self.session_id: str = str(int(time.time()))
        self.current_topic: str = "general"
        self.zero_knowledge_mode: bool = False
        self.dnd_mode: bool = False
        self.whisper_mode: bool = False
        self.active_device: str = "PC"  # "PC" or "Mobile"
        self.boss_tone: str = "normal"  # "stressed", "playful", "work", "normal"
        self.temporary_context: Dict[str, Any] = {}
        self.interruption_occurred: bool = False
        self.topic_history: List[str] = ["general"]

    def switch_topic(self, new_topic: str) -> None:
        """Seamlessly transitions conversational topic logs."""
        if self.current_topic != new_topic:
            self.topic_history.append(new_topic)
            self.current_topic = new_topic

    def set_zero_knowledge(self, status: bool) -> None:
        """Toggle saving status. When True, no conversations or logs are written."""
        self.zero_knowledge_mode = status

    def set_dnd(self, status: bool) -> None:
        """Toggles DND status."""
        self.dnd_mode = status

    def reset_session(self) -> None:
        """Refreshes ephemeral session trackers."""
        self.session_id = str(int(time.time()))
        self.temporary_context.clear()
        self.boss_tone = "normal"
        self.topic_history = ["general"]
        self.current_topic = "general"
        self.interruption_occurred = False
