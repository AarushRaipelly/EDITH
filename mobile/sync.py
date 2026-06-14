import json
import logging
from typing import Dict, Any

logger = logging.getLogger("EDITH.Mobile.Sync")

class DeviceSynchronizer:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def package_sync_data(self) -> str:
        """Serializes preferences, tasks, schedules, and active logs to a payload."""
        logger.info("Packing database state for synchronization.")
        # Retrieve all database memories
        all_pref = self.memory_db.get_all_memories_by_topic("settings")
        all_schedule = self.memory_db.get_all_memories_by_topic("academic_schedule")
        
        sync_package = {
            "preferences": all_pref,
            "schedule": all_schedule,
            "device": "PC"
        }
        return json.dumps(sync_package)

    def unpack_sync_data(self, json_payload: str) -> bool:
        """Parses phone synchronization data and overwrites local tables."""
        logger.info("Unpacking mobile sync data.")
        try:
            data = json.loads(json_payload)
            # Update settings
            for key, val in data.get("preferences", {}).items():
                self.memory_db.save_memory("settings", key, val)
            return True
        except Exception as e:
            logger.error(f"Sync unpack failed: {e}")
            return False
