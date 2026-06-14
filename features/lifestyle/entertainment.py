from typing import List, Dict

class EntertainmentManager:
    def __init__(self) -> None:
        self.catalogs = {
            "stressed": {
                "movies": ["Amélie", "My Neighbor Totoro", "The Grand Budapest Hotel"],
                "music": ["Weightless - Marconi Union", "Lofi Girl Study Beats", "Chill Acoustic Sessions"]
            },
            "playful": {
                "movies": ["Superbad", "The Naked Gun", "Spider-Man: Into the Spider-Verse"],
                "music": ["Happy - Pharrell Williams", "Don't Stop Me Now - Queen", "Uptown Funk"]
            },
            "work": {
                "movies": ["The Social Network", "Limitless", "Whiplash"],
                "music": ["Mozart Clarinet Concerto", "Synthwave Productivity Loops", "Deep Focus Binaural Beats"]
            }
        }

    def suggest(self, mood: str, media_type: str = "all") -> Dict[str, List[str]]:
        """Returns entertainment choices based on current mood status."""
        catalog = self.catalogs.get(mood.lower(), self.catalogs["playful"])
        
        if media_type == "movies":
            return {"movies": catalog["movies"]}
        elif media_type == "music":
            return {"music": catalog["music"]}
            
        return catalog
