from typing import Dict, List, Optional
import time

class EdithLearningManager:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db
        self.pending_modifications: List[Dict[str, str]] = []

    def log_correction(self, pattern: str, correction: str) -> Dict[str, str]:
        """Registers a correction from Boss and drafts a pending change."""
        modification = {
            "id": str(int(time.time())),
            "pattern": pattern,
            "correction": correction,
            "status": "pending_approval"
        }
        self.pending_modifications.append(modification)
        return modification

    def approve_modification(self, mod_id: str) -> bool:
        """Applies a specific behavioral modification after Boss grants permission."""
        for mod in self.pending_modifications:
            if mod["id"] == mod_id and mod["status"] == "pending_approval":
                mod["status"] = "approved"
                # Store permanent correction pattern in sqlite memory
                self.memory_db.save_memory("behavior_rules", mod["pattern"], mod["correction"])
                return True
        return False

    def reject_modification(self, mod_id: str) -> bool:
        """Discards a proposed behavioral update."""
        for mod in self.pending_modifications:
            if mod["id"] == mod_id:
                mod["status"] = "rejected"
                return True
        return False

    def get_pending_rules(self) -> List[Dict[str, str]]:
        """Returns all corrections waiting for approval."""
        return [m for m in self.pending_modifications if m["status"] == "pending_approval"]

    def retrieve_active_rules(self) -> Dict[str, str]:
        """Loads all verified behavior rules from memory."""
        return self.memory_db.get_all_memories_by_topic("behavior_rules")
