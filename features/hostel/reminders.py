import time
from datetime import datetime
from config import settings

def check_curfew() -> str:
    """Calculates hours remaining until the hostel gate closes."""
    now = datetime.now()
    curfew_hour = settings.HOSTEL_GATE_CURFEW_HOUR
    
    if now.hour >= curfew_hour:
        return "Warning, Boss! Curfew time has passed. The hostel gate is likely closed."
    
    time_left = curfew_hour - now.hour
    minutes_left = 60 - now.minute
    if minutes_left < 60:
        time_left -= 1
    else:
        minutes_left = 0
        
    return f"Boss, curfew warning: you have {time_left} hours and {minutes_left} minutes until hostel gate closing at {curfew_hour}:00."

def check_mess() -> str:
    """Checks upcoming hostel meal block timelines."""
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    
    breakfast = settings.MESS_BREAKFAST_TIME
    lunch = settings.MESS_LUNCH_TIME
    dinner = settings.MESS_DINNER_TIME

    if current_time_str < breakfast:
        return f"Breakfast opens at {breakfast}. Keep going, Boss."
    elif current_time_str < lunch:
        return f"Breakfast closed. Next meal is Lunch at {lunch}."
    elif current_time_str < dinner:
        return f"Lunch closed. Dinner opens at {dinner}."
    else:
        return "All meal times have concluded for today, Boss. Canteen may have night snacks."
