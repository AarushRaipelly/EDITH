# EDITH Setup & Installation Guide 🛠️

Follow these instructions to establish the active environment for EDITH.

## Prerequisites

- **Python 3.8 or higher**
- **C++ Build Tools** (Required for optional libraries like `face_recognition` and `pvporcupine`)
- **Git**

## Setup Flow

1. **Extract/Clone codebase** into your working directory.
2. **Create the environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Install standard dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Register the `edith` CMD Command globally**:
   Install the package in editable mode:
   ```bash
   pip install -e .
   ```
   *Note: Ensure your Python/Scripts directory is added to your system PATH variables.*

5. **Configure Keys**:
   Copy the `.env.example` template to `.env` and insert your credentials.
   ```bash
   cp .env.example .env
   ```
6. **First Onboarding Launch**:
   Run the setup script:
   ```bash
   python main.py
   ```
   This will launch the Onboarding Wizard (voice profile settings, fallback PIN setup, emergency numbers, class timetable, monthly budgets).

## Headless Launch Setup (Windows)

To launch EDITH silently without spawning any CMD terminal window, use the following methods:

### Method 1: Desktop Shortcut (Recommended)
1. In the project directory, locate the [edith.vbs](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.vbs) script.
2. Right-click on `edith.vbs` → **Send to** → **Desktop (create shortcut)**.
3. Go to your Desktop, right-click on the new shortcut, and choose **Properties**.
4. In the Shortcut tab, click **Change Icon...**, choose a cool icon, and save.
5. Double-click the shortcut to run EDITH. The HUD will appear silently in the background.

### Method 2: Batch Launcher
Run the fallback [edith.bat](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.bat) file. It launches EDITH in the background and closes the CMD window immediately.

### Method 3: Pythonw Native
Simply run:
```bash
pythonw main.py
```
Or execute [edith.pyw](file:///c:/Users/PC01/Desktop/Aarush/COLLEGE/personal_project/EDITH/edith.pyw) using:
```bash
python edith.pyw
```
