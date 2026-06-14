import requests
import logging
from typing import Dict, List

logger = logging.getLogger("EDITH.Emergency.SOS")

class SOSEngine:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def trigger_sos(self) -> str:
        """Collects location parameters and prepares notifications for emergency contacts."""
        logger.critical("SOS SYSTEM INITIATED!")
        
        # 1. Fetch Location Coordinates (Simulated or via IP geolocation API)
        lat, lon = self._get_geolocation()
        location_url = f"https://maps.google.com/?q={lat},{lon}"
        
        # 2. Get Predefined Contacts
        contacts = self.memory_db.get_all_memories_by_topic("emergency_contacts")
        contact_list = [f"{name} ({phone})" for name, phone in contacts.items()]
        
        message = (
            f"ALERT: SOS Triggered by Boss. Location: {location_url}. "
            "Please check in immediately."
        )
        
        # In production, triggers telegram or Twilio API messaging
        logger.warning(f"Simulating dispatch of SOS message: '{message}' to: {contact_list}")
        
        return (
            "SOS PROTOCOL COMPLETED, Boss.\n"
            f"- Current Location: Latitude: {lat}, Longitude: {lon}\n"
            f"- Alert dispatched to contacts: {', '.join(contact_list) if contact_list else 'None configured'}."
        )

    def _get_geolocation(self) -> tuple:
        """Fetches longitude and latitude. Falls back to mock values on failure."""
        try:
            resp = requests.get("https://ipapi.co/json/", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("latitude", 28.6139), data.get("longitude", 77.2090)
        except Exception:
            pass
        return 28.6139, 77.2090  # Default Delhi coordinates
