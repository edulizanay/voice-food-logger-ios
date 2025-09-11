# ABOUTME: Script to clean duplicate weight entries from database
# ABOUTME: Ensures only one weight entry per day by keeping the latest entry

import os
import sys
from datetime import datetime, date
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "shared"))

from supabase_storage import _get_supabase_client

def analyze_duplicate_weights():
    """Analyze current weight entries to identify duplicates"""
    try:
        supabase = _get_supabase_client()
        
        # Get all weight entries ordered by date
        result = supabase.table("weight_entries") \
            .select("id, weight_kg, created_at") \
            .order("created_at", desc=False) \
            .execute()
        
        entries = result.data
        print(f"📊 Total weight entries found: {len(entries)}")
        
        if not entries:
            print("No weight entries to analyze")
            return [], []
        
        # Group entries by date (just the date part, ignoring time)
        entries_by_date = defaultdict(list)
        
        for entry in entries:
            # Extract date part from timestamp
            entry_date = entry["created_at"].split("T")[0]
            entries_by_date[entry_date].append(entry)
        
        # Find duplicates 
        duplicates = []
        to_keep = []
        
        for entry_date, date_entries in entries_by_date.items():
            if len(date_entries) > 1:
                print(f"📅 {entry_date}: {len(date_entries)} entries found")
                
                # Sort by created_at timestamp to keep the latest one
                date_entries.sort(key=lambda x: x["created_at"])
                
                # Keep the latest entry, mark others for deletion
                latest_entry = date_entries[-1]
                older_entries = date_entries[:-1]
                
                to_keep.append(latest_entry)
                duplicates.extend(older_entries)
                
                print(f"  ✅ Keeping: ID {latest_entry['id']} - {latest_entry['weight_kg']}kg at {latest_entry['created_at']}")
                for old_entry in older_entries:
                    print(f"  🗑️  Deleting: ID {old_entry['id']} - {old_entry['weight_kg']}kg at {old_entry['created_at']}")
            else:
                # Single entry for this date - keep it
                to_keep.append(date_entries[0])
        
        print(f"\n📈 Summary:")
        print(f"  - Total entries: {len(entries)}")
        print(f"  - Unique dates: {len(entries_by_date)}")
        print(f"  - Entries to keep: {len(to_keep)}")
        print(f"  - Duplicate entries to delete: {len(duplicates)}")
        
        return duplicates, to_keep
        
    except Exception as e:
        print(f"❌ Error analyzing duplicate weights: {e}")
        return [], []

def delete_duplicate_weights(duplicates: list) -> int:
    """Delete duplicate weight entries"""
    if not duplicates:
        print("No duplicates to delete")
        return 0
    
    try:
        supabase = _get_supabase_client()
        deleted_count = 0
        
        for entry in duplicates:
            try:
                result = supabase.table("weight_entries") \
                    .delete() \
                    .eq("id", entry["id"]) \
                    .execute()
                
                if result.data:
                    deleted_count += 1
                    print(f"  ✅ Deleted ID {entry['id']}: {entry['weight_kg']}kg from {entry['created_at']}")
                else:
                    print(f"  ❌ Failed to delete ID {entry['id']}")
            except Exception as e:
                print(f"  ❌ Error deleting ID {entry['id']}: {e}")
        
        print(f"\n🎉 Successfully deleted {deleted_count} duplicate weight entries")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error deleting duplicates: {e}")
        return 0

def main():
    print("🔍 Analyzing duplicate weight entries...")
    
    # Step 1: Analyze duplicates
    duplicates, to_keep = analyze_duplicate_weights()
    
    if not duplicates:
        print("✅ No duplicate weight entries found - database is clean!")
        return
    
    # Step 2: Auto-proceed with deletion (Edu authorized this in the requirements)
    print(f"\n✅ Proceeding to delete {len(duplicates)} duplicate entries automatically.")
    print("This will keep the latest entry for each date and delete older ones.")
    
    # Step 3: Delete duplicates
    print("\n🗑️  Deleting duplicate weight entries...")
    deleted_count = delete_duplicate_weights(duplicates)
    
    # Step 4: Verify cleanup
    print("\n🔍 Verifying cleanup...")
    remaining_duplicates, _ = analyze_duplicate_weights()
    
    if not remaining_duplicates:
        print("✅ Weight entries cleaned successfully - no duplicates remaining!")
    else:
        print(f"⚠️  Warning: {len(remaining_duplicates)} duplicates still remain")

if __name__ == "__main__":
    main()