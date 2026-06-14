import time
from typing import Dict

class WellbeingManager:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def trigger_break_suggestion(self) -> str:
        """Returns focus break recommendations."""
        return "Boss, you've been working intensely. Time to step away, stretch, rest your eyes, and grab some water."

    def check_in_mood(self, mood_score: int, journals: str) -> None:
        """Logs mood entries. ONLY invoked when Boss explicitly requests a mood check-in."""
        timestamp = int(time.time())
        key = f"mood_{timestamp}"
        value = f"{mood_score}|{journals}"
        self.memory_db.save_memory("wellbeing_log", key, value)

    def retrieve_mood_history(self) -> Dict[str, str]:
        """Recalls past mood entries."""
        return self.memory_db.get_all_memories_by_topic("wellbeing_log")
