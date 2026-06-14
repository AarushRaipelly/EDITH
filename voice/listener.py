import logging
import time
import threading
import difflib
import winsound
from config import settings
from typing import Optional

logger = logging.getLogger("EDITH.Voice.Listener")

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("speech_recognition library not found. Falling back to keyboard input.")

class EdithListener:
    def __init__(self, brain=None) -> None:
        self.brain = brain
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = None
        self.ambient_adjusted = False
        
        if sr:
            mic_index = getattr(settings, "MIC_INDEX", 1)
            logger.info(f"Initializing microphone on index: {mic_index}")
            try:
                self.microphone = sr.Microphone(device_index=mic_index)
            except Exception as e:
                logger.warning(f"Could not initialize microphone on index {mic_index}: {e}. Trying default index.")
                try:
                    self.microphone = sr.Microphone()
                except Exception as e2:
                    logger.warning(f"Microphone initialization failed completely: {e2}. Falling back to keyboard.")
                    self.microphone = None

    def listen(self) -> str:
        """Listens to microphone voice input, falling back to keyboard/stdin input."""
        if not getattr(self.__class__, "mic_enabled", True):
            time.sleep(0.5)
            return ""

        if not self.recognizer or not self.microphone:
            try:
                # If running inside HUD and no mic, sleep instead of blocking on stdin input()
                if self.brain and self.brain.hud:
                    time.sleep(0.5)
                    return ""
                return input("Voice Input (Simulated) > ").strip()
            except (KeyboardInterrupt, EOFError):
                return ""

        audio = None
        try:
            with self.microphone as source:
                if not self.ambient_adjusted:
                    # Set Boss parameters
                    self.recognizer.energy_threshold = 500
                    self.recognizer.dynamic_energy_threshold = False
                    self.recognizer.pause_threshold = 0.8
                    
                    logger.info("Calibrating background noise levels...")
                    if self.brain and self.brain.hud:
                        self.brain.hud.update_status("Processing")
                        self.brain.hud.update_recognized_text("Calibrating mic...")
                    try:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    except Exception as e:
                        logger.warning(f"Failed to adjust for ambient noise: {e}")
                    self.ambient_adjusted = True
                
                logger.info("Listening for voice...")
                if self.brain and self.brain.hud:
                    self.brain.hud.update_status("Listening")
                    self.brain.hud.update_recognized_text("Listening...")
                
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=8.0)
        except sr.WaitTimeoutError:
            if self.brain and self.brain.hud:
                self.brain.hud.update_status("Idle")
                self.brain.hud.update_recognized_text("Idle")
            return ""
        except Exception as e:
            logger.error(f"Error capturing audio from microphone: {e}")
            if self.brain and self.brain.hud:
                self.brain.hud.update_status("Idle")
                self.brain.hud.update_recognized_text(f"Error: {e}")
            return ""

        if not audio:
            if self.brain and self.brain.hud:
                self.brain.hud.update_status("Idle")
                self.brain.hud.update_recognized_text("Idle")
            return ""

        # Perform translation using Google Speech API with en-IN language support
        try:
            if self.brain and self.brain.hud:
                self.brain.hud.update_status("Processing")
                self.brain.hud.update_recognized_text("Transcribing...")
            text = self.recognizer.recognize_google(audio, language="en-IN")
            # Print recognized text to console every single time for debugging
            print(f"[Google Heard]: '{text}'")
            logger.info(f"Speech Recognized (en-IN): {text}")
            if self.brain and self.brain.hud:
                self.brain.hud.update_recognized_text(text)
            return text
        except sr.UnknownValueError:
            print("[Google Heard]: [Speech was unintelligible]")
            logger.info("Speech was unintelligible.")
            if self.brain and self.brain.hud:
                self.brain.hud.update_recognized_text("[Unintelligible]")
                self.brain.hud.update_status("Idle")
            return ""
        except sr.RequestError as e:
            print(f"[Google Heard]: [API Error: {e}]")
            logger.warning(f"Google Speech Recognition service unavailable: {e}")
            if self.brain and self.brain.hud:
                self.brain.hud.update_recognized_text(f"[API Error: {e}]")
                self.brain.hud.update_status("Idle")
            return ""
        except Exception as e:
            print(f"[Google Heard]: [Error: {e}]")
            logger.error(f"Error during speech recognition translation: {e}")
            if self.brain and self.brain.hud:
                self.brain.hud.update_recognized_text(f"[Error: {e}]")
                self.brain.hud.update_status("Idle")
            return ""

    def listen_for_wake_word(self, wake_word: str = "edith") -> bool:
        """Fuzzy wake word detector that supports multiple variations and SequenceMatcher ratios."""
        val = self.listen().lower().strip()
        if not val:
            return False
            
        WAKE_WORDS = [
            'edith', 'edit', 'idiot', 'idea', 'eedit',
            'edithe', 'hey edit', 'hey edith', 'hey idiot',
            'hey idea', 'hey jarvis', 'jarvis', 'hey eater',
            'either', 'heidi', 'egit', 'reddit', 'hey reddit',
            'davis', 'hey davis', 'atis', 'adith', 'hey adith'
        ]
        
        # 1. Check exact variations
        for word in WAKE_WORDS:
            if word in val:
                return True
                
        # 2. Check fuzzy match on each word
        for word in val.split():
            ratio = difflib.SequenceMatcher(None, word, 'edith').ratio()
            if ratio > 0.7:
                return True
                
        return False

    def start_background_listening(self, callback) -> None:
        """Starts continuous background listening loop in a daemon thread."""
        t = threading.Thread(target=self._continuous_loop, args=(callback,), daemon=True)
        t.start()
        logger.info("Background voice listener thread started.")

    def _continuous_loop(self, callback) -> None:
        """The continuous loop running in the background thread."""
        from voice.speaker import EdithSpeaker
        speaker = EdithSpeaker()
        
        logger.info("Continuous voice loop active. Ready to trigger on 'Edith'.")
        
        while True:
            try:
                # Continuous check for wake word
                if self.listen_for_wake_word("edith"):
                    print("Wake word detected!")
                    logger.info("Wake word detected!")
                    
                    # Play a soft double-beep chime
                    try:
                        winsound.Beep(800, 150)
                        winsound.Beep(1200, 200)
                    except Exception as e:
                        logger.warning(f"Failed to play chime: {e}")
                        
                    # Say "I'm here, Boss!" out loud
                    speaker.speak("I'm here, Boss!")
                    
                    # Listen for the actual command within 5 seconds
                    logger.info("Listening for command...")
                    command_audio = None
                    try:
                        with self.microphone as source:
                            command_audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=8.0)
                    except sr.WaitTimeoutError:
                        speaker.speak("I didn't hear a command, Boss.")
                        continue
                    except Exception as e:
                        logger.error(f"Error during command capture: {e}")
                        continue
                        
                    if command_audio:
                        try:
                            command_text = self.recognizer.recognize_google(command_audio, language="en-IN")
                            print(f"[Google Heard Command]: '{command_text}'")
                            
                            # Always confirm what was heard before executing
                            speaker.speak(f"Heard {command_text}.")
                            
                            # Execute command callback and speak response
                            if callback:
                                response = callback(command_text)
                                if response:
                                    speaker.speak(response)
                                    
                        except sr.UnknownValueError:
                            print("[Google Heard Command]: [Speech was unintelligible]")
                            speaker.speak("I didn't catch that, Boss.")
                        except Exception as e:
                            logger.error(f"Error transcribing command: {e}")
                            
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Unhandled error in voice loop: {e}")
                time.sleep(1.0)

    def record_voice_profile(self, dest_path: str) -> bool:
        """Captures microphone audio and saves it as a WAV file for voice biometrics."""
        if not self.recognizer or not self.microphone:
            logger.warning("Microphone not available. Creating a mock voice profile WAV file.")
            import wave
            with wave.open(dest_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframes(b'\x00' * 88200)
            return True

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logger.info("Recording voice profile... Please speak clearly.")
            try:
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=4.0)
                wav_data = audio.get_wav_data()
                with open(dest_path, "wb") as f:
                    f.write(wav_data)
                logger.info(f"Voice profile recorded and saved to {dest_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to record voice profile: {e}")
                return False
