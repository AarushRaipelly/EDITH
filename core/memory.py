import sqlite3
import shutil
import time
from typing import Dict, List, Optional
from config import settings
from security.encryption import EncryptionManager

class EdithMemory:
    def __init__(self) -> None:
        self.encryptor = EncryptionManager()
        self.db_path = settings.DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        """Initializes tables for encrypted memories and dialogue history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    UNIQUE(topic, key)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def save_memory(self, topic: str, key: str, value: str) -> None:
        """Encrypts and stores a piece of long-term memory."""
        encrypted_val = self.encryptor.encrypt(value)
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memories (topic, key, value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (topic, key, encrypted_val, now))
            conn.commit()

    def get_memory(self, topic: str, key: str) -> Optional[str]:
        """Retrieves and decrypts a piece of long-term memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM memories WHERE topic = ? AND key = ?
            """, (topic, key))
            row = cursor.fetchone()
            if row:
                return self.encryptor.decrypt(row[0])
        return None

    def get_all_memories_by_topic(self, topic: str) -> Dict[str, str]:
        """Retrieves and decrypts all keys under a specific topic."""
        memories = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT key, value FROM memories WHERE topic = ?
            """, (topic,))
            rows = cursor.fetchall()
            for key, val in rows:
                memories[key] = self.encryptor.decrypt(val)
        return memories

    def wipe_topic(self, topic: str) -> None:
        """Erases all memories under a specific topic."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE topic = ?", (topic,))
            conn.commit()

    def wipe_all(self) -> None:
        """Completely wipes database database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories")
            cursor.execute("DELETE FROM conversations")
            conn.commit()

    def log_dialogue(self, session_id: str, role: str, content: str) -> None:
        """Logs encrypted conversation turn."""
        encrypted_content = self.encryptor.encrypt(content)
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, encrypted_content, now))
            conn.commit()

    def get_dialogue_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves the dialogue history for a session."""
        history = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content FROM conversations WHERE session_id = ? ORDER BY id ASC
            """, (session_id,))
            rows = cursor.fetchall()
            for role, content in rows:
                history.append({
                    "role": role,
                    "content": self.encryptor.decrypt(content)
                })
        return history

    def backup(self) -> str:
        """Backs up the SQLite database to the backups folder."""
        backup_filename = f"edith_backup_{int(time.time())}.db"
        dest_path = settings.BACKUPS_DIR / backup_filename
        shutil.copy2(str(self.db_path), str(dest_path))
        return str(dest_path)

    def restore(self, backup_path: str) -> None:
        """Restores the memory database from a backup file."""
        shutil.copy2(backup_path, str(self.db_path))
        # Re-initialize after copying to verify connection integrity
        self._init_db()
