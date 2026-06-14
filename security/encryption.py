import os
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

def load_and_validate_key() -> bytes:
    """Loads the encryption key from .env and validates it. Raises error if missing or corrupted."""
    base_dir = Path(__file__).resolve().parent.parent
    
    # Reload .env from disk to ensure we have the latest generated key
    load_dotenv(base_dir / ".env", override=True)
    
    key_str = os.getenv("EDITH_ENCRYPTION_KEY", "").strip()
    if not key_str:
        raise ValueError("CRITICAL ERROR: EDITH_ENCRYPTION_KEY is missing from the environment or .env file!")
        
    try:
        key_bytes = key_str.encode()
        # Verify it can be loaded by Fernet (checks for correct 32-byte base64 format)
        Fernet(key_bytes)
        return key_bytes
    except Exception as e:
        raise ValueError(f"CRITICAL ERROR: EDITH_ENCRYPTION_KEY is corrupted or invalid Fernet key format: {e}")

class EncryptionManager:
    def __init__(self) -> None:
        try:
            self.key = load_and_validate_key()
        except ValueError as e:
            # Crash loudly at startup if key validation fails
            raise e
        self.cipher = Fernet(self.key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypts plain text string to encrypted token."""
        if not plain_text:
            return ""
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        """Decrypts encrypted token to plain text string."""
        if not cipher_text:
            return ""
        try:
            return self.cipher.decrypt(cipher_text.encode()).decode()
        except Exception:
            return "[Decryption Failed - Check Encryption Key]"

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypts raw bytes."""
        return self.cipher.encrypt(data)

    def decrypt_bytes(self, cipher_data: bytes) -> bytes:
        """Decrypts raw bytes."""
        return self.cipher.decrypt(cipher_data)
