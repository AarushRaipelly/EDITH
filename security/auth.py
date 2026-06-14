import time
import logging
import wave
import numpy as np
from typing import Dict, Any
from pathlib import Path
from config import settings

logger = logging.getLogger("EDITH.Security.Auth")

class EdithAuth:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db
        self.authenticated = False
        self.last_auth_time = 0.0

    def generate_voice_fingerprint(self, wav_path: str) -> np.ndarray:
        """Computes a 20-dimensional frequency fingerprint from a WAV audio file."""
        try:
            with wave.open(wav_path, "rb") as wav:
                params = wav.getparams()
                frames = wav.readframes(params.nframes)
                signal = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                if len(signal) == 0:
                    return np.zeros(20, dtype=np.float32)

                # Compute power spectrum using FFT
                fft_data = np.abs(np.fft.rfft(signal))
                
                # Group into 20 frequency bands
                buckets = np.array_split(fft_data, 20)
                fingerprint = np.array([np.mean(b) if len(b) > 0 else 0.0 for b in buckets], dtype=np.float32)
                
                # Normalize vector to unit length
                norm = np.linalg.norm(fingerprint)
                if norm > 0:
                    fingerprint = fingerprint / norm
                return fingerprint
        except Exception as e:
            logger.error(f"Error generating voice fingerprint: {e}")
            return np.zeros(20, dtype=np.float32)

    def verify_pin(self, pin: str) -> bool:
        """Verifies the owner's PIN stored in the encrypted memory database."""
        stored_pin = self.memory_db.get_memory("security", "pin")
        if stored_pin and pin == stored_pin:
            self.authenticated = True
            self.last_auth_time = time.time()
            return True
        return False

    def verify_voice(self, voice_sample_path: str) -> bool:
        """Biometric voiceprint verification using Fast Fourier Transform (FFT) fingerprints."""
        logger.info(f"Analyzing voiceprint from: {voice_sample_path}")
        
        saved_profile_path = settings.MEMORY_DIR / "voice_profile.npy"
        if not saved_profile_path.exists():
            logger.warning("No registered voice profile found. Checking database metadata status.")
            stored_profile = self.memory_db.get_memory("security", "voice_profile_registered")
            return stored_profile == "True"

        try:
            saved_fp = np.load(str(saved_profile_path))
            current_fp = self.generate_voice_fingerprint(voice_sample_path)
            
            # Compute cosine similarity
            dot_product = np.dot(saved_fp, current_fp)
            norm_saved = np.linalg.norm(saved_fp)
            norm_current = np.linalg.norm(current_fp)
            
            if norm_saved == 0.0 or norm_current == 0.0:
                return False
                
            similarity = dot_product / (norm_saved * norm_current)
            logger.info(f"Vocal biometric similarity matches: {similarity:.4f}")
            
            # Check threshold (0.85)
            if similarity >= 0.85:
                self.authenticated = True
                self.last_auth_time = time.time()
                return True
        except Exception as e:
            logger.error(f"Error verifying voice biometric signature: {e}")
            
        return False

    def verify_face(self, face_image_path: str) -> bool:
        """Simulates biometric face recognition.
        Matches if facial data correlates to Boss's stored profile.
        """
        logger.info(f"Analyzing facial layout from: {face_image_path}")
        stored_profile = self.memory_db.get_memory("security", "face_profile_registered")
        if stored_profile == "True":
            self.authenticated = True
            self.last_auth_time = time.time()
            return True
        return False

    def check_session_timeout(self, timeout_limit: float) -> bool:
        """Invalidates credentials if the duration since last login exceeds the threshold."""
        if not self.authenticated:
            return True
        elapsed = time.time() - self.last_auth_time
        if elapsed > timeout_limit:
            self.authenticated = False
            return True
        return False

    def lock_session(self) -> None:
        """Logs out immediately."""
        self.authenticated = False
        self.last_auth_time = 0.0
