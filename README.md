# E.D.I.T.H. (Extremely Intelligent Diurnal Tactical Helper) 🤖

E.D.I.T.H. is an advanced Python-based personal AI assistant designed to run as a sleek, glowing, borderless desktop HUD widget. It responds wittily to the owner ("Boss"), integrating voice activation, encrypted SQLite-based memory storage, hostel/academic utilities, safety gate security controls, and robust thread-safe GUI updates.

---

## 🎨 Futuristic Sci-Fi HUD Interface
EDITH runs in a borderless, always-on-top corner widget matching an **Iron Man Arc Reactor** aesthetic.

### Visual Design Specs:
* **Dimensions**: Standard corner view (`280x420px`), expandable to full view (`500x700px`) on double-click.
* **Background**: Pure tactical black (`#050d12`) with neon-cyan glowing L-bracket corners.
* **Header**: Features an animated pulsing Arc Reactor core, a monospaced "EDITH" title, a blinking green status dot, and top-right window controls.
* **Mode Bar**: Displays the current operation state (IDLE, LISTENING, PROCESSING, SPEAKING, DND, SLEEPING) alongside a real-time digital clock.
* **Chat Bubbles History**: Shows dialogue logs in right-aligned (Boss) and left-aligned (EDITH) slate/teal bubble containers with auto-scroll.
* **Interactive Text Input**: Includes a monospaced entry box and SEND button at the bottom of the chat container to type manual commands.
* **2x2 Stats Grid**: Displays real-time battery status, active tasks, memory usage (via real `psutil` system metrics), and next class countdown (queried dynamically from the academic schedule database).
* **Waveform Visualizer**: Animates 5 bar voice frequency waves during active listening or speaking.
* **Control Row**: Includes toggle commands for microphone capture (`🎙️ MIC`), DND block, voice output muting (`🔇 MUTE`), and system sleep (`💤 SLEEP`).

### HUD Interactions:
* **Click and Drag**: Drag anywhere on the HUD background to reposition the window on your screen.
* **Double-click**: Double-click the widget to expand it to a larger layout (`500x700px`) or restore it back to standard (`280x420px`).
* **Right-click (Minimize to Tray)**: Right-clicking collapses the HUD into a tiny `24x24px` cyan glowing handle circle dot in the bottom-right corner of the screen. Simply click/double-click the dot to restore the HUD.
* **Title Controls**: Use the custom top-right buttons: Minimize (`—`), Fullscreen/Expand (`⛶`), and Close (`✕`).

---

## 🛡️ Advanced Security & Safety Gates
EDITH implements strict, multi-tier protection layers to safeguard Boss's environment.
* **Safety Gate Whitelists**: 
  - **App Whitelist**: Gated to safe/common Windows executables (calc, notepad, chrome, vscode, paint, word, excel, powerpoint, vlc, spotify, brave, edge). Unauthorized launcher requests are blocked.
  - **File Blacklist**: Prevents reading/writing files outside the workspace directory.
  - **Contact Blacklist**: Blocks sending emails or messages to unauthorized/suspicious addresses or phone numbers.
* **Access Profiles**:
  - **Guest Mode**: Activated via command. Restricts queries to whitelisted topics (general, weather, mess) and blocks all file operations, message transmissions, or app launching.
  - **Roommate Mode**: Restricts roommate access to general academic/hostel schedules and weather, locking down financial trackers, biometrics registration, and email/WhatsApp automation.
* **Owner Biometrics**: Verified voice profiles (via FFT frequencies comparison) and PIN fallbacks protect high-stakes operations.
* **Intrusions Honeypots**: Spawns realistic mock financial balance sheets to distract uninvited guests while silently logging details.
* **Panic Wipe**: Silently cleans session contexts, deletes temporary cache directories, and wipes sensitive logs immediately when the panic word is received.

---

## 🗣️ Hinglish & Tone Adapter
* **Hinglish/Hindi Translation**: Automatically detects if Boss is speaking in Hindi or mixed Hinglish. Translates speech to standard English queries for internal brain routing, and translates final responses back into Hinglish/Hindi format.
* **Vocal Tone Analysis**: Scans transcripts for lexical stress, anxiety, or work markers to adapt EDITH's personality in real-time. If Boss is stressed, she responds calmly and supportively; if playful, she adds witty humor.
* **Whisper Mode**: Lowers pyttsx3 volume scale (to 0.2) and slows down speech rate (to 150) for quiet, brief, and discreet replies.
* **Voice-First Toggle**: Swaps between speech output and text-only mode dynamically when Boss asks to ("give me that in text", "type that out").

---

## ⏰ Diurnal Background Reminders & Routines
* **Reminder Daemon**: A background checking loop periodically monitors daily parameters:
  - **Medication Schedule**: Plays an breakthrough alarm and speaks out when it's time to take active doses.
  - **Hostel Curfew**: Alerts Boss 30 minutes before hostel gate curfew closes (`settings.HOSTEL_GATE_CURFEW_HOUR`).
  - **Mess Meals**: Triggers chimes and announces canteen openings for breakfast, lunch, and dinner.
* **Morning Routine**: Triggered by "good morning" or "morning routine". EDITH compiles the current local weather, today's class schedule, pending assignment deadlines, battery level, and tells a funny developer joke.

---

## 🎙️ winsound Beep Alert Chimes
EDITH confirms actions with custom audio alerts:
* `wake`: soft double-beep chime
* `success`: rising musical arpeggio
* `warning`: flat warning tone sequence
* `error`: descending buzz tone
* `breakthrough`: rapid breakthrough alert

---

## 🚀 Headless Setup & Launch (Windows)
To run EDITH completely hidden in the background without any CMD console window popping up:

### Method 1: Desktop VBS Launcher (Recommended)
1. Locate [edith.vbs](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.vbs) in the project root.
2. Right-click `edith.vbs` → **Send to** → **Desktop (create shortcut)**.
3. Go to your Desktop, right-click the shortcut → **Properties**.
4. In the Shortcut tab, click **Change Icon...**, choose a custom icon, and save.
5. Double-click the shortcut to run. The HUD will appear silently without spawning a CMD window.

### Method 2: Batch Launcher
Execute the fallback [edith.bat](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.bat) script. It launches EDITH in pythonw background mode and immediately closes the terminal window.

### Method 3: Pythonw Native
From terminal, run:
```bash
pythonw main.py
```
Or execute [edith.pyw](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.pyw) using:
```bash
python edith.pyw
```

---

## 📂 Project Layout
* `config/`: Preferences and app state loaders.
* `core/`: Main brain, tasks manager, memory SQLite DB, context management.
* `security/`: Auth, encryption, safety gates, sandboxing, and audit logs.
* `voice/`: Speeches, listeners, tone, Hinglish translator.
* `features/`: Academic, hostel, emergency, budget trackers.
* `vision/`: Cameras, scans, object/face identifiers.
* `dashboard/`: HUD borderless widgets and UI components.
* `modes/`: Profiles (DND, guest, whisper, roommate).
* `setup.py`: Registers local packages and global script commands.
