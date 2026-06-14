import time
from pathlib import Path
from config import settings

class EdithAuditLogger:
    def __init__(self) -> None:
        self.log_file = settings.LOGS_DIR / "audit.log"
        # Ensure log directory is present
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_action(self, action: str, details: str, context) -> None:
        """Appends logs to audit file unless DND mode blocks tracking."""
        if context and context.dnd_mode:
            return  # Blackout: do absolutely nothing

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_line = f"[{timestamp}] ACTION: {action} | DETAILS: {details} | DEVICE: {context.active_device if context else 'Unknown'}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
