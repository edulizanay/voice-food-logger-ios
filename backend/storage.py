import json
import os
from datetime import datetime

def _calculate_daily_totals(entries: list) -> dict:
    """Calculate total macros for all entries in a day"""
    totals = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0
    }
    
    for entry in entries:
        if 'items' in entry:
            for item in entry['items']:
                if 'macros' in item:
                    macros = item['macros']
                    totals["calories"] += macros.get("calories", 0)
                    totals["protein_g"] += macros.get("protein_g", 0)
                    totals["carbs_g"] += macros.get("carbs_g", 0)
                    totals["fat_g"] += macros.get("fat_g", 0)
    
    # Round the totals
    return {
        "calories": round(totals["calories"]),
        "protein_g": round(totals["protein_g"], 1),
        "carbs_g": round(totals["carbs_g"], 1),
        "fat_g": round(totals["fat_g"], 1)
    }

def store_food_data(food_items: list, timestamp: datetime = None) -> bool:
    """
    Store food logging entry to daily JSON file
    
    Args:
        food_items: List of food items with 'food' and 'quantity' keys
        timestamp: When the food was consumed (defaults to now)
        
    Returns:
        True if stored successfully
        
    Raises:
        Exception: If storage fails
    """
    if not food_items:
        raise ValueError("food_items cannot be empty")
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create entry
    entry = {
        "timestamp": timestamp.isoformat(),
        "items": food_items
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get daily log file path
    filename = f"logs_{timestamp.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    # Load existing entries or create new list
    entries = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
            # Handle both old format (list) and new format (dict with entries)
            if isinstance(data, list):
                entries = data  # Old format - direct list of entries
            elif isinstance(data, dict) and 'entries' in data:
                entries = data['entries']  # New format - entries within dict
            else:
                entries = [data]  # Single entry
    
    # Add new entry
    entries.append(entry)
    
    # Calculate daily totals and create the data structure
    daily_totals = _calculate_daily_totals(entries)
    daily_data = {
        "entries": entries,
        "daily_macros": daily_totals
    }
    
    # Save updated entries with daily totals
    with open(filepath, 'w') as file:
        json.dump(daily_data, file, indent=2)
    
    print(f"Stored food entry with {len(food_items)} items to {filepath}")
    return True

def get_today_entries() -> list:
    """Get all food entries for today"""
    today = datetime.now()
    filename = f"logs_{today.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return []
    
    # Check if file is empty
    if os.path.getsize(filepath) == 0:
        return []
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            # Handle both old format (list) and new format (dict with entries)
            if isinstance(data, list):
                return data  # Old format - direct list of entries
            elif isinstance(data, dict) and 'entries' in data:
                return data['entries']  # New format - entries within dict
            else:
                return [data]  # Single entry
        except json.JSONDecodeError:
            return []

def get_daily_totals() -> dict:
    """Get daily macro totals for today"""
    today = datetime.now()
    filename = f"logs_{today.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    
    # Check if file is empty
    if os.path.getsize(filepath) == 0:
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            
            # If new format with daily_macros, return those
            if isinstance(data, dict) and 'daily_macros' in data:
                return data['daily_macros']
            
            # Otherwise calculate from entries (backward compatibility)
            entries = []
            if isinstance(data, list):
                entries = data  # Old format - direct list of entries
            elif isinstance(data, dict) and 'entries' in data:
                entries = data['entries']  # New format - entries within dict
            else:
                entries = [data]  # Single entry
                
            return _calculate_daily_totals(entries)
            
        except json.JSONDecodeError:
            return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

def get_entries_by_date(date: str) -> list:
    """Get food entries for a specific date (YYYY-MM-DD format)"""
    filename = f"logs_{date}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return []
    
    # Check if file is empty
    if os.path.getsize(filepath) == 0:
        return []
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            
            # Handle different data formats
            if isinstance(data, list):
                return data  # Old format - direct list of entries
            elif isinstance(data, dict) and 'entries' in data:
                return data['entries']  # New format - entries within dict
            else:
                return [data]  # Single entry
                
        except json.JSONDecodeError:
            return []

def get_daily_totals_by_date(date: str) -> dict:
    """Get daily macro totals for a specific date (YYYY-MM-DD format)"""
    filename = f"logs_{date}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    
    # Check if file is empty
    if os.path.getsize(filepath) == 0:
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            
            # If new format with daily_macros, return those
            if isinstance(data, dict) and 'daily_macros' in data:
                return data['daily_macros']
            
            # Otherwise calculate from entries (backward compatibility)
            entries = []
            if isinstance(data, list):
                entries = data  # Old format - direct list of entries
            elif isinstance(data, dict) and 'entries' in data:
                entries = data['entries']  # New format - entries within dict
            else:
                entries = [data]  # Single entry
                
            return _calculate_daily_totals(entries)
            
        except json.JSONDecodeError:
            return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

if __name__ == "__main__":
    # Test the storage system
    test_items = [
        {"food": "chicken breast", "quantity": "150 grams"},
        {"food": "rice", "quantity": "0.5 cup"}
    ]
    
    try:
        store_food_data(test_items)
        entries = get_today_entries()
        print(f"Retrieved {len(entries)} entries for today")
        for entry in entries:
            print(f"  {entry['timestamp']}: {len(entry['items'])} items")
    except Exception as e:
        print(f"Error: {e}")