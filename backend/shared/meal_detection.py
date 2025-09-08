"""
Meal time detection based on time of day.
Automatically categorizes food entries into breakfast, lunch, dinner, or snack.
"""

from datetime import datetime
from typing import Literal

MealType = Literal["breakfast", "lunch", "dinner", "snack"]

def detect_meal_time(timestamp: datetime = None) -> MealType:
    """
    Detect the meal type based on the time of day.
    
    Args:
        timestamp: Optional datetime to check. If None, uses current time.
    
    Returns:
        Meal type: breakfast, lunch, dinner, or snack
    
    Time ranges:
        - Breakfast: 5:00 AM - 10:59 AM
        - Lunch: 11:00 AM - 2:59 PM
        - Snack: 3:00 PM - 5:59 PM
        - Dinner: 6:00 PM - 9:59 PM
        - Snack: 10:00 PM - 4:59 AM (late night snack)
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    hour = timestamp.hour
    
    # Breakfast: 5 AM to 10:59 AM
    if 5 <= hour < 11:
        return "breakfast"
    
    # Lunch: 11 AM to 2:59 PM
    elif 11 <= hour < 15:
        return "lunch"
    
    # Afternoon snack: 3 PM to 5:59 PM
    elif 15 <= hour < 18:
        return "snack"
    
    # Dinner: 6 PM to 9:59 PM
    elif 18 <= hour < 22:
        return "dinner"
    
    # Late night / early morning snack: 10 PM to 4:59 AM
    else:
        return "snack"


def get_meal_emoji(meal_type: MealType) -> str:
    """
    Get an emoji representation for the meal type.
    
    Args:
        meal_type: The type of meal
    
    Returns:
        Emoji string for the meal type
    """
    meal_emojis = {
        "breakfast": "🌅",
        "lunch": "☀️",
        "dinner": "🌙",
        "snack": "🍿"
    }
    return meal_emojis.get(meal_type, "🍽️")


def get_meal_display_name(meal_type: MealType) -> str:
    """
    Get a display-friendly name for the meal type.
    
    Args:
        meal_type: The type of meal
    
    Returns:
        Capitalized display name
    """
    return meal_type.capitalize()


def get_meal_time_suggestion(meal_type: MealType) -> str:
    """
    Get a contextual suggestion based on the meal type.
    
    Args:
        meal_type: The type of meal
    
    Returns:
        Contextual suggestion string
    """
    suggestions = {
        "breakfast": "Start your day with protein and complex carbs",
        "lunch": "Keep it balanced to maintain afternoon energy",
        "dinner": "Lighter portions help with better sleep",
        "snack": "Choose nutrient-dense options for sustained energy"
    }
    return suggestions.get(meal_type, "Enjoy your meal!")