import os
from pathlib import Path
from config import settings

class VoiceNotesOrganizer:
    def __init__(self) -> None:
        self.notes_dir = settings.DATA_DIR / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        # Setup category keywords mapping
        self.subject_keywords = {
            "math": ["algebra", "calculus", "integral", "derivative", "equation"],
            "physics": ["mechanics", "quantum", "gravity", "force", "velocity", "wave"],
            "chemistry": ["organic", "molecule", "reaction", "acid", "periodic", "element"],
            "computer_science": ["python", "java", "coding", "algorithm", "database", "git"]
        }

    def save_note(self, content: str) -> str:
        """Classifies and writes dictated speech content into a text note file."""
        subject = self._classify_subject(content)
        subject_dir = self.notes_dir / subject
        subject_dir.mkdir(exist_ok=True)

        note_id = int(os.time()) if hasattr(os, "time") else int(settings.SESSION_TIMEOUT_SECONDS) # fallback
        import time
        note_id = int(time.time())
        
        note_file = subject_dir / f"note_{note_id}.txt"
        with open(note_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Saved to {subject} folder as note_{note_id}.txt"

    def _classify_subject(self, content: str) -> str:
        cleaned = content.lower()
        for subj, keywords in self.subject_keywords.items():
            if any(kw in cleaned for kw in keywords) or subj.replace("_", " ") in cleaned:
                return subj
        return "general"
