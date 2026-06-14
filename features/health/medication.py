import time
from typing import List, Dict

class MedicationManager:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def add_medication(self, name: str, dose: str, time_of_day: str) -> None:
        """Saves medication parameters to long-term memory."""
        key = f"med_{name}_{time_of_day.replace(':', '')}"
        value = f"{dose}|{time_of_day}|active"
        self.memory_db.save_memory("medications", key, value)

    def remove_medication(self, name: str, time_of_day: str) -> None:
        """Removes a medication reminder."""
        key = f"med_{name}_{time_of_day.replace(':', '')}"
        self.memory_db.save_memory("medications", key, f"||inactive")

    def get_active_medications(self) -> List[Dict[str, str]]:
        """Returns active medication list."""
        raw_meds = self.memory_db.get_all_memories_by_topic("medications")
        active_list = []
        for key, val in raw_meds.items():
            if not val or val.startswith("||"):
                continue
            parts = val.split("|")
            if len(parts) != 3:
                continue
            dose, time_slot, status = parts
            if status == "active":
                # Extract name from key
                name = key.split("_")[1]
                active_list.append({
                    "name": name,
                    "dose": dose,
                    "time": time_slot
                })
        return active_list
