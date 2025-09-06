#!/usr/bin/env python3
"""
Simple test for storage module
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import store_food_data, get_today_entries

def test_storage():
    """Test food data storage"""
    test_items = [
        {"food": "chicken breast", "quantity": "150 grams"},
        {"food": "rice", "quantity": "0.5 cup"}
    ]
    
    try:
        print("📋 Testing food data storage...")
        
        # Test storing data
        success = store_food_data(test_items)
        if not success:
            print("❌ Storage failed")
            return False
        
        print("✅ Storage successful!")
        
        # Test retrieving data
        entries = get_today_entries()
        print(f"Retrieved {len(entries)} entries for today:")
        
        for entry in entries:
            print(f"  {entry['timestamp']}: {len(entry['items'])} items")
            for item in entry['items']:
                print(f"    - {item['food']}: {item['quantity']}")
        
        print(f"\n✅ Storage test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_storage()
    exit(0 if success else 1)