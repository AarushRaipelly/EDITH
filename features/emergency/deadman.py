import time
import logging
from features.emergency.sos import SOSEngine

logger = logging.getLogger("EDITH.Emergency.Deadman")

class DeadManSwitch:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db
        self.last_check_in = time.time()

    def update_check_in(self) -> None:
        """Resets the dead man's timer to the current time."""
        self.last_check_in = time.time()
        # Save to database to survive crashes
        self.memory_db.save_memory("security", "last_activity", str(self.last_check_in))

    def check_switch_status(self) -> bool:
        """Evaluates elapsed time against limits and triggers SOS if necessary."""
        stored_limit_hours = self.memory_db.get_memory("security", "deadman_hours")
        limit_hours = float(stored_limit_hours) if stored_limit_hours else 24.0
        
        last_act_str = self.memory_db.get_memory("security", "last_activity")
        last_act = float(last_act_str) if last_act_str else self.last_check_in
        
        elapsed_seconds = time.time() - last_act
        limit_seconds = limit_hours * 3600.0
        
        if elapsed_seconds > limit_seconds:
            logger.critical("DEAD MAN SWITCH TRIGGERED! Boss is unresponsive.")
            sos = SOSEngine(self.memory_db)
            sos.trigger_sos()
            return True
            
        return False
