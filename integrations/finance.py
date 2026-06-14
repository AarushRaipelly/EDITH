import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("EDITH.Integrations.Finance")

class FinanceIntegration:
    def __init__(self, budget_tracker) -> None:
        self.tracker = budget_tracker

    def parse_sms_transaction(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """Parses bank alerts to register budget debits automatically."""
        # Matches formats like: "Sent Rs.500 to Friend via UPI" or "Debited Rs. 150"
        pattern = r"(?:Rs\.|INR)\s*([\d,]+)"
        match = re.search(pattern, sms_text, re.IGNORECASE)
        
        if match:
            try:
                amount_val = float(match.group(1).replace(",", ""))
                category = "General"
                if "swiggy" in sms_text.lower() or "canteen" in sms_text.lower():
                    category = "Food"
                elif "uber" in sms_text.lower() or "auto" in sms_text.lower():
                    category = "Travel"
                    
                # Log transaction to budget
                self.tracker.add_expense(category, amount_val, f"Auto-parsed SMS: {sms_text[:30]}...")
                return {"amount": amount_val, "category": category}
            except ValueError:
                pass
        return None
