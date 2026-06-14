import os
from pathlib import Path
from dotenv import load_dotenv

# Base Path definition
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment files
load_dotenv(BASE_DIR / ".env")

# App Directory Structures
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"
CACHE_DIR = DATA_DIR / "cache"

# Ensure all workspace directories are present
for directory in [DATA_DIR, MEMORY_DIR, LOGS_DIR, BACKUPS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database file location
DB_PATH = MEMORY_DIR / "edith.db"

# API Token configurations
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PICOVOICE_API_KEY = os.getenv("PICOVOICE_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EDITH_ENCRYPTION_KEY = os.getenv("EDITH_ENCRYPTION_KEY", "")

# Default Preferences
VOICE_SPEECH_RATE = 175
VOICE_VOLUME = 0.9
VOICE_GENDER = "female"  # "male" or "female"
PREFERRED_LANGUAGE = "hinglish"  # "english", "hindi", "hinglish"

# Session Timeout
SESSION_TIMEOUT_SECONDS = 900  # 15 minutes

# Default Academic configuration
DEFAULT_POMODORO_WORK_MINS = 25
DEFAULT_POMODORO_BREAK_MINS = 5

# Hostel Preferences
HOSTEL_GATE_CURFEW_HOUR = 21  # 9:00 PM
MESS_BREAKFAST_TIME = "08:00"
MESS_LUNCH_TIME = "13:00"
MESS_DINNER_TIME = "20:00"

# Health Settings
DEFAULT_WATER_GOAL_LITERS = 3.0

# Security Defaults
ANOMALY_THRESHOLD = 0.8  # Threshold for warning Boss about security anomalies

# Microphone Preference
MIC_INDEX = 1

