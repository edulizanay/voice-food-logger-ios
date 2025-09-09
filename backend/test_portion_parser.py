#!/usr/bin/env python3

"""
Test suite for enhanced portion parser
Tests should fail initially, then pass after parser.yaml is updated
"""

import pytest
import json
import sys
import os

# Add the shared directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from processing import process_food_text

class TestPortionParser:
    """Test enhanced portion parsing with smart estimation"""
    
    def test_bowl_of_cereal_with_milk(self):
        """Test parsing bowl of cereal with milk - should estimate both portions"""
        transcription = "I had a bowl of cereal with milk"
        
        result = process_food_text(transcription)
        
        # Should have 2 items
        assert len(result["items"]) == 2
        
        # Find cereal item
        cereal_item = next(item for item in result["items"] if "cereal" in item["food"])
        assert cereal_item["quantity"] == "40g" or cereal_item["quantity"] == "45g"  # Accept range
        assert cereal_item["estimated"] == True
        assert cereal_item["unit"] == "g"
        
        # Find milk item
        milk_item = next(item for item in result["items"] if "milk" in item["food"])
        assert milk_item["quantity"] == "200ml" or milk_item["quantity"] == "250ml"  # Accept range
        assert milk_item["estimated"] == True
        assert milk_item["unit"] == "ml"
    
    def test_exact_quantity_eggs(self):
        """Test parsing exact quantities - should not be estimated"""
        transcription = "I ate 2 eggs for breakfast"
        
        result = process_food_text(transcription)
        
        # Should have 1 item
        assert len(result["items"]) == 1
        
        eggs_item = result["items"][0]
        assert "egg" in eggs_item["food"]
        assert eggs_item["quantity"] == "100g"  # 2 eggs × 50g each
        assert eggs_item["estimated"] == False  # Exact count given
        assert eggs_item["unit"] == "g"
    
    def test_handful_of_nuts(self):
        """Test handful portion descriptor"""
        transcription = "I had a handful of almonds"
        
        result = process_food_text(transcription)
        
        assert len(result["items"]) == 1
        
        almonds_item = result["items"][0]
        assert "almond" in almonds_item["food"]
        assert almonds_item["quantity"] == "28g" or almonds_item["quantity"] == "30g"  # Accept range
        assert almonds_item["estimated"] == True
        assert almonds_item["unit"] == "g"
    
    def test_large_plate_of_pasta(self):
        """Test size modifiers (large plate)"""
        transcription = "I ate a large plate of spaghetti"
        
        result = process_food_text(transcription)
        
        assert len(result["items"]) == 1
        
        pasta_item = result["items"][0]
        assert "spaghetti" in pasta_item["food"] or "pasta" in pasta_item["food"]
        # Large plate should be bigger than normal plate (250g)
        quantity_num = int(pasta_item["quantity"].replace("g", ""))
        assert quantity_num >= 280  # At least 280g for large
        assert pasta_item["estimated"] == True
        assert pasta_item["unit"] == "g"
    
    def test_glass_of_water(self):
        """Test liquid in glass"""
        transcription = "I drank a glass of water"
        
        result = process_food_text(transcription)
        
        assert len(result["items"]) == 1
        
        water_item = result["items"][0]
        assert "water" in water_item["food"]
        assert water_item["quantity"] == "240ml"  # Standard glass
        assert water_item["estimated"] == True
        assert water_item["unit"] == "ml"
    
    def test_cup_of_cooked_rice(self):
        """Test cup measurement for solid food"""
        transcription = "I had a cup of rice"
        
        result = process_food_text(transcription)
        
        assert len(result["items"]) == 1
        
        rice_item = result["items"][0]
        assert "rice" in rice_item["food"]
        assert rice_item["quantity"] == "185g"  # Cup of cooked rice
        assert rice_item["estimated"] == False  # Cup is a standard measurement 
        assert rice_item["unit"] == "g"
    
    def test_mixed_exact_and_estimated(self):
        """Test mix of exact and estimated quantities"""
        transcription = "I ate 150 grams of chicken and a bowl of salad"
        
        result = process_food_text(transcription)
        
        assert len(result["items"]) == 2
        
        # Find chicken (exact)
        chicken_item = next(item for item in result["items"] if "chicken" in item["food"])
        assert chicken_item["quantity"] == "150g"
        assert chicken_item["estimated"] == False  # Exact amount given
        assert chicken_item["unit"] == "g"
        
        # Find salad (estimated)
        salad_item = next(item for item in result["items"] if "salad" in item["food"])
        quantity_num = int(salad_item["quantity"].replace("g", ""))
        assert 80 <= quantity_num <= 120  # Bowl of salad range
        assert salad_item["estimated"] == True
        assert salad_item["unit"] == "g"

    def test_soup_bowl_liquid(self):
        """Test soup in bowl - should be liquid measurement"""
        transcription = "I had a bowl of chicken soup"
        
        result = process_food_text(transcription)
        
        # Could be 1 item (soup) or 2+ items (if separated)
        assert len(result["items"]) >= 1
        
        # Find soup item
        soup_item = next(item for item in result["items"] if "soup" in item["food"])
        quantity_num = int(soup_item["quantity"].replace("ml", ""))
        assert 300 <= quantity_num <= 400  # Bowl of soup range
        assert soup_item["estimated"] == True
        assert soup_item["unit"] == "ml"

if __name__ == "__main__":
    # Run the tests to see current failures
    pytest.main([__file__, "-v"])