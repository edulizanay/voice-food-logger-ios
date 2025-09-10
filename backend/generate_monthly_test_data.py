#!/usr/bin/env python3
"""
Script to generate a month of test data for weight and calorie tracking.
Creates realistic test data going backwards from today for testing the iOS app.
"""

import requests
import json
from datetime import datetime, timedelta
import random
import time

# Configuration
BASE_URL = "http://localhost:5001"
DAYS_BACK = 30

def generate_weight_data():
    """Generate realistic weight data with slight daily variations."""
    print("🏋️ Generating monthly weight data...")
    
    # Starting weight (kg)
    base_weight = 72.0
    
    # Weight goal
    goals_response = requests.get(f"{BASE_URL}/api/user-goals")
    if goals_response.status_code == 200:
        goals_data = goals_response.json()
        if goals_data.get('data'):
            goal_weight = goals_data['data'].get('weight_goal_kg', 70.0)
        else:
            goal_weight = 70.0
    else:
        goal_weight = 70.0
        
    print(f"   Target weight: {goal_weight} kg")
    print(f"   Starting weight: {base_weight} kg")
    
    # Generate daily weight entries going backwards
    current_weight = base_weight
    entries_created = 0
    
    for days_ago in range(DAYS_BACK):
        # Calculate date
        entry_date = datetime.now() - timedelta(days=days_ago)
        date_str = entry_date.strftime("%Y-%m-%d")
        
        # Add realistic daily weight variation (-0.3 to +0.3 kg)
        daily_variation = random.uniform(-0.3, 0.3)
        
        # Add slight downward trend (0.02 kg per day toward goal)
        if current_weight > goal_weight:
            trend = -0.02
        else:
            trend = 0.01
            
        current_weight += daily_variation + trend
        
        # Keep weight within reasonable bounds
        current_weight = max(65.0, min(80.0, current_weight))
        
        # Create weight entry
        weight_data = {
            "weight_kg": round(current_weight, 1),
            "date": date_str,
            "notes": f"Generated test data for {date_str}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/weight-entries", json=weight_data)
            if response.status_code == 200:
                entries_created += 1
                if days_ago % 5 == 0:  # Progress indicator
                    print(f"   ✅ {date_str}: {current_weight:.1f} kg")
            else:
                print(f"   ❌ Failed to create weight entry for {date_str}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating weight entry for {date_str}: {e}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print(f"✅ Created {entries_created} weight entries")

def generate_calorie_data():
    """Generate realistic daily calorie intake data."""
    print("🍎 Generating monthly calorie data...")
    
    # Get calorie goal
    goals_response = requests.get(f"{BASE_URL}/api/user-goals")
    if goals_response.status_code == 200:
        goals_data = goals_response.json()
        if goals_data.get('data'):
            goal_calories = goals_data['data'].get('calorie_goal', 1800)
        else:
            goal_calories = 1800
    else:
        goal_calories = 1800
        
    print(f"   Target calories: {goal_calories} per day")
    
    entries_created = 0
    
    for days_ago in range(DAYS_BACK):
        # Calculate date  
        entry_date = datetime.now() - timedelta(days=days_ago)
        date_str = entry_date.strftime("%Y-%m-%d")
        timestamp = entry_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Generate realistic calorie intake (80% to 120% of goal)
        intake_variation = random.uniform(0.8, 1.2)
        daily_calories = int(goal_calories * intake_variation)
        
        # Calculate macros (roughly realistic proportions)
        protein_ratio = random.uniform(0.15, 0.25)  # 15-25% protein
        fat_ratio = random.uniform(0.25, 0.35)      # 25-35% fat  
        carb_ratio = 1.0 - protein_ratio - fat_ratio # Rest carbs
        
        protein_g = round((daily_calories * protein_ratio) / 4, 1)  # 4 cal/g
        fat_g = round((daily_calories * fat_ratio) / 9, 1)          # 9 cal/g
        carbs_g = round((daily_calories * carb_ratio) / 4, 1)       # 4 cal/g
        
        # Create food entry data
        food_items = [
            {
                "food": f"Daily meal summary for {date_str}",
                "quantity": "1 day",
                "macros": {
                    "calories": daily_calories,
                    "protein_g": protein_g,
                    "carbs_g": carbs_g,
                    "fat_g": fat_g
                }
            }
        ]
        
        entry_data = {
            "timestamp": timestamp,
            "items": food_items,
            "meal_type": "daily_summary",
            "meal_emoji": "📊"
        }
        
        try:
            # Use the existing entries endpoint 
            response = requests.post(f"{BASE_URL}/api/entries", json=entry_data)
            if response.status_code == 200:
                entries_created += 1
                if days_ago % 5 == 0:  # Progress indicator
                    print(f"   ✅ {date_str}: {daily_calories} cal (P: {protein_g}g, C: {carbs_g}g, F: {fat_g}g)")
            else:
                print(f"   ❌ Failed to create calorie entry for {date_str}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating calorie entry for {date_str}: {e}")
            
        time.sleep(0.1)
    
    print(f"✅ Created {entries_created} calorie entries")

def check_server_health():
    """Check if the backend server is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return False

def main():
    print("📊 Generating Monthly Test Data")
    print("=" * 40)
    
    # Check server health
    if not check_server_health():
        print("❌ Server is not available. Please start the backend server first.")
        return
        
    print(f"📅 Generating data for {DAYS_BACK} days back from today")
    print()
    
    # Generate weight data
    generate_weight_data()
    print()
    
    # Generate calorie data  
    generate_calorie_data()
    print()
    
    print("🎉 Monthly test data generation complete!")
    print("📱 You can now test the iOS app with realistic monthly data")

if __name__ == "__main__":
    main()