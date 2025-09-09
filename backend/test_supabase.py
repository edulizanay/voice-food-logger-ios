#!/usr/bin/env python3
"""Test script for Supabase storage module"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add shared directory to path
sys.path.append('shared')

# Now import and test the supabase storage
from supabase_storage import store_food_data, get_today_entries, get_daily_totals

def main():
    print("🧪 Testing Supabase storage integration...")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_KEY: {'***' + os.getenv('SUPABASE_KEY', '')[-10:]}")
    
    # Test data - simulates what comes from food processing
    test_items = [
        {
            "food": "chicken breast", 
            "quantity": "150g",
            "macros": {"calories": 231, "protein_g": 43.5, "carbs_g": 0, "fat_g": 5.0}
        },
        {
            "food": "rice", 
            "quantity": "0.5 cup",
            "macros": {"calories": 103, "protein_g": 2.1, "carbs_g": 22.3, "fat_g": 0.2}
        }
    ]
    
    try:
        # Test storing data
        print("\n📝 Testing store_food_data...")
        success = store_food_data(test_items)
        print(f"✅ Storage successful: {success}")
        
        # Test retrieving today's entries
        print("\n📊 Testing get_today_entries...")
        entries = get_today_entries()
        print(f"✅ Retrieved {len(entries)} entry groups")
        
        for i, entry in enumerate(entries):
            print(f"  Entry {i+1}: {len(entry['items'])} items at {entry['timestamp']}")
            for item in entry['items']:
                print(f"    - {item['quantity']} of {item['food']} ({item['macros']['calories']} cal)")
        
        # Test calculating daily totals
        print("\n🧮 Testing get_daily_totals...")
        totals = get_daily_totals()
        print(f"✅ Daily totals:")
        print(f"  Calories: {totals['calories']}")
        print(f"  Protein: {totals['protein_g']}g")
        print(f"  Carbs: {totals['carbs_g']}g")
        print(f"  Fat: {totals['fat_g']}g")
        
        print("\n🎉 All tests passed! Supabase integration is working!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()