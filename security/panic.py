import logging
from config import settings

logger = logging.getLogger("EDITH.Security.Panic")

def trigger_panic(brain) -> str:
    """Triggered by panic word. Wipes active session memory and alerts Boss."""
    logger.critical("PANIC PROTOCOL TRIGGERED! Initiating silent wipe...")
    
    # 1. Reset context/session immediately
    brain.context.reset_session()
    
    # 2. Clear temp memory cache
    cache_dir = settings.CACHE_DIR
    for item in cache_dir.iterdir():
        if item.is_file():
            try:
                item.unlink()
            except Exception:
                pass
                
    # 3. Alert Boss (simulated silent SMS or backend webhook)
    # in real app: send_silent_webhook_alert()
    
    return "Understood. Session has been secured."
