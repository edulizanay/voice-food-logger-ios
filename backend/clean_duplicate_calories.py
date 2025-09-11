# ABOUTME: Script to clean duplicate calorie entries from database  
# ABOUTME: Ensures only one calorie entry per day by aggregating multiple entries for past 7 days

import os
import sys
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "shared"))

from supabase_storage import _get_supabase_client

def analyze_duplicate_calories(days_back=7):
    """Analyze current food entries to identify duplicates for past N days"""
    try:
        supabase = _get_supabase_client()
        
        # Calculate date range (past N days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"📊 Analyzing calorie entries from {start_date} to {end_date} ({days_back} days)")
        
        # First check what columns are available by selecting everything
        sample_result = supabase.table("food_entries") \
            .select("*") \
            .limit(1) \
            .execute()
        
        if sample_result.data:
            print(f"Available columns: {list(sample_result.data[0].keys())}")
        
        # Get all food entries in date range with available columns
        result = supabase.table("food_entries") \
            .select("*") \
            .gte("created_at", f"{start_date}T00:00:00") \
            .lte("created_at", f"{end_date}T23:59:59") \
            .order("created_at", desc=False) \
            .execute()
        
        entries = result.data
        print(f"📊 Total food entries found: {len(entries)}")
        
        if not entries:
            print("No food entries to analyze")
            return [], [], {}
        
        # Group entries by date (just the date part, ignoring time)
        entries_by_date = defaultdict(list)
        
        for entry in entries:
            # Extract date part from timestamp  
            entry_date = entry["created_at"].split("T")[0]
            entries_by_date[entry_date].append(entry)
        
        # Show summary for each date
        print(f"\n📈 Daily breakdown:")
        daily_totals = {}
        
        for entry_date, date_entries in sorted(entries_by_date.items()):
            # Calculate daily totals
            total_calories = sum(entry.get("calories", 0) for entry in date_entries)
            total_protein = sum(entry.get("protein", 0) for entry in date_entries)
            total_carbs = sum(entry.get("carbs", 0) for entry in date_entries)
            total_fat = sum(entry.get("fat", 0) for entry in date_entries)
            
            daily_totals[entry_date] = {
                "calories": total_calories,
                "protein": total_protein, 
                "carbs": total_carbs,
                "fat": total_fat,
                "entry_count": len(date_entries)
            }
            
            print(f"📅 {entry_date}: {len(date_entries)} entries, {total_calories} cal, {total_protein:.1f}g protein")
            
            # Show individual entries for dates with multiple entries
            if len(date_entries) > 1:
                for entry in date_entries:
                    print(f"  - ID {entry['id']}: {entry.get('food_name', 'Unknown')} ({entry.get('quantity', '')}) - {entry.get('calories', 0)} cal")
        
        # For calorie tracking, we want to aggregate multiple entries per day into single daily totals
        # Rather than delete duplicates, we should create daily summary entries
        
        # Find dates with multiple entries that should be consolidated
        dates_to_consolidate = []
        entries_to_remove = []
        
        for entry_date, date_entries in entries_by_date.items():
            if len(date_entries) > 1:
                dates_to_consolidate.append(entry_date)
                # Keep all entries for now - we'll aggregate them into daily totals
                entries_to_remove.extend(date_entries)
        
        print(f"\n📈 Summary:")
        print(f"  - Total entries: {len(entries)}")
        print(f"  - Unique dates: {len(entries_by_date)}")
        print(f"  - Dates with multiple entries: {len(dates_to_consolidate)}")
        print(f"  - Entries that could be consolidated: {len(entries_to_remove)}")
        
        return dates_to_consolidate, entries_to_remove, daily_totals
        
    except Exception as e:
        print(f"❌ Error analyzing duplicate calories: {e}")
        return [], [], {}

def create_daily_calorie_summaries(dates_to_consolidate, daily_totals):
    """Create daily summary entries for dates with multiple entries"""
    if not dates_to_consolidate:
        print("No dates need consolidation")
        return 0
    
    try:
        supabase = _get_supabase_client()
        created_count = 0
        
        print(f"\n📝 Creating daily summary entries...")
        
        for entry_date in dates_to_consolidate:
            totals = daily_totals[entry_date]
            
            # Create a daily summary entry with proper UUID
            summary_entry = {
                "session_id": str(uuid.uuid4()),  # Generate a proper UUID
                "food_name": f"Daily Total ({entry_date})",
                "quantity": f"{totals['entry_count']} meals/snacks",
                "calories": totals["calories"],
                "protein": totals["protein"],
                "carbs": totals["carbs"],
                "fat": totals["fat"],
                "created_at": f"{entry_date}T12:00:00"  # Set to noon of that day
            }
            
            try:
                result = supabase.table("food_entries").insert(summary_entry).execute()
                
                if result.data:
                    created_count += 1
                    print(f"  ✅ Created daily summary for {entry_date}: {totals['calories']} cal, {totals['protein']:.1f}g protein")
                else:
                    print(f"  ❌ Failed to create summary for {entry_date}")
            except Exception as e:
                print(f"  ❌ Error creating summary for {entry_date}: {e}")
        
        print(f"\n🎉 Successfully created {created_count} daily summary entries")
        return created_count
        
    except Exception as e:
        print(f"❌ Error creating daily summaries: {e}")
        return 0

def remove_individual_entries(entries_to_remove):
    """Remove individual entries that have been consolidated into daily summaries"""
    if not entries_to_remove:
        print("No individual entries to remove")
        return 0
    
    try:
        supabase = _get_supabase_client()
        deleted_count = 0
        
        print(f"\n🗑️  Removing {len(entries_to_remove)} individual entries...")
        
        for entry in entries_to_remove:
            try:
                result = supabase.table("food_entries") \
                    .delete() \
                    .eq("id", entry["id"]) \
                    .execute()
                
                if result.data:
                    deleted_count += 1
                    print(f"  ✅ Deleted ID {entry['id']}: {entry.get('food_name', 'Unknown')} ({entry.get('calories', 0)} cal)")
                else:
                    print(f"  ❌ Failed to delete ID {entry['id']}")
            except Exception as e:
                print(f"  ❌ Error deleting ID {entry['id']}: {e}")
        
        print(f"\n🎉 Successfully deleted {deleted_count} individual entries")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error deleting individual entries: {e}")
        return 0

def main():
    print("🔍 Analyzing duplicate calorie entries for past 7 days...")
    
    # Step 1: Analyze current state
    dates_to_consolidate, entries_to_remove, daily_totals = analyze_duplicate_calories(days_back=7)
    
    if not dates_to_consolidate:
        print("✅ No duplicate calorie entries found - database is clean!")
        return
    
    # Step 2: Auto-proceed with consolidation (Edu authorized this in the requirements)
    print(f"\n✅ Proceeding to consolidate entries for {len(dates_to_consolidate)} dates automatically.")
    print("This will create daily summary entries and remove individual entries.")
    
    # Step 3: Create daily summaries
    print("\n📊 Creating daily summary entries...")
    created_count = create_daily_calorie_summaries(dates_to_consolidate, daily_totals)
    
    if created_count > 0:
        # Step 4: Remove individual entries
        print("\n🗑️  Removing individual entries that were consolidated...")
        deleted_count = remove_individual_entries(entries_to_remove)
        
        # Step 5: Verify cleanup
        print("\n🔍 Verifying cleanup...")
        remaining_dates, _, _ = analyze_duplicate_calories(days_back=7)
        
        if not remaining_dates:
            print("✅ Calorie entries consolidated successfully!")
        else:
            print(f"⚠️  Warning: {len(remaining_dates)} dates still have multiple entries")
    else:
        print("❌ Failed to create daily summaries - skipping individual entry deletion")

if __name__ == "__main__":
    main()