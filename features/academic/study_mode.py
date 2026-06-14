import time
import threading
import logging
from config import settings

logger = logging.getLogger("EDITH.Academic.StudyMode")

class StudyModeManager:
    def __init__(self) -> None:
        self.active_study_session = False
        self.pomodoro_thread = None

    def start_pomodoro(self, work_mins: int = settings.DEFAULT_POMODORO_WORK_MINS, break_mins: int = settings.DEFAULT_POMODORO_BREAK_MINS, loops: int = 4) -> None:
        """Launches a Pomodoro work loop in a background thread."""
        if self.active_study_session:
            return
        
        self.active_study_session = True
        self.pomodoro_thread = threading.Thread(
            target=self._pomodoro_loop, 
            args=(work_mins, break_mins, loops),
            daemon=True
        )
        self.pomodoro_thread.start()

    def _pomodoro_loop(self, work_mins: int, break_mins: int, loops: int) -> None:
        logger.info("Pomodoro loop initiated.")
        self.block_distracting_websites()
        
        # Load and play focus background audio track
        self.play_focus_music()

        for loop in range(loops):
            if not self.active_study_session:
                break
            
            logger.info(f"Pomodoro Work Block {loop+1}/{loops} started.")
            time.sleep(work_mins * 60)
            
            if not self.active_study_session:
                break
                
            logger.info("Work block finished. Time for a break!")
            time.sleep(break_mins * 60)

        self.stop_study_session()

    def stop_study_session(self) -> None:
        """Concludes study session and restores settings."""
        self.active_study_session = False
        self.unblock_distracting_websites()
        logger.info("Study session concluded. Distractions unblocked.")

    def block_distracting_websites(self) -> None:
        """Mocks modifying hosts file or network configurations to prevent distraction."""
        logger.info("Distraction Blocker: Distracting URLs redirected to localhost (Mock).")

    def unblock_distracting_websites(self) -> None:
        """Restores network hosts file to default."""
        logger.info("Distraction Blocker: Hosts file restored (Mock).")

    def play_focus_music(self) -> None:
        """Plays study/relaxing lo-fi audio tracks."""
        logger.info("Audio: Focus sound track started playing in the background.")
