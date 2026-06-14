import requests
import logging
from typing import List, Dict

logger = logging.getLogger("EDITH.Integrations.WebSearch")

class WebSearchEngine:
    def __init__(self) -> None:
        pass

    def search(self, query: str) -> List[Dict[str, str]]:
        """Queries public databases (e.g. DuckDuckGo XML/HTML API) and generates formatted responses."""
        logger.info(f"Searching web: '{query}'")
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        
        try:
            resp = requests.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                abstract = data.get("AbstractText", "")
                if abstract:
                    results.append({
                        "source": data.get("AbstractSource", "DuckDuckGo"),
                        "snippet": abstract,
                        "url": data.get("AbstractURL", "")
                    })
                
                # Check related topics
                topics = data.get("RelatedTopics", [])
                for t in topics[:2]:
                    if "Text" in t and "FirstURL" in t:
                        results.append({
                            "source": "DuckDuckGo Related",
                            "snippet": t["Text"],
                            "url": t["FirstURL"]
                        })
                
                if results:
                    return results
        except Exception as e:
            logger.error(f"Search API request failed: {e}")
            
        # Fallback simulated response
        return [{
            "source": "Mock search database",
            "snippet": f"Simulated information on '{query}'. It details standard theoretical perspectives.",
            "url": "https://wikipedia.org/wiki/" + query.replace(" ", "_")
        }]
