import socket
import logging

logger = logging.getLogger("EDITH.Modes.Offline")

class OfflineModeManager:
    def __init__(self) -> None:
        pass

    def is_internet_available(self) -> bool:
        """Checks if web connections are active by opening a test socket connection."""
        try:
            # Connect to Google Public DNS
            socket.setdefaulttimeout(2.0)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except Exception:
            logger.warning("No internet connection detected. Switching to offline-gated features.")
            return False
            
    def get_supported_offline_features(self) -> list:
        return ["academic_schedule", "local_notes", "pomodoro_timer", "medication_reminders", "budget_tracker"]
