import time
from typing import Dict, List

class StudentBudgetTracker:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def set_monthly_limit(self, amount: float) -> None:
        """Saves target budget spending ceiling."""
        self.memory_db.save_memory("budget_settings", "monthly_cap", str(amount))

    def get_monthly_limit(self) -> float:
        """Retrieves target budget spending ceiling."""
        cap = self.memory_db.get_memory("budget_settings", "monthly_cap")
        return float(cap) if cap else 10000.0  # Default 10000 currency units

    def add_expense(self, category: str, amount: float, description: str) -> None:
        """Appends expense item to database logs."""
        timestamp = time.time()
        key = f"expense_{timestamp:.6f}"
        value = f"{category}|{amount}|{description}"
        self.memory_db.save_memory("expenses_log", key, value)

    def get_total_spent(self) -> float:
        """Sums up logged expenses."""
        logs = self.memory_db.get_all_memories_by_topic("expenses_log")
        total = 0.0
        for val in logs.values():
            try:
                parts = val.split("|")
                if len(parts) == 3:
                    _, amount_str, _ = parts
                    total += float(amount_str)
            except ValueError:
                pass
        return total

def get_budget_summary(memory_db) -> str:
    """Calculates spent ratio and returns alert messages."""
    tracker = StudentBudgetTracker(memory_db)
    limit = tracker.get_monthly_limit()
    spent = tracker.get_total_spent()
    
    remaining = limit - spent
    ratio = (spent / limit) * 100.0 if limit > 0 else 0
    
    summary = f"Budget status: Spent {spent}/{limit} ({ratio:.1f}%).\n"
    if remaining <= 0:
        summary += "Warning: You have exceeded your monthly budget, Boss!"
    elif ratio >= 80:
        summary += f"Caution: You are approaching your limit. Only {remaining:.1f} left!"
    else:
        summary += f"Safe: You have {remaining:.1f} remaining for this month."
        
    return summary
