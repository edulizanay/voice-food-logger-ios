"""
Test suite for storage functionality.
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime
from storage import store_food_data, get_today_entries, get_daily_totals, _calculate_daily_totals


class TestStorage(unittest.TestCase):
    """Test cases for food data storage."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_store_food_data(self):
        """Test storing food entry data."""
        food_items = [
            {
                "food": "banana",
                "quantity": "1 piece",
                "macros": {"calories": 105, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.3}
            }
        ]
        
        test_time = datetime(2025, 1, 15, 8, 30)  # Breakfast time
        result = store_food_data(food_items, test_time)
        
        self.assertTrue(result)
        
        # Check if file was created
        expected_file = "logs/logs_2025-01-15.json"
        self.assertTrue(os.path.exists(expected_file))
        
        # Check file contents
        with open(expected_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("entries", data)
        self.assertIn("daily_macros", data)
        self.assertEqual(len(data["entries"]), 1)
        
        entry = data["entries"][0]
        self.assertIn("id", entry)
        self.assertIn("meal_type", entry)
        self.assertIn("meal_emoji", entry)
        self.assertEqual(entry["meal_type"], "breakfast")
        self.assertEqual(entry["meal_emoji"], "🌅")
        self.assertEqual(entry["items"], food_items)
    
    def test_calculate_daily_totals(self):
        """Test daily macro calculation."""
        entries = [
            {
                "items": [
                    {"food": "banana", "macros": {"calories": 105, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.3}},
                    {"food": "apple", "macros": {"calories": 95, "protein_g": 0.5, "carbs_g": 25.0, "fat_g": 0.3}}
                ]
            }
        ]
        
        totals = _calculate_daily_totals(entries)
        
        self.assertEqual(totals["calories"], 200)
        self.assertEqual(totals["protein_g"], 1.8)
        self.assertEqual(totals["carbs_g"], 52.0)
        self.assertEqual(totals["fat_g"], 0.6)
    
    def test_get_today_entries_empty(self):
        """Test retrieving entries when no data exists."""
        entries = get_today_entries()
        self.assertEqual(entries, [])
    
    def test_get_daily_totals_empty(self):
        """Test retrieving totals when no data exists."""
        totals = get_daily_totals()
        expected = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
        self.assertEqual(totals, expected)
    
    def test_store_multiple_entries(self):
        """Test storing multiple entries in the same day."""
        # Store breakfast
        breakfast_items = [
            {"food": "oatmeal", "macros": {"calories": 150, "protein_g": 5.0, "carbs_g": 30.0, "fat_g": 3.0}}
        ]
        breakfast_time = datetime(2025, 1, 15, 8, 0)
        store_food_data(breakfast_items, breakfast_time)
        
        # Store lunch
        lunch_items = [
            {"food": "chicken salad", "macros": {"calories": 300, "protein_g": 25.0, "carbs_g": 10.0, "fat_g": 15.0}}
        ]
        lunch_time = datetime(2025, 1, 15, 12, 30)
        store_food_data(lunch_items, lunch_time)
        
        # Check file contents
        log_file = "logs/logs_2025-01-15.json"
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data["entries"]), 2)
        
        # Check totals
        expected_totals = {
            "calories": 450,
            "protein_g": 30.0,
            "carbs_g": 40.0,
            "fat_g": 18.0
        }
        self.assertEqual(data["daily_macros"], expected_totals)
    
    def test_meal_type_detection_integration(self):
        """Test that meal types are correctly assigned based on time."""
        test_cases = [
            (datetime(2025, 1, 15, 7, 0), "breakfast", "🌅"),
            (datetime(2025, 1, 15, 12, 0), "lunch", "☀️"),
            (datetime(2025, 1, 15, 19, 0), "dinner", "🌙"),
            (datetime(2025, 1, 15, 16, 0), "snack", "🍿"),
        ]
        
        for test_time, expected_meal, expected_emoji in test_cases:
            food_items = [{"food": "test", "macros": {"calories": 100, "protein_g": 1, "carbs_g": 1, "fat_g": 1}}]
            store_food_data(food_items, test_time)
            
            # Get the log file for this date
            log_file = f"logs/logs_{test_time.strftime('%Y-%m-%d')}.json"
            with open(log_file, 'r') as f:
                data = json.load(f)
            
            # Check the last entry (most recent)
            entry = data["entries"][-1]
            self.assertEqual(entry["meal_type"], expected_meal, 
                           f"Expected {expected_meal} for time {test_time.hour}:00")
            self.assertEqual(entry["meal_emoji"], expected_emoji,
                           f"Expected {expected_emoji} for time {test_time.hour}:00")


if __name__ == '__main__':
    unittest.main()