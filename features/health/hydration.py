import time
from config import settings

class HydrationTracker:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def log_water_intake(self, milliliters: int) -> None:
        """Appends intake volume (ml) to today's tally."""
        today = time.strftime("%Y-%m-%d")
        current_logged = self.memory_db.get_memory("hydration", today)
        
        total = milliliters
        if current_logged:
            total += int(current_logged)
            
        self.memory_db.save_memory("hydration", today, str(total))

    def get_todays_intake(self) -> int:
        """Returns total milliliters consumed today."""
        today = time.strftime("%Y-%m-%d")
        logged = self.memory_db.get_memory("hydration", today)
        return int(logged) if logged else 0

    def check_progress_report(self) -> str:
        """Returns percentage progress toward the daily goal."""
        target_ml = settings.DEFAULT_WATER_GOAL_LITERS * 1000.0
        consumed = self.get_todays_intake()
        percentage = (consumed / target_ml) * 100.0
        
        return f"Boss, you have consumed {consumed}ml / {int(target_ml)}ml ({percentage:.1f}% of your goal today)."
