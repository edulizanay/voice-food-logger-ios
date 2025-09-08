import json
import os
import uuid
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
    
    # Create entry with unique ID
    entry = {
        "id": str(uuid.uuid4()),
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

def delete_entry(entry_id: str) -> bool:
    """
    Delete a food entry by its ID
    
    Args:
        entry_id: UUID string of the entry to delete
        
    Returns:
        True if deleted successfully, False if entry not found
    """
    today = datetime.now()
    filename = f"logs_{today.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict) or 'entries' not in data:
                return False
                
            entries = data['entries']
            # Find and remove entry with matching ID
            original_count = len(entries)
            entries = [entry for entry in entries if entry.get('id') != entry_id]
            
            if len(entries) == original_count:
                return False  # Entry not found
            
            # Recalculate daily totals
            daily_totals = _calculate_daily_totals(entries)
            updated_data = {
                "entries": entries,
                "daily_macros": daily_totals
            }
            
            # Save updated data
            with open(filepath, 'w') as file:
                json.dump(updated_data, file, indent=2)
            
            print(f"Deleted entry with ID {entry_id}")
            return True
            
        except json.JSONDecodeError:
            return False

def update_entry_quantity(entry_id: str, new_quantity: str) -> bool:
    """
    Update the quantity of a food entry by its ID
    
    Args:
        entry_id: UUID string of the entry to update
        new_quantity: New quantity string (e.g., "200g")
        
    Returns:
        True if updated successfully, False if entry not found
    """
    today = datetime.now()
    filename = f"logs_{today.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict) or 'entries' not in data:
                return False
                
            entries = data['entries']
            entry_found = False
            
            # Find and update entry with matching ID
            for entry in entries:
                if entry.get('id') == entry_id:
                    if 'items' in entry and len(entry['items']) > 0:
                        # Update quantity of the first (and typically only) item
                        entry['items'][0]['quantity'] = new_quantity
                        entry_found = True
                        break
            
            if not entry_found:
                return False
            
            # Re-process the entry to recalculate macros
            # Import processing here to avoid circular imports
            from processing import process_food_text
            
            # Create a text representation for reprocessing
            food_name = entry['items'][0]['food']
            text_for_processing = f"{new_quantity} of {food_name}"
            
            try:
                # Reprocess to get new macros
                processed_data = process_food_text(text_for_processing)
                if processed_data['items']:
                    # Update the entry with new macros
                    entry['items'][0]['macros'] = processed_data['items'][0].get('macros')
            except Exception as e:
                print(f"Warning: Could not recalculate macros for updated quantity: {e}")
                # Continue without macro update
            
            # Recalculate daily totals
            daily_totals = _calculate_daily_totals(entries)
            updated_data = {
                "entries": entries,
                "daily_macros": daily_totals
            }
            
            # Save updated data
            with open(filepath, 'w') as file:
                json.dump(updated_data, file, indent=2)
            
            print(f"Updated entry {entry_id} with new quantity: {new_quantity}")
            return True
            
        except json.JSONDecodeError:
            return False

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