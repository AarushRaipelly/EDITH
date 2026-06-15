import os
from pathlib import Path
import logging
from config import settings

logger = logging.getLogger("EDITH.Security.SafetyGate")

class SafetyGate:
    def __init__(self) -> None:
        self.whitelisted_apps = {
            "calculator", "calc", "notepad", "paint", "mspaint", 
            "cmd", "command prompt", "task manager", "taskmgr", 
            "file explorer", "explorer", "chrome", "vlc", 
            "spotify", "whatsapp", "whatsapp desktop", "vs code", 
            "vscode", "word", "excel", "powerpoint", "brave", "edge"
        }
        
        # Blacklisted contacts/numbers that Edith cannot email or text
        self.blacklisted_contacts = {
            "spammer", "unauthorized", "attacker", "intruder",
            "9999999999", "0000000000"
        }

    def is_app_allowed(self, app_name: str) -> bool:
        """Checks if the system application is whitelisted."""
        name = app_name.lower().strip()
        allowed = name in self.whitelisted_apps
        if not allowed:
            logger.warning(f"SafetyGate: Blocked execution of unauthorized app '{app_name}'")
        return allowed

    def is_file_path_allowed(self, file_path: str, write_mode: bool = False) -> bool:
        """Prevents reading/writing files outside the allowed workspace boundary."""
        try:
            target_path = Path(file_path).resolve()
            allowed_root = Path(settings.BASE_DIR).resolve()
            
            # Check if target_path is inside the allowed_root
            allowed = allowed_root in target_path.parents or target_path == allowed_root
            if not allowed:
                logger.warning(f"SafetyGate: Blocked file access attempt to path outside workspace: '{file_path}'")
            return allowed
        except Exception as e:
            logger.error(f"SafetyGate: Error validating file path '{file_path}': {e}")
            return False

    def is_contact_allowed(self, contact: str) -> bool:
        """Validates if messaging/emailing a contact is allowed."""
        cleaned = contact.lower().strip()
        allowed = cleaned not in self.blacklisted_contacts
        if not allowed:
            logger.warning(f"SafetyGate: Blocked communication to blacklisted contact/number '{contact}'")
        return allowed
