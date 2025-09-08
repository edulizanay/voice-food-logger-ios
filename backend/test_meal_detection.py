"""
Test suite for meal detection functionality.
"""

import unittest
from datetime import datetime
from meal_detection import detect_meal_time, get_meal_emoji, get_meal_display_name


class TestMealDetection(unittest.TestCase):
    """Test cases for meal time detection."""
    
    def test_breakfast_time(self):
        """Test breakfast detection."""
        # 8:30 AM
        breakfast_time = datetime(2025, 1, 1, 8, 30)
        self.assertEqual(detect_meal_time(breakfast_time), "breakfast")
        
        # Edge case: 5:00 AM (start of breakfast)
        early_breakfast = datetime(2025, 1, 1, 5, 0)
        self.assertEqual(detect_meal_time(early_breakfast), "breakfast")
        
        # Edge case: 10:59 AM (end of breakfast)
        late_breakfast = datetime(2025, 1, 1, 10, 59)
        self.assertEqual(detect_meal_time(late_breakfast), "breakfast")
    
    def test_lunch_time(self):
        """Test lunch detection."""
        # 12:30 PM
        lunch_time = datetime(2025, 1, 1, 12, 30)
        self.assertEqual(detect_meal_time(lunch_time), "lunch")
        
        # Edge case: 11:00 AM (start of lunch)
        early_lunch = datetime(2025, 1, 1, 11, 0)
        self.assertEqual(detect_meal_time(early_lunch), "lunch")
        
        # Edge case: 2:59 PM (end of lunch)
        late_lunch = datetime(2025, 1, 1, 14, 59)
        self.assertEqual(detect_meal_time(late_lunch), "lunch")
    
    def test_dinner_time(self):
        """Test dinner detection."""
        # 7:30 PM
        dinner_time = datetime(2025, 1, 1, 19, 30)
        self.assertEqual(detect_meal_time(dinner_time), "dinner")
        
        # Edge case: 6:00 PM (start of dinner)
        early_dinner = datetime(2025, 1, 1, 18, 0)
        self.assertEqual(detect_meal_time(early_dinner), "dinner")
        
        # Edge case: 9:59 PM (end of dinner)
        late_dinner = datetime(2025, 1, 1, 21, 59)
        self.assertEqual(detect_meal_time(late_dinner), "dinner")
    
    def test_snack_times(self):
        """Test snack detection for various times."""
        # Afternoon snack: 4:00 PM
        afternoon_snack = datetime(2025, 1, 1, 16, 0)
        self.assertEqual(detect_meal_time(afternoon_snack), "snack")
        
        # Late night snack: 11:00 PM
        late_night_snack = datetime(2025, 1, 1, 23, 0)
        self.assertEqual(detect_meal_time(late_night_snack), "snack")
        
        # Early morning snack: 3:00 AM
        early_morning_snack = datetime(2025, 1, 1, 3, 0)
        self.assertEqual(detect_meal_time(early_morning_snack), "snack")
    
    def test_meal_emojis(self):
        """Test meal emoji assignment."""
        self.assertEqual(get_meal_emoji("breakfast"), "🌅")
        self.assertEqual(get_meal_emoji("lunch"), "☀️")
        self.assertEqual(get_meal_emoji("dinner"), "🌙")
        self.assertEqual(get_meal_emoji("snack"), "🍿")
        self.assertEqual(get_meal_emoji("unknown"), "🍽️")  # Default
    
    def test_meal_display_names(self):
        """Test meal display name formatting."""
        self.assertEqual(get_meal_display_name("breakfast"), "Breakfast")
        self.assertEqual(get_meal_display_name("lunch"), "Lunch")
        self.assertEqual(get_meal_display_name("dinner"), "Dinner")
        self.assertEqual(get_meal_display_name("snack"), "Snack")
    
    def test_edge_cases(self):
        """Test boundary conditions."""
        # 4:59 AM - should be snack (just before breakfast)
        pre_breakfast = datetime(2025, 1, 1, 4, 59)
        self.assertEqual(detect_meal_time(pre_breakfast), "snack")
        
        # 10:59 AM - should be breakfast (just before lunch)
        pre_lunch = datetime(2025, 1, 1, 10, 59)
        self.assertEqual(detect_meal_time(pre_lunch), "breakfast")
        
        # 2:59 PM - should be lunch (just before snack)
        pre_snack = datetime(2025, 1, 1, 14, 59)
        self.assertEqual(detect_meal_time(pre_snack), "lunch")
        
        # 5:59 PM - should be snack (just before dinner)
        pre_dinner = datetime(2025, 1, 1, 17, 59)
        self.assertEqual(detect_meal_time(pre_dinner), "snack")


if __name__ == '__main__':
    unittest.main()