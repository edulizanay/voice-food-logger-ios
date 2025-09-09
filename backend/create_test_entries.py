#!/usr/bin/env python3
"""
Create test entries for testing delete/edit functionality
"""

import sys
import os
from datetime import datetime

# Add shared directory to path
sys.path.append('shared')

from supabase_storage import store_food_data

def create_test_entries():
    """Create a few test entries with different meal types"""
    
    print("Creating test entries...")
    
    # Test entry 1: Breakfast
    breakfast_items = [
        {
            "food": "scrambled eggs",
            "quantity": "2 eggs",
            "macros": {"calories": 140, "protein_g": 12.0, "carbs_g": 1.0, "fat_g": 10.0}
        },
        {
            "food": "toast",
            "quantity": "2 slices", 
            "macros": {"calories": 160, "protein_g": 4.0, "carbs_g": 30.0, "fat_g": 2.0}
        }
    ]
    
    # Test entry 2: Lunch  
    lunch_items = [
        {
            "food": "grilled chicken",
            "quantity": "200g",
            "macros": {"calories": 308, "protein_g": 58.0, "carbs_g": 0.0, "fat_g": 6.7}
        },
        {
            "food": "brown rice",
            "quantity": "150g cooked",
            "macros": {"calories": 165, "protein_g": 3.4, "carbs_g": 33.0, "fat_g": 1.2}
        }
    ]
    
    # Test entry 3: Snack
    snack_items = [
        {
            "food": "banana",
            "quantity": "1 medium",
            "macros": {"calories": 105, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.3}
        }
    ]
    
    try:
        # Store the test entries
        store_food_data(breakfast_items)
        print("✅ Created breakfast entry (eggs + toast)")
        
        store_food_data(lunch_items) 
        print("✅ Created lunch entry (chicken + rice)")
        
        store_food_data(snack_items)
        print("✅ Created snack entry (banana)")
        
        print("\n🎉 Test entries created successfully!")
        print("You can now test delete and edit functionality in your iOS app.")
        
    except Exception as e:
        print(f"❌ Error creating test entries: {e}")

if __name__ == "__main__":
    create_test_entries()