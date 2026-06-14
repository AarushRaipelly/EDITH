import logging
from config import settings

logger = logging.getLogger("EDITH.Voice.Speaker")

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    logger.warning("pyttsx3 library not found. Falling back to print statements.")

class EdithSpeaker:
    muted = False

    def __init__(self, brain=None) -> None:
        self.brain = brain

    def speak(self, text: str) -> None:
        """Speaks the text output aloud, and prints it to the console."""
        # Always output to console
        print(f"\nEDITH: {text}")

        # Update HUD chat and status thread-safely
        try:
            if self.brain and self.brain.hud:
                self.brain.hud.add_chat_message("EDITH", text)
                self.brain.hud.update_status("Speaking")
        except Exception:
            pass

        if not pyttsx3 or not text or EdithSpeaker.muted:
            try:
                if self.brain and self.brain.hud:
                    self.brain.hud.update_status("Idle")
            except Exception:
                pass
            return

        try:
            # Initialize Windows SAPI5 engine on demand
            engine = pyttsx3.init('sapi5')
            
            # Configure engine properties
            engine.setProperty("rate", settings.VOICE_SPEECH_RATE)
            engine.setProperty("volume", settings.VOICE_VOLUME)
            
            # Select Zira, Hazel or other female voice
            voices = engine.getProperty("voices")
            selected_voice = False
            for voice in voices:
                name = voice.name.lower()
                if "zira" in name or "hazel" in name or "female" in name:
                    engine.setProperty("voice", voice.id)
                    selected_voice = True
                    break
                    
            if not selected_voice and len(voices) > 1:
                engine.setProperty("voice", voices[1].id)

            engine.say(text)
            engine.runAndWait()
            # Clean up immediately
            del engine
        except Exception as e:
            logger.error(f"Text-to-speech execution failed: {e}")
        finally:
            try:
                if self.brain and self.brain.hud:
                    self.brain.hud.update_status("Idle")
            except Exception:
                pass

