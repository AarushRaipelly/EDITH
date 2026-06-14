import time
import threading
import logging

logger = logging.getLogger("EDITH.Emergency.FakeCall")

class FakeCallScheduler:
    def __init__(self) -> None:
        pass

    def schedule_fake_call(self, delay_minutes: float) -> None:
        """Schedules a fake incoming phone call to execute in a thread."""
        logger.info(f"Fake call scheduled in {delay_minutes} minutes.")
        t = threading.Thread(target=self._trigger_call, args=(delay_minutes * 60,), daemon=True)
        t.start()

    def _trigger_call(self, delay_seconds: float) -> None:
        time.sleep(delay_seconds)
        # Ring alert or play simulated sound
        logger.warning("[FAKE CALL TRIGGERED] Incoming call from 'Home' - Ringing Boss's device.")
        print("\n*** RING RING! Incoming Call from: Home ***")
