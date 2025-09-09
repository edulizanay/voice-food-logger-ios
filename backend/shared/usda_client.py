"""
USDA FoodData Central API Client
Provides access to USDA's comprehensive food nutrition database
"""

import os
import requests
import json
import re
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv

load_dotenv()

class USDAClient:
    """Client for USDA FoodData Central API"""
    
    # Map USDA nutrient numbers to our nutrition fields
    NUTRIENT_MAPPING = {
        "208": "calories",      # Energy (kcal)
        "203": "protein_g",     # Protein (g)
        "204": "fat_g",         # Total lipid (fat) (g)
        "205": "carbs_g",       # Carbohydrate, by difference (g)
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize USDA client with API key"""
        self.api_key = api_key or os.getenv("USDA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.timeout = 10  # seconds
        
    def search_food(self, query: str, data_type: str = "SR Legacy", page_size: int = 10) -> List[Dict]:
        """
        Search USDA food database
        
        Args:
            query: Food search term (e.g., "chicken breast")
            data_type: Type of food data ("SR Legacy", "Branded", "Foundation", etc.)
            page_size: Number of results to return
            
        Returns:
            List of food items with nutrition data
        """
        try:
            url = f"{self.base_url}/foods/search"
            params = {
                "api_key": self.api_key,
                "query": query,
                "dataType": data_type,
                "pageSize": page_size,
                "sortBy": "score",  # Most relevant first
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            # Filter out processed/breaded items for better matches
            if foods:
                foods = self._filter_best_matches(foods, query)
            
            return foods
            
        except Exception as e:
            print(f"USDA search failed for '{query}': {e}")
            return []

    def _filter_best_matches(self, foods: List[Dict], query: str) -> List[Dict]:
        """
        Filter and reorder foods to get best matches first
        Prefer raw/basic foods over processed ones
        """
        # Words that indicate processed/prepared foods (lower priority)
        processed_words = ['breaded', 'fried', 'cooked', 'prepared', 'seasoned', 'marinated', 'stuffed']
        
        # Split foods into raw/basic vs processed
        raw_foods = []
        processed_foods = []
        
        for food in foods:
            description = food.get('description', '').lower()
            is_processed = any(word in description for word in processed_words)
            
            if is_processed:
                processed_foods.append(food)
            else:
                raw_foods.append(food)
        
        # Return raw foods first, then processed
        return raw_foods + processed_foods
    
    def get_nutrition(self, food_name: str, quantity_g: float) -> Dict:
        """
        Get nutrition information for a food item
        
        Args:
            food_name: Name of food to look up
            quantity_g: Quantity in grams
            
        Returns:
            Dictionary with nutrition information
        """
        try:
            # Search for the food
            search_results = self.search_food(food_name)
            
            if not search_results:
                print(f"No USDA results found for '{food_name}', falling back to local")
                return self._fallback_to_local(food_name, quantity_g)
            
            # Use the best match (first result)
            best_match = search_results[0]
            
            # Extract and scale nutrition
            nutrition = self._extract_nutrition(best_match, quantity_g)
            return nutrition
            
        except Exception as e:
            print(f"USDA nutrition lookup failed for '{food_name}': {e}")
            return self._fallback_to_local(food_name, quantity_g)
    
    def _extract_nutrition(self, food_data: Dict, quantity_g: float) -> Dict:
        """
        Extract key nutrition values from USDA food data
        
        Args:
            food_data: USDA API food item response
            quantity_g: Quantity in grams to scale to
            
        Returns:
            Nutrition dictionary scaled to quantity
        """
        # Initialize nutrition with defaults
        base_nutrition = {
            "calories": 0,
            "protein_g": 0.0,
            "fat_g": 0.0,
            "carbs_g": 0.0,
        }
        
        # Extract nutrients from USDA data (values are per 100g)
        food_nutrients = food_data.get("foodNutrients", [])
        
        for nutrient in food_nutrients:
            nutrient_number = nutrient.get("nutrientNumber")
            if nutrient_number in self.NUTRIENT_MAPPING:
                field_name = self.NUTRIENT_MAPPING[nutrient_number]
                value = nutrient.get("value", 0)
                
                # Convert to appropriate type
                if field_name == "calories":
                    base_nutrition[field_name] = int(value) if value else 0
                else:
                    base_nutrition[field_name] = float(value) if value else 0.0
        
        # Scale nutrition to requested quantity (USDA values are per 100g)
        scaled_nutrition = self._scale_nutrition(base_nutrition, quantity_g)
        scaled_nutrition["source"] = "usda"
        
        return scaled_nutrition
    
    def _scale_nutrition(self, base_nutrition: Dict, quantity_g: float) -> Dict:
        """
        Scale nutrition values from 100g base to requested quantity
        
        Args:
            base_nutrition: Nutrition per 100g
            quantity_g: Target quantity in grams
            
        Returns:
            Scaled nutrition dictionary
        """
        scale_factor = quantity_g / 100.0
        
        return {
            "calories": round(base_nutrition["calories"] * scale_factor),
            "protein_g": round(base_nutrition["protein_g"] * scale_factor, 1),
            "fat_g": round(base_nutrition["fat_g"] * scale_factor, 1),
            "carbs_g": round(base_nutrition["carbs_g"] * scale_factor, 1),
        }
    
    def _fallback_to_local(self, food_name: str, quantity_g: float) -> Dict:
        """
        Fallback to local nutrition database when USDA API fails
        
        Args:
            food_name: Food name
            quantity_g: Quantity in grams
            
        Returns:
            Nutrition from local database or defaults
        """
        try:
            # Import here to avoid circular imports
            from processing import _lookup_nutrition as local_lookup
            
            # Convert grams back to quantity string for local lookup
            quantity_str = f"{quantity_g}g"
            
            # Use existing local lookup
            local_nutrition = local_lookup(food_name, quantity_str)
            local_nutrition["source"] = "local_fallback"
            
            return local_nutrition
            
        except Exception as e:
            print(f"Local fallback also failed for '{food_name}': {e}")
            
            # Return default values as last resort
            return {
                "calories": 0,
                "protein_g": 0.0,
                "fat_g": 0.0,
                "carbs_g": 0.0,
                "source": "default"
            }
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """Handle API error responses"""
        if response.status_code == 403:
            print("USDA API: Invalid API key or access denied")
        elif response.status_code == 429:
            print("USDA API: Rate limit exceeded (1000 requests/hour)")
        elif response.status_code >= 500:
            print("USDA API: Server error")
        else:
            print(f"USDA API error: {response.status_code} - {response.text}")

# Utility function to convert various quantity formats to grams
def parse_quantity_to_grams(quantity_str: str) -> float:
    """
    Parse quantity string to grams
    
    Args:
        quantity_str: Quantity like "150g", "28g", "1 cup", etc.
        
    Returns:
        Quantity in grams as float
    """
    quantity_str = quantity_str.lower().strip()
    
    # Extract numeric value
    numbers = re.findall(r'\d+\.?\d*', quantity_str)
    if not numbers:
        return 100.0  # Default to 100g
    
    value = float(numbers[0])
    
    # Handle different units
    if 'g' in quantity_str and 'kg' not in quantity_str:
        return value  # Already in grams
    elif 'kg' in quantity_str:
        return value * 1000  # Convert kg to grams
    elif 'cup' in quantity_str:
        return value * 150  # Rough approximation: 1 cup ≈ 150g
    elif 'tablespoon' in quantity_str or 'tbsp' in quantity_str:
        return value * 15   # 1 tbsp ≈ 15g
    elif 'teaspoon' in quantity_str or 'tsp' in quantity_str:
        return value * 5    # 1 tsp ≈ 5g
    elif 'oz' in quantity_str:
        return value * 28.35  # 1 oz ≈ 28.35g
    elif 'lb' in quantity_str or 'pound' in quantity_str:
        return value * 453.6  # 1 lb ≈ 453.6g
    else:
        # Default: assume grams
        return value

if __name__ == "__main__":
    # Simple test
    client = USDAClient()
    print("Testing USDA client...")
    
    # Test search
    results = client.search_food("chicken breast")
    print(f"Found {len(results)} results for chicken breast")
    
    if results:
        print(f"First result: {results[0]['description']}")
        
        # Test nutrition lookup  
        nutrition = client.get_nutrition("chicken breast", 100)
        print(f"Nutrition per 100g: {nutrition}")