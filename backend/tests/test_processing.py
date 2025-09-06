#!/usr/bin/env python3
"""
Simple test for processing module
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing import process_food_text

def test_processing():
    """Test food text processing"""
    test_descriptions = [
        "I ate 150 grams of chicken and half a cup of rice",
        "Had two eggs and a banana for breakfast",
        "Ate some pasta with tomato sauce"
    ]
    
    print("🍽️ Testing food text processing...")
    
    for i, desc in enumerate(test_descriptions, 1):
        try:
            print(f"\nTest {i}: {desc}")
            result = process_food_text(desc)
            
            if result and 'items' in result:
                print(f"✅ Processing successful!")
                print(f"Found {len(result['items'])} food items:")
                for item in result['items']:
                    print(f"  - {item['food']}: {item['quantity']}")
            else:
                print(f"❌ Processing failed - no valid result")
                return False
                
        except Exception as e:
            print(f"❌ Processing failed with error: {e}")
            return False
    
    print(f"\n✅ All processing tests passed!")
    return True

if __name__ == "__main__":
    success = test_processing()
    exit(0 if success else 1)