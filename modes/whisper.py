import logging
from config import settings

logger = logging.getLogger("EDITH.Modes.Whisper")

class WhisperModeController:
    def __init__(self, speaker, brain=None) -> None:
        self.speaker = speaker
        self.brain = brain

    def activate_whisper(self) -> None:
        """Lowers speaker volume and shortens conversational text structures."""
        logger.info("Whisper mode activated.")
        if self.brain:
            self.brain.context.whisper_mode = True
        if self.speaker and hasattr(self.speaker, "engine") and self.speaker.engine:
            try:
                self.speaker.engine.setProperty("volume", 0.2)
                self.speaker.engine.setProperty("rate", 150)
            except Exception:
                pass

    def deactivate_whisper(self) -> None:
        """Restores standard voice volume settings."""
        logger.info("Whisper mode deactivated.")
        if self.brain:
            self.brain.context.whisper_mode = False
        if self.speaker and hasattr(self.speaker, "engine") and self.speaker.engine:
            try:
                self.speaker.engine.setProperty("volume", settings.VOICE_VOLUME)
                self.speaker.engine.setProperty("rate", settings.VOICE_SPEECH_RATE)
            except Exception:
                pass
