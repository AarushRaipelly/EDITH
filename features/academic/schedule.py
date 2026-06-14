import time
from typing import Dict, List

class AcademicSchedule:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def add_class(self, day: str, subject: str, start_time: str, room: str) -> None:
        """Stores a class slot into database memories."""
        key = f"{day.lower()}_{start_time}"
        value = f"{subject}|{room}"
        self.memory_db.save_memory("academic_schedule", key, value)

    def get_classes_by_day(self, day: str) -> List[Dict[str, str]]:
        """Retrieves and formats schedule classes for a given day."""
        raw_schedule = self.memory_db.get_all_memories_by_topic("academic_schedule")
        classes = []
        for key, val in raw_schedule.items():
            if key.startswith(day.lower()):
                parts = key.split("_")
                if len(parts) < 2:
                    continue
                time_slot = parts[1]
                val_parts = val.split("|")
                if len(val_parts) != 2:
                    continue
                subject, room = val_parts
                classes.append({
                    "time": time_slot,
                    "subject": subject,
                    "room": room
                })
        # Sort classes chronologically by start time
        classes.sort(key=lambda x: x["time"])
        return classes

def get_schedule_summary(memory_db) -> str:
    """Convenience helper to retrieve today's schedule summary."""
    day_name = time.strftime("%A").lower()
    sched = AcademicSchedule(memory_db)
    classes = sched.get_classes_by_day(day_name)
    if not classes:
        return f"No classes scheduled for today ({day_name.capitalize()}), Boss."
    
    summary = f"Today's Timetable ({day_name.capitalize()}):\n"
    for c in classes:
        summary += f"- {c['time']}: {c['subject']} in Room {c['room']}\n"
    return summary
