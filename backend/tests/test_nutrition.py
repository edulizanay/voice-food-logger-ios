#!/usr/bin/env python3
"""
Test nutrition lookup and macro calculations
"""
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing import _lookup_nutrition, _calculate_macros, _parse_quantity
from storage import store_food_data, get_daily_totals, _calculate_daily_totals

def test_nutrition_lookup():
    """Test nutrition database lookup"""
    print("🥗 Testing nutrition database lookup...")
    
    test_cases = [
        ('chicken breast', '150 grams', True),
        ('rice', '0.5 cup', True), 
        ('whey protein', '1 scoop', True),
        ('unknown_food', '100 grams', False)
    ]
    
    for food, quantity, should_find in test_cases:
        result = _lookup_nutrition(food, quantity)
        
        if should_find:
            if result['calories'] > 0:
                print(f"✅ Found {food}: {result['calories']} cal, {result['protein_g']}g protein")
            else:
                print(f"❌ Expected to find {food} but got zero calories")
                return False
        else:
            if result['calories'] == 0:
                print(f"✅ Correctly didn't find {food}")
            else:
                print(f"❌ Unexpectedly found data for {food}")
                return False
    
    return True

def test_quantity_parsing():
    """Test quantity string parsing"""
    print("🔢 Testing quantity parsing...")
    
    test_cases = [
        ('150 grams', 150.0, 'grams'),
        ('0.5 cup', 0.5, 'cup'),
        ('half cup', 0.5, 'half'),
        ('2 kilograms', 2.0, 'kg'),
        ('1 scoop', 1.0, 'scoop'),
        ('1 piece', 1.0, 'piece')
    ]
    
    for quantity_str, expected_value, test_type in test_cases:
        result = _parse_quantity(quantity_str)
        if abs(result - expected_value) < 0.1:
            print(f"✅ {quantity_str} -> {result}")
        else:
            print(f"❌ {quantity_str} -> {result}, expected ~{expected_value}")
            return False
    
    return True

def test_macro_calculations():
    """Test macro scaling calculations"""
    print("📊 Testing macro calculations...")
    
    # Test with chicken breast (165 cal, 31g protein, 0g carbs, 3.6g fat per 100g)
    base_nutrition = {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6}
    
    test_cases = [
        ('100 grams', 1.0),     # 100g = 1x base values
        ('200 grams', 2.0),     # 200g = 2x base values  
        ('50 grams', 0.5),      # 50g = 0.5x base values
        ('1 kilogram', 10.0),   # 1kg = 10x base values (but parsed as 1.0 and scaled by 10)
    ]
    
    for quantity_str, expected_factor in test_cases:
        result = _calculate_macros(base_nutrition, quantity_str)
        expected_calories = int(base_nutrition["calories"] * expected_factor)
        
        if abs(result["calories"] - expected_calories) <= 1:  # Allow 1 calorie rounding difference
            print(f"✅ {quantity_str}: {result['calories']} cal (expected ~{expected_calories})")
        else:
            print(f"❌ {quantity_str}: {result['calories']} cal, expected ~{expected_calories}")
            return False
    
    return True

def test_daily_totals():
    """Test daily totals calculation"""
    print("📈 Testing daily totals calculation...")
    
    # Create test entries with known macro values
    test_entries = [
        {
            "items": [
                {
                    "food": "chicken", 
                    "quantity": "100g",
                    "macros": {"calories": 100, "protein_g": 20, "carbs_g": 0, "fat_g": 2}
                },
                {
                    "food": "rice",
                    "quantity": "1 cup", 
                    "macros": {"calories": 200, "protein_g": 4, "carbs_g": 44, "fat_g": 0.5}
                }
            ]
        },
        {
            "items": [
                {
                    "food": "banana",
                    "quantity": "1 piece",
                    "macros": {"calories": 89, "protein_g": 1.1, "carbs_g": 23, "fat_g": 0.3}
                }
            ]
        }
    ]
    
    totals = _calculate_daily_totals(test_entries)
    expected = {"calories": 389, "protein_g": 25.1, "carbs_g": 67, "fat_g": 2.8}
    
    for key in expected:
        if abs(totals[key] - expected[key]) < 0.1:
            print(f"✅ Total {key}: {totals[key]} (expected {expected[key]})")
        else:
            print(f"❌ Total {key}: {totals[key]}, expected {expected[key]}")
            return False
    
    return True

def test_storage_with_macros():
    """Test storage system with macro information"""
    print("💾 Testing storage with macros...")
    
    # Clean up any existing test file
    test_file = 'logs/logs_2025-09-06.json'
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Test storing items with macros
    test_items = [
        {
            'food': 'test_chicken',
            'quantity': '100 grams',
            'macros': {'calories': 165, 'protein_g': 31, 'carbs_g': 0, 'fat_g': 3.6}
        }
    ]
    
    try:
        store_food_data(test_items)
        totals = get_daily_totals()
        
        if totals['calories'] == 165 and totals['protein_g'] == 31:
            print("✅ Storage and retrieval working correctly")
            return True
        else:
            print(f"❌ Storage test failed: {totals}")
            return False
            
    except Exception as e:
        print(f"❌ Storage test error: {e}")
        return False

def run_all_tests():
    """Run all nutrition tests"""
    print("🧪 Running Phase 2 Nutrition Tests\n")
    
    tests = [
        test_nutrition_lookup,
        test_quantity_parsing, 
        test_macro_calculations,
        test_daily_totals,
        test_storage_with_macros
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ FAILED with error: {e}\n")
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)