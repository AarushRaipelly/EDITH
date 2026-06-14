import requests
import random
import logging
from typing import Dict

logger = logging.getLogger("EDITH.Lifestyle.MemeMode")

class MemeManager:
    def __init__(self) -> None:
        self.local_memes = [
            "Why do programmers wear glasses? Because they can't C#! 👓",
            "There are 10 types of people in this world: those who understand binary, and those who don't. 💻",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem. 💡",
            "['hip', 'hip'] (hip hip array!) 🚀",
            "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 🍺"
        ]

    def get_random_meme(self) -> str:
        """Fetches memes from Reddit API or falls back to local humor list."""
        try:
            # Querying Reddit meme endpoints
            resp = requests.get("https://meme-api.com/gimme", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                return f"Title: {data.get('title')}\nLink: {data.get('url')}"
        except Exception:
            pass

        return random.choice(self.local_memes)
