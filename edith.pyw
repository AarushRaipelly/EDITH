import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from config import settings
from core.edith import EdithBrain
from modes.cmd import CMDInterface
from dashboard.hud import EdithHUD
from voice.speaker import EdithSpeaker
from voice.listener import EdithListener

# Setup root logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(settings.LOGS_DIR / "edith.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EDITH.Main")

def run_onboarding(brain: EdithBrain) -> None:
    """Guides Boss through the onboarding setup checklist."""
    speaker = EdithSpeaker()
    speaker.speak("Welcome, Boss, to EDITH onboarding. Let's configure your assistant profile.")
    
    print("\n--- EDITH ONBOARDING WIZARD ---")
    
    # 1. Fallback PIN
    pin = input("Set a fallback PIN (e.g. 1234) > ").strip()
    brain.memory.save_memory("security", "pin", pin)
    
    # 2. Panic Word
    panic = input("Set a secret Panic Word (e.g. 'wipeout') > ").strip()
    brain.memory.save_memory("security", "panic_word", panic)
    
    # 3. Emergency Contacts
    emergency_name = input("Enter an emergency contact name (e.g. 'Dad') > ").strip()
    emergency_phone = input("Enter their phone number > ").strip()
    brain.memory.save_memory("emergency_contacts", emergency_name, emergency_phone)
    
    # 4. Dead man's switch timer
    deadman_hours = input("Set Dead Man's Switch duration in hours (default: 24) > ").strip()
    brain.memory.save_memory("security", "deadman_hours", deadman_hours or "24")
    
    # 5. Monthly budget
    budget = input("Set your monthly student budget limit (default: 10000) > ").strip()
    brain.memory.save_memory("budget_settings", "monthly_cap", budget or "10000")

    # Save mock profiles so face matches, and run voice recording
    brain.memory.save_memory("security", "face_profile_registered", "True")
    
    import numpy as np
    from security.auth import EdithAuth
    from voice.listener import EdithListener
    
    speaker.speak("Let's record your voice profile. Speak clearly for 3 seconds when prompted.")
    wav_path = settings.MEMORY_DIR / "voice_profile.wav"
    listener = EdithListener()
    if listener.record_voice_profile(str(wav_path)):
        auth = EdithAuth(brain.memory)
        fp = auth.generate_voice_fingerprint(str(wav_path))
        np.save(str(settings.MEMORY_DIR / "voice_profile.npy"), fp)
        brain.memory.save_memory("security", "voice_profile_registered", "True")
        speaker.speak("Voice biometric signature registered successfully.")
    else:
        speaker.speak("Voice registration failed. Falling back to default profile.")
        brain.memory.save_memory("security", "voice_profile_registered", "True")
    
    # Complete Onboarding flag
    brain.memory.save_memory("system", "onboarded", "True")
    brain.onboarded = True
    
    speaker.speak("Setup complete! EDITH is fully initialized. Ready when you are, Boss.")

def main() -> None:
    """Application entry point."""
    # Programmatically ensure secure Fernet encryption key setup before initialization
    from setup_key import setup_encryption_key
    setup_encryption_key()

    brain = EdithBrain()
    speaker = EdithSpeaker()
    listener = EdithListener()

    # Parse arguments
    cmd_mode = "--cmd" in sys.argv or "-c" in sys.argv

    # Check onboarding completion
    if not brain.onboarded:
        run_onboarding(brain)

    if cmd_mode:
        # CMD Mode: text-only interface by default
        interface = CMDInterface(brain)
        interface.start_loop()
    else:
        # Hide the console window on Windows for headless GUI execution
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )

        # Desktop GUI Mode: Start Tkinter HUD (which runs on the main thread)
        # And run the voice loop in a background thread.
        hud = EdithHUD(brain)
        brain.hud = hud
        
        # Start voice loop in a background thread
        import threading
        voice_thread = threading.Thread(target=brain.start_voice_loop, daemon=True)
        voice_thread.start()
        
        try:
            hud.start()  # Blocks on root.mainloop()
        except KeyboardInterrupt:
            logger.info("Interrupt received, shutting down.")
        finally:
            hud.stop()
            brain.shutdown()

if __name__ == "__main__":
    main()
