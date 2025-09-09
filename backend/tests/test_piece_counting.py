#!/usr/bin/env python3
"""
Test suite for piece counting and token limit fixes
Tests edge cases that were failing before the fixes
"""

import pytest
import sys
import os

# Add the shared directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from processing import process_food_text

class TestPieceCounting:
    """Test piece-to-gram conversions and token limit fixes"""
    
    def test_large_number_almonds(self):
        """Test that large numbers don't cause token truncation"""
        result = process_food_text("I ate 815 almonds")
        
        assert len(result["items"]) == 1
        item = result["items"][0]
        
        assert item["food"] == "almonds"
        # 815 almonds × 1.5g = 1222.5g ≈ 1223g
        assert item["quantity"] == "1223g"
        assert item["estimated"] == True  # Count exact, weight estimated
        assert item["unit"] == "g"
        
        # Should have high calorie count
        assert item["macros"]["calories"] > 6000
        assert item["macros"]["source"] == "usda"
    
    def test_two_almonds_and_rice(self):
        """Test that multi-item complex response doesn't get truncated"""
        result = process_food_text("I ate two almonds and 100 grams of rice")
        
        # Should have 2 items, not fallback to raw transcription
        assert len(result["items"]) == 2
        assert "error" not in result  # No parser error fallback
        
        # Find almonds and rice items
        almonds_item = None
        rice_item = None
        
        for item in result["items"]:
            if "almond" in item["food"]:
                almonds_item = item
            elif "rice" in item["food"]:
                rice_item = item
        
        # Test almonds: 2 × 1.5g = 3g
        assert almonds_item is not None
        assert almonds_item["quantity"] == "3g"
        assert almonds_item["estimated"] == False  # Exact count given
        
        # Test rice: 100g as specified
        assert rice_item is not None
        assert rice_item["quantity"] == "100g"
        assert rice_item["estimated"] == False  # Exact weight given
    
    def test_single_banana(self):
        """Test single piece conversion works correctly"""
        result = process_food_text("I ate one banana")
        
        assert len(result["items"]) == 1
        item = result["items"][0]
        
        assert item["food"] == "banana"
        assert item["quantity"] == "120g"  # Medium banana
        assert item["estimated"] == True   # Size estimated
        assert item["unit"] == "g"
        
        # Should get raw banana, not dehydrated (after USDA fix)
        # Calories should be ~89-107, not 346+ (dehydrated)
        assert item["macros"]["calories"] < 200
        assert item["macros"]["source"] == "usda"
    
    def test_mixed_pieces_and_weights(self):
        """Test mixed exact counts and weights"""
        result = process_food_text("I ate two eggs and 50 grams of chicken")
        
        assert len(result["items"]) == 2
        
        # Find eggs and chicken
        eggs_item = None
        chicken_item = None
        
        for item in result["items"]:
            if "egg" in item["food"]:
                eggs_item = item
            elif "chicken" in item["food"]:
                chicken_item = item
        
        # Test eggs: 2 × 50g = 100g
        assert eggs_item is not None
        assert eggs_item["quantity"] == "100g"
        assert eggs_item["estimated"] == False  # Standard conversion
        
        # Test chicken: 50g as specified
        assert chicken_item is not None
        assert chicken_item["quantity"] == "50g"
        assert chicken_item["estimated"] == False  # Exact weight given
    
    def test_various_nut_pieces(self):
        """Test different nut piece conversions"""
        # Test almonds
        result = process_food_text("I ate five almonds")
        assert len(result["items"]) == 1
        item = result["items"][0]
        # 5 × ~1.5g = ~7.5g (may vary based on LLM calculation)
        quantity_num = float(item["quantity"].replace('g', ''))
        assert 7 <= quantity_num <= 8
        
        # Test that it's not defaulting to 2g or 5g
        assert item["quantity"] != "5g"
        assert item["quantity"] != "2g"

class TestUSDAFoodSelection:
    """Test that USDA returns raw foods over processed ones"""
    
    def test_banana_returns_raw_not_dehydrated(self):
        """Test banana returns raw banana, not dehydrated"""
        result = process_food_text("I ate one banana")
        item = result["items"][0]
        
        # Raw banana should be ~89-107 cal/100g
        # Dehydrated banana is ~346 cal/100g
        calories_per_100g = (item["macros"]["calories"] / float(item["quantity"].replace('g', ''))) * 100
        
        # Should be closer to raw banana calories
        assert calories_per_100g < 150, f"Got {calories_per_100g} cal/100g, expected <150 for raw banana"
    
    def test_chicken_returns_raw_not_cooked(self):
        """Test chicken returns raw chicken when possible"""
        result = process_food_text("I ate 100 grams of chicken")
        item = result["items"][0]
        
        # Raw chicken is typically 165-200 cal/100g
        # Cooked/prepared chicken can be much higher
        calories_per_100g = item["macros"]["calories"]  # Already per 100g
        
        assert calories_per_100g < 250, f"Got {calories_per_100g} cal/100g, might be processed chicken"

class TestTokenLimitRegression:
    """Test that complex inputs don't hit token limits"""
    
    def test_complex_multi_item_description(self):
        """Test complex descriptions don't get truncated"""
        complex_input = "I ate two eggs, three slices of bread, a handful of almonds, 100 grams of chicken breast, and a medium apple"
        
        result = process_food_text(complex_input)
        
        # Should parse multiple items, not fall back to raw transcription
        assert len(result["items"]) >= 4  # At least 4 distinct foods
        assert "error" not in result  # No parser error
        
        # Check that we don't get the raw input as food name (fallback behavior)
        for item in result["items"]:
            assert item["food"] != complex_input
            assert "serving" not in item["quantity"]  # Should have real quantities

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])