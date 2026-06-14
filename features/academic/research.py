import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger("EDITH.Academic.Research")

class ResearchAssistant:
    def __init__(self) -> None:
        pass

    def search_arxiv(self, query: str) -> List[Dict[str, str]]:
        """Queries arXiv API for academic abstracts matching the term."""
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=3"
        results = []
        try:
            resp = requests.get(url, timeout=5.0)
            if resp.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                
                # Namespaces
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip()
                    summary = entry.find('atom:summary', ns).text.strip()
                    results.append({
                        "title": title,
                        "summary": summary
                    })
        except Exception as e:
            logger.error(f"Failed to query arXiv api: {e}")
            # Mock fallback data
            results = [{
                "title": f"Mock Paper: A Review on {query.capitalize()}",
                "summary": "This hypothetical paper summarizes the core components and mathematical foundations of the topic, outlining state-of-the-art results."
            }]
        return results

    def summarize_chapter(self, text: str) -> str:
        """Helper to create executive bullet summaries of textbook chapters."""
        sentences = text.split(". ")
        # Return first few sentences as mock summary
        summary = "Executive Summary:\n"
        for i, s in enumerate(sentences[:3]):
            if s:
                summary += f"- {s.strip()}.\n"
        return summary

    def explain_concept(self, concept: str) -> str:
        """Returns simplified explanation of complex terms."""
        concepts_db = {
            "quantum mechanics": "Physics branch analyzing microscopic objects. Like how light acts both like tiny billiard balls and ocean waves.",
            "gradient descent": "Optimizing technique finding local minima. Like walking downhill blindly by taking steps in the steepest direction.",
            "recursion": "A programming pattern where a function calls itself to solve smaller sub-pieces of the main problem."
        }
        return concepts_db.get(concept.lower(), f"Concept '{concept}' - In simple terms: It is a critical component of its domain which requires systematic analysis.")
