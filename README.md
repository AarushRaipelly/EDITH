# EDITH (Extremely Intelligent Diurnal Tactical Helper) 🤖

EDITH is a highly advanced Python-based AI personal assistant designed to run on PCs with integrated mobile synchronization and visual HUD support. Formatted to respond warmly, causally, and wittily to the owner ("Boss"), EDITH integrates voice recognition, encrypted memory storage, multi-mode operations (including DND and panic lockouts), hostel/academic managers, and local security systems.

## Key Features

- **Voice & Speech Interface**: Dynamic wake-word activation (`Hey Edith`), English/Hindi/Hinglish language detection, stress/tone analysis, and quiet whisper mode support.
- **Security & Privacy**: Verified voice profile gating, fallback PIN auth, face verification, AES encryption, honeypots, sandboxed tasks, and a silent session wipe panic word.
- **Academic Manager**: Class timetable reminders, assignments/exams countdowns, and voice note categorization.
- **Hostel Helper**: Canteen reminders, roommate profiles, expense logs, curfew warnings, and lower power mode.
- **Glassmorphic HUD**: Beautiful tkinter graphical dashboard showing CPU stats, pending tasks, reminders, and current active profile mode.
- **Integrations**: Selenium-based browser automation, Google Calendar/Drive triggers, Telegram bots, WhatsApp notifications, local weather, RSS reader, and custom API webhook support.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/EDITH.git
   cd EDITH
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API credentials:
   ```bash
   cp .env.example .env
   ```

5. **Start EDITH**:
   - For graphical and voice mode:
     ```bash
     python main.py
     ```
   - For terminal text-only mode:
     ```bash
     edith --cmd
     ```

## Project Layout

- `config/`: Preferences and app state loaders.
- `core/`: Main brain, tasks, memory db, context management.
- `security/`: Auth, encryption, panic keys, sandboxing, and audit logs.
- `voice/`: Speeches, listeners, tone, Hinglish translator.
- `features/`: Academic, hostel, emergency, budget trackers.
- `vision/`: Cameras, scans, object/face identifiers.
- `dashboard/`: HUD canvas widgets.
- `modes/`: Profiles (DND, guest, whisper).
- `tests/`: Automated unit and system assertions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
