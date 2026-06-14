import requests
import logging
from config import settings

logger = logging.getLogger("EDITH.Integrations.Weather")

class WeatherIntegration:
    def __init__(self) -> None:
        self.api_key = settings.WEATHER_API_KEY

    def get_weather(self, city: str = "Delhi") -> str:
        """Retrieves meteorological data for a target location."""
        if not self.api_key:
            logger.warning("Weather API Key missing. Returning mock weather data.")
            return f"Mock weather for {city}: 32°C, Partly Cloudy, Humidity: 60%."

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        try:
            resp = requests.get(url, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"Weather in {city}: {temp}°C, {desc.capitalize()}."
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
        return "Weather service currently unreachable."
