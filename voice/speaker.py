import logging
import time
import winsound
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

    def play_alert(self, alert_type: str) -> None:
        """Plays custom alert frequencies and duration patterns on Windows systems."""
        if EdithSpeaker.muted:
            return
            
        try:
            if alert_type == "wake":
                # Double-beep chime
                winsound.Beep(800, 120)
                winsound.Beep(1200, 180)
            elif alert_type == "success":
                # Upward arpeggio
                winsound.Beep(600, 100)
                winsound.Beep(800, 100)
                winsound.Beep(1000, 150)
            elif alert_type == "warning":
                # Flat warning tone
                winsound.Beep(440, 200)
                time.sleep(0.05)
                winsound.Beep(440, 200)
            elif alert_type == "error":
                # Descending warning buzz
                winsound.Beep(500, 250)
                winsound.Beep(350, 350)
            elif alert_type == "breakthrough":
                # High-pitched DND alarm breakthrough
                winsound.Beep(1500, 100)
                time.sleep(0.05)
                winsound.Beep(1500, 100)
                time.sleep(0.05)
                winsound.Beep(1500, 100)
            else:
                # Default standard beep
                winsound.Beep(800, 150)
        except Exception as e:
            logger.warning(f"Failed to execute winsound beep alert of type '{alert_type}': {e}")

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

        # Respect Voice-First Preference (switch to text-only when requested)
        if self.brain and not getattr(self.brain.context, "respond_via_voice", True):
            try:
                if self.brain.hud:
                    self.brain.hud.update_status("Idle")
            except Exception:
                pass
            return

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
            
            # Configure engine properties (adjusting dynamically for whisper mode)
            is_whispering = self.brain and getattr(self.brain.context, "whisper_mode", False)
            volume = 0.2 if is_whispering else settings.VOICE_VOLUME
            rate = 150 if is_whispering else settings.VOICE_SPEECH_RATE
            
            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)
            
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
