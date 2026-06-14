# E.D.I.T.H. (Extremely Intelligent Diurnal Tactical Helper) 🤖

E.D.I.T.H. is an advanced Python-based personal AI assistant designed to run as a sleek, glowing, borderless desktop HUD widget. It responds wittily to the owner ("Boss"), integrating voice activation, encrypted SQLite-based memory storage, hostel/academic utilities, local security systems, and robust thread-safe GUI updates.

---

## 🎨 Futuristic Sci-Fi HUD Interface
EDITH runs in a borderless, always-on-top corner widget matching an **Iron Man Arc Reactor** aesthetic.

### Visual Design Specs:
* **Dimensions**: standard corner view (`280x420px`), expandable to full view (`500x700px`) on double-click.
* **Background**: pure tactical black (`#050d12`) with neon-cyan glowing L-bracket corners.
* **Header**: features an animated pulsing Arc Reactor core, a monospaced "EDITH" title, a blinking green status dot, and top-right window controls.
* **Mode Bar**: displays the current operation state (IDLE, LISTENING, PROCESSING, SPEAKING, DND, SLEEPING) alongside a real-time digital clock.
* **Chat Bubbles History**: shows dialogue logs in right-aligned (Boss) and left-aligned (EDITH) slate/teal bubble containers with auto-scroll.
* **Interactive Text Input**: includes a monospaced entry box and SEND button at the bottom of the chat container to type manual commands.
* **2x2 Stats Grid**: displays real-time battery status, active tasks, memory usage, and next class countdown with progress bars.
* **Waveform Visualizer**: animates 5 bar voice frequency waves during active listening or speaking.
* **Control Row**: includes toggle commands for microphone capture (`🎙️ MIC`), DND block, voice output muting (`🔇 MUTE`), and system sleep (`💤 SLEEP`).

### HUD Interactions:
* **Click and Drag**: drag anywhere on the HUD background to reposition the window on your screen.
* **Double-click**: double-click the widget to expand it to a larger layout (`500x700px`) or restore it back to standard (`280x420px`).
* **Right-click (Minimize to Tray)**: right-clicking collapses the HUD into a tiny `24x24px` cyan glowing handle circle dot in the bottom-right corner of the screen. Simply click/double-click the dot to restore the HUD.
* **Title Controls**: use the custom top-right buttons: Minimize (`—`), Fullscreen/Expand (`⛶`), and Close (`✕`).

---

## 🎙️ Voice & Wake-Word Upgrades
EDITH features an expanded list of 24 fuzzy wake-word variations to compensate for Google Speech Recognition mishearing her name:
* `edith`, `edit`, `idiot`, `idea`, `eedit`, `edithe`, `hey edit`, `hey edith`, `hey idiot`, `hey idea`, `hey jarvis`, `jarvis`, `hey eater`, `either`, `heidi`, `egit`, `reddit`, `hey reddit`, `davis`, `hey davis`, `atis`, `adith`, `hey adith`.

### winsound Beep Confirmation:
Upon hearing any of these wake words, EDITH plays a soft double-beep chime (`800Hz` & `1200Hz`) to confirm she is listening, updates the Arc Reactor to green, and replies *"I'm here, Boss."*

---

## 🔒 Queue-Based Thread Safety
To prevent crashes such as `RuntimeError: main thread is not in main loop`, EDITH implements a **queue-based update dispatch system**:
1. A thread-safe message queue (`queue.Queue`) handles all communications from background processes.
2. Background threads (voice listener, speaker, API calls) place updates into the queue instead of calling Tkinter widgets directly.
3. A `process_queue()` loop runs on the main Tkinter thread every 100ms (via `root.after()`) to pull updates from the queue and apply them safely, ensuring 100% stability.

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
* `security/`: Auth, encryption, panic keys, sandboxing, and audit logs.
* `voice/`: Speeches, listeners, tone, Hinglish translator.
* `features/`: Academic, hostel, emergency, budget trackers.
* `vision/`: Cameras, scans, object/face identifiers.
* `dashboard/`: HUD borderless widgets and UI components.
* `modes/`: Profiles (DND, guest, whisper).
* `setup.py`: Registers local packages and global script commands.
