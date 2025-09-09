import os
import uuid
from datetime import datetime
from supabase import create_client, Client
from meal_detection import detect_meal_time, get_meal_emoji

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def _get_supabase_client():
    """Get initialized Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def _calculate_daily_totals(entries: list) -> dict:
    """Calculate total macros for all entries in a day (same as original)"""
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
    Store food logging entry to Supabase database
    
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
    
    # Generate session ID to group items from same recording
    session_id = str(uuid.uuid4())
    
    # Detect meal type based on timestamp
    meal_type = detect_meal_time(timestamp)
    meal_emoji = get_meal_emoji(meal_type)
    
    try:
        supabase = _get_supabase_client()
        
        # Prepare rows for database - each food item gets its own row
        rows = []
        for item in food_items:
            macros = item.get('macros', {})
            row = {
                "food_name": item.get("food"),
                "quantity": item.get("quantity"),
                "calories": macros.get("calories"),
                "protein": macros.get("protein_g"),
                "carbs": macros.get("carbs_g"),
                "fat": macros.get("fat_g"),
                "session_id": session_id,
                "created_at": timestamp.isoformat()
            }
            rows.append(row)
        
        # Insert all rows at once
        result = supabase.table("food_entries").insert(rows).execute()
        
        print(f"Stored food entry with {len(food_items)} items to Supabase (session: {session_id})")
        return True
        
    except Exception as e:
        print(f"Error storing to Supabase: {e}")
        raise

def get_today_entries() -> list:
    """Get all food entries for today, grouped by session"""
    try:
        supabase = _get_supabase_client()
        today = datetime.now().date()
        
        # Query today's entries
        result = supabase.table("food_entries") \
            .select("*") \
            .gte("created_at", f"{today}T00:00:00") \
            .lte("created_at", f"{today}T23:59:59") \
            .order("created_at", desc=False) \
            .execute()
        
        # Group by session_id to maintain UI compatibility
        sessions = {}
        for row in result.data:
            session_id = row.get("session_id")
            
            # Handle entries without session_id (fallback to individual entries)
            if not session_id:
                session_id = str(row["id"])
            
            if session_id not in sessions:
                sessions[session_id] = {
                    "id": session_id,
                    "timestamp": row["created_at"],
                    "meal_type": detect_meal_time(datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))),
                    "meal_emoji": "",  # Will be set below
                    "items": []
                }
            
            # Add item to session
            sessions[session_id]["items"].append({
                "food": row["food_name"],
                "quantity": row["quantity"],
                "macros": {
                    "calories": row["calories"] or 0,
                    "protein_g": row["protein"] or 0,
                    "carbs_g": row["carbs"] or 0,
                    "fat_g": row["fat"] or 0
                }
            })
        
        # Set meal emoji for each session
        for session in sessions.values():
            session["meal_emoji"] = get_meal_emoji(session["meal_type"])
        
        # Return as list for UI compatibility
        return list(sessions.values())
        
    except Exception as e:
        print(f"Error retrieving today's entries: {e}")
        return []

def get_daily_totals() -> dict:
    """Get daily macro totals for today"""
    try:
        supabase = _get_supabase_client()
        today = datetime.now().date()
        
        # Query today's entries and calculate totals
        result = supabase.table("food_entries") \
            .select("calories, protein, carbs, fat") \
            .gte("created_at", f"{today}T00:00:00") \
            .lte("created_at", f"{today}T23:59:59") \
            .execute()
        
        totals = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0
        }
        
        for row in result.data:
            totals["calories"] += row.get("calories") or 0
            totals["protein_g"] += row.get("protein") or 0
            totals["carbs_g"] += row.get("carbs") or 0
            totals["fat_g"] += row.get("fat") or 0
        
        # Round the totals
        return {
            "calories": round(totals["calories"]),
            "protein_g": round(totals["protein_g"], 1),
            "carbs_g": round(totals["carbs_g"], 1),
            "fat_g": round(totals["fat_g"], 1)
        }
        
    except Exception as e:
        print(f"Error calculating daily totals: {e}")
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

def get_entries_by_date(date: str) -> list:
    """Get food entries for a specific date (YYYY-MM-DD format)"""
    try:
        supabase = _get_supabase_client()
        
        # Query entries for specific date
        result = supabase.table("food_entries") \
            .select("*") \
            .gte("created_at", f"{date}T00:00:00") \
            .lte("created_at", f"{date}T23:59:59") \
            .order("created_at", desc=False) \
            .execute()
        
        # Group by session_id
        sessions = {}
        for row in result.data:
            session_id = row.get("session_id", str(row["id"]))
            
            if session_id not in sessions:
                sessions[session_id] = {
                    "id": session_id,
                    "timestamp": row["created_at"],
                    "meal_type": detect_meal_time(datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))),
                    "items": []
                }
            
            sessions[session_id]["items"].append({
                "food": row["food_name"],
                "quantity": row["quantity"],
                "macros": {
                    "calories": row["calories"] or 0,
                    "protein_g": row["protein"] or 0,
                    "carbs_g": row["carbs"] or 0,
                    "fat_g": row["fat"] or 0
                }
            })
        
        return list(sessions.values())
        
    except Exception as e:
        print(f"Error retrieving entries for {date}: {e}")
        return []

def get_daily_totals_by_date(date: str) -> dict:
    """Get daily macro totals for a specific date (YYYY-MM-DD format)"""
    try:
        supabase = _get_supabase_client()
        
        # Query entries for specific date and calculate totals
        result = supabase.table("food_entries") \
            .select("calories, protein, carbs, fat") \
            .gte("created_at", f"{date}T00:00:00") \
            .lte("created_at", f"{date}T23:59:59") \
            .execute()
        
        totals = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0
        }
        
        for row in result.data:
            totals["calories"] += row.get("calories") or 0
            totals["protein_g"] += row.get("protein") or 0
            totals["carbs_g"] += row.get("carbs") or 0
            totals["fat_g"] += row.get("fat") or 0
        
        return {
            "calories": round(totals["calories"]),
            "protein_g": round(totals["protein_g"], 1),
            "carbs_g": round(totals["carbs_g"], 1),
            "fat_g": round(totals["fat_g"], 1)
        }
        
    except Exception as e:
        print(f"Error calculating daily totals for {date}: {e}")
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

def delete_entry(entry_id: str) -> bool:
    """
    Delete a food entry by its session ID or individual ID
    
    Args:
        entry_id: Session ID or individual entry ID to delete
        
    Returns:
        True if deleted successfully, False if entry not found
    """
    try:
        supabase = _get_supabase_client()
        
        # First try to delete by session_id (for grouped entries)
        result = supabase.table("food_entries") \
            .delete() \
            .eq("session_id", entry_id) \
            .execute()
        
        if result.data:
            print(f"Deleted session with ID {entry_id}")
            return True
        
        # If no session found, try individual entry ID
        result = supabase.table("food_entries") \
            .delete() \
            .eq("id", entry_id) \
            .execute()
        
        if result.data:
            print(f"Deleted individual entry with ID {entry_id}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error deleting entry {entry_id}: {e}")
        return False

def update_entry_quantity(entry_id: str, new_quantity: str) -> bool:
    """
    Update the quantity of a food entry by its ID
    
    Args:
        entry_id: Session ID or individual entry ID to update
        new_quantity: New quantity string (e.g., "200g")
        
    Returns:
        True if updated successfully, False if entry not found
    """
    try:
        supabase = _get_supabase_client()
        
        # For now, just update the quantity - macro recalculation could be added later
        result = supabase.table("food_entries") \
            .update({"quantity": new_quantity}) \
            .eq("id", entry_id) \
            .execute()
        
        if result.data:
            print(f"Updated entry {entry_id} with new quantity: {new_quantity}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error updating entry {entry_id}: {e}")
        return False

if __name__ == "__main__":
    # Test the storage system
    test_items = [
        {
            "food": "chicken breast", 
            "quantity": "150 grams",
            "macros": {"calories": 231, "protein_g": 43.5, "carbs_g": 0, "fat_g": 5.0}
        },
        {
            "food": "rice", 
            "quantity": "0.5 cup",
            "macros": {"calories": 103, "protein_g": 2.1, "carbs_g": 22.3, "fat_g": 0.2}
        }
    ]
    
    try:
        print("Testing Supabase storage...")
        store_food_data(test_items)
        entries = get_today_entries()
        print(f"Retrieved {len(entries)} entries for today")
        for entry in entries:
            print(f"  {entry['timestamp']}: {len(entry['items'])} items")
        
        totals = get_daily_totals()
        print(f"Daily totals: {totals}")
        
    except Exception as e:
        print(f"Error: {e}")