from typing import Dict, List

class HostelExpenseTracker:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def add_expense(self, description: str, total_amount: float, paid_by: str, split_among: List[str]) -> None:
        """Logs a shared transaction and balances debt pools."""
        if not split_among:
            return
        
        split_share = total_amount / len(split_among)
        # Store paid amount
        self._adjust_ledger(paid_by, total_amount)
        
        # Debts adjustment
        for user in split_among:
            self._adjust_ledger(user, -split_share)

    def get_ledger(self) -> Dict[str, float]:
        """Returns the net balances of all friends."""
        raw_ledger = self.memory_db.get_all_memories_by_topic("hostel_expenses")
        ledger = {}
        for name, val in raw_ledger.items():
            ledger[name] = float(val)
        return ledger

    def _adjust_ledger(self, name: str, amount: float) -> None:
        topic = "hostel_expenses"
        current_bal = self.memory_db.get_memory(topic, name)
        new_bal = amount
        if current_bal:
            new_bal = float(current_bal) + amount
        self.memory_db.save_memory(topic, name, str(new_bal))

    def reset_balances(self) -> None:
        """Clears expense history."""
        self.memory_db.wipe_topic("hostel_expenses")
