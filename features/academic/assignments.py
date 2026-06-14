import time
from typing import List, Dict, Any

class AssignmentTracker:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def add_assignment(self, subject: str, description: str, deadline_timestamp: float) -> None:
        """Saves assignment metadata to SQLite database."""
        key = f"assignment_{subject}_{int(deadline_timestamp)}"
        value = f"{description}|{deadline_timestamp}|pending"
        self.memory_db.save_memory("assignments", key, value)

    def mark_completed(self, key: str) -> None:
        """Marks a pending assignment as completed."""
        val = self.memory_db.get_memory("assignments", key)
        if val:
            desc, deadline, _ = val.split("|")
            new_val = f"{desc}|{deadline}|completed"
            self.memory_db.save_memory("assignments", key, new_val)

    def get_pending_assignments(self) -> List[Dict[str, Any]]:
        """Returns a list of assignments that are still pending."""
        raw_data = self.memory_db.get_all_memories_by_topic("assignments")
        pending_list = []
        now = time.time()
        for key, val in raw_data.items():
            parts = val.split("|")
            if len(parts) != 3:
                continue
            desc, deadline_str, status = parts
            try:
                deadline = float(deadline_str)
            except ValueError:
                continue
            if status == "pending":
                days_left = (deadline - now) / 86400.0
                pending_list.append({
                    "key": key,
                    "description": desc,
                    "deadline": deadline,
                    "days_remaining": round(days_left, 1)
                })
        # Sort by closest deadline
        pending_list.sort(key=lambda x: x["deadline"])
        return pending_list
