import logging
from config import settings

logger = logging.getLogger("EDITH.Modes.DND")

class DNDController:
    def __init__(self, brain) -> None:
        self.brain = brain

    def activate_dnd(self) -> None:
        """Enforces blackout: silences listeners and shuts active background tasks."""
        self.brain.context.set_dnd(True)
        # Suspend listener loop
        logger.warning("Blackout activated. Zero recording, zero logging, zero activity.")
        
    def deactivate_dnd(self) -> None:
        """Deactivates blackout."""
        self.brain.context.set_dnd(False)
        logger.info("Blackout deactivated. Resuming monitoring logs.")

    def play_breakthrough_alert(self, contact_name: str) -> None:
        """Plays custom priority contact alert sound."""
        logger.warning(f"DND Breakthrough alert! Incoming message from priority contact: {contact_name}")
        # simulated audio beep
        print("\n*** BEEP BEEP BEEP! Priority Contact Alert! ***")
