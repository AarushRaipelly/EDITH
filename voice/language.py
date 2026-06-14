import re
from typing import Dict

class EdithLanguageManager:
    def __init__(self) -> None:
        # Dictionary of common Hinglish terms mapped to English meanings
        self.hinglish_dict: Dict[str, str] = {
            "kya": "what",
            "kaise": "how",
            "karo": "do",
            "chalu": "start",
            "band": "stop",
            "batao": "tell",
            "khabar": "news",
            "mausam": "weather",
            "paani": "water",
            "kamra": "room"
        }

    def detect_language(self, text: str) -> str:
        """Determines if input is English, Hindi (Unicode Devnagari), or Hinglish."""
        # Detect Devnagari unicode range
        if re.search(r"[\u0900-\u097F]", text):
            return "hindi"

        # Detect transliterated Hinglish words
        words = text.lower().split()
        hinglish_hits = sum(1 for w in words if w in self.hinglish_dict)
        
        if hinglish_hits > 0:
            return "hinglish"
        return "english"

    def translate_to_english(self, text: str) -> str:
        """Translates Hinglish or basic Hindi phrases into standard English queries."""
        words = text.lower().split()
        translated_words = [self.hinglish_dict.get(w, w) for w in words]
        return " ".join(translated_words)

    def formulate_response(self, english_response: str, target_lang: str) -> str:
        """Adapts response vocabulary to match Boss's target language."""
        if target_lang == "hinglish":
            # Return basic Hinglish sentence wrapping
            return f"Boss, {english_response} (Maine update kar diya hai)."
        elif target_lang == "hindi":
            return f"बॉस, {english_response}"
        return english_response
