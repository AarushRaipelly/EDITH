import requests
import logging
from typing import List, Dict

logger = logging.getLogger("EDITH.Budget.Deals")

class DealFinder:
    def __init__(self) -> None:
        pass

    def find_cheapest_deals(self, product_name: str) -> List[Dict[str, str]]:
        """Queries or mocks API listings for cheapest online product offers."""
        logger.info(f"Searching for cheapest deals: '{product_name}'")
        
        # In production, queries eBay, Amazon, or local api search index
        # Here we return simulated comparison results
        mock_deals = [
            {"store": "Amazon", "price": "₹12,499", "url": "https://amazon.in/mock-item"},
            {"store": "Flipkart", "price": "₹11,999", "url": "https://flipkart.com/mock-item"},
            {"store": "Local Tech Hub", "price": "₹11,500", "url": "Dorm complex shop 4"}
        ]
        
        # Sort by simulated price (simple heuristic parsing digits)
        def parse_price(deal):
            nums = "".join(c for c in deal["price"] if c.isdigit())
            return int(nums) if nums else 99999
            
        mock_deals.sort(key=parse_price)
        return mock_deals
