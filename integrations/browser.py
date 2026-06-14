import webbrowser
import logging

logger = logging.getLogger("EDITH.Integrations.Browser")

class BrowserController:
    def __init__(self) -> None:
        pass

    def open_url(self, url: str) -> None:
        """Opens a webpage in the default system browser."""
        logger.info(f"Opening browser URL: '{url}'")
        webbrowser.open(url)

    def automate_form_fill(self, url: str, form_data: dict) -> None:
        """Automates fields input and submissions via Selenium.
        Placeholder hook for Selenium driver execution.
        """
        logger.info(f"Initiating Selenium automation on: {url} with parameters: {list(form_data.keys())}")

    def open_app(self, app_name: str) -> bool:
        """Launches native system applications on Windows using os.startfile or subprocess fallback."""
        import os
        import subprocess
        
        app_name = app_name.lower().strip()
        
        # Expand environment variables for paths
        user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        app_data = os.environ.get("APPDATA", "C:\\Users\\Default\\AppData\\Roaming")
        local_app_data = os.environ.get("LOCALAPPDATA", "C:\\Users\\Default\\AppData\\Local")
        
        # Define candidate paths for common Windows applications
        app_paths = {
            "calculator": ["calc.exe"],
            "calc": ["calc.exe"],
            "notepad": ["notepad.exe"],
            "paint": ["mspaint.exe"],
            "mspaint": ["mspaint.exe"],
            "cmd": ["cmd.exe"],
            "command prompt": ["cmd.exe"],
            "task manager": ["taskmgr.exe"],
            "taskmgr": ["taskmgr.exe"],
            "file explorer": ["explorer.exe"],
            "explorer": ["explorer.exe"],
            "chrome": [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "chrome.exe"
            ],
            "vlc": [
                "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
                "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe",
                "vlc.exe"
            ],
            "spotify": [
                os.path.join(app_data, "Spotify\\Spotify.exe"),
                os.path.join(local_app_data, "Microsoft\\WindowsApps\\Spotify.exe"),
                "spotify.exe"
            ],
            "whatsapp desktop": [
                os.path.join(local_app_data, "WhatsApp\\WhatsApp.exe"),
                os.path.join(local_app_data, "Microsoft\\WindowsApps\\WhatsApp.exe"),
                "whatsapp.exe"
            ],
            "whatsapp": [
                os.path.join(local_app_data, "WhatsApp\\WhatsApp.exe"),
                os.path.join(local_app_data, "Microsoft\\WindowsApps\\WhatsApp.exe"),
                "whatsapp.exe"
            ],
            "vs code": [
                os.path.join(local_app_data, "Programs\\Microsoft VS Code\\Code.exe"),
                "code.exe"
            ],
            "vscode": [
                os.path.join(local_app_data, "Programs\\Microsoft VS Code\\Code.exe"),
                "code.exe"
            ],
            "word": [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                "winword.exe"
            ],
            "excel": [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
                "excel.exe"
            ],
            "powerpoint": [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
                "powerpnt.exe"
            ],
            "brave": [
                "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "brave.exe"
            ],
            "edge": [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                "msedge.exe"
            ]
        }
        
        candidates = app_paths.get(app_name)
        if not candidates:
            # Fallback: sanitize and try running name directly
            sanitized = "".join(c for c in app_name if c.isalnum() or c in ['-', '_', ' '])
            if sanitized:
                candidates = [sanitized]
            else:
                logger.error(f"Invalid application name: '{app_name}'")
                return False
                
        # Resolve path
        resolved_cmd = None
        for path in candidates:
            if os.path.isabs(path):
                if os.path.exists(path):
                    resolved_cmd = path
                    break
            else:
                resolved_cmd = path
                break
                
        if not resolved_cmd:
            resolved_cmd = candidates[-1]

        logger.info(f"Launching application '{app_name}' via resolved command '{resolved_cmd}'")
        
        # 1. Primary Method: os.startfile()
        try:
            norm_cmd = os.path.normpath(resolved_cmd) if os.path.isabs(resolved_cmd) else resolved_cmd
            os.startfile(norm_cmd)
            return True
        except AttributeError:
            pass  # Non-Windows systems
        except Exception as e:
            logger.warning(f"os.startfile failed for '{resolved_cmd}': {e}. Falling back to subprocess.Popen...")
            
        # 2. Fallback Method: subprocess.Popen
        try:
            subprocess.Popen(resolved_cmd, shell=True)
            return True
        except Exception as e:
            logger.error(f"Failed to launch application '{app_name}' via subprocess: {e}")
            return False


