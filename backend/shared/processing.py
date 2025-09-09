import os
import json
import yaml
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def _load_prompt() -> str:
    """Load the food parsing prompt from YAML file"""
    # Get the directory of this file and build absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "processing", "prompts", "parser.yaml")
    with open(prompt_path, 'r') as file:
        prompts = yaml.safe_load(file)
        return prompts['food_parsing_prompt']

def _load_nutrition_database() -> dict:
    """Load the nutrition database from JSON file"""
    # Get the directory of this file and build absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "data", "nutrition_db.json")
    try:
        with open(db_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: Nutrition database not found at {db_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in nutrition database at {db_path}")
        return {}

def _extract_response_content(llm_output: str) -> str:
    """Extract JSON content from between <response> tags"""
    print(f"🔍 DEBUG - Raw LLM Output:\n{llm_output}")
    print(f"🔍 DEBUG - Output length: {len(llm_output)} characters")
    
    # Extract content between <response> and </response> tags
    start_tag = "<response>"
    end_tag = "</response>"
    
    start_index = llm_output.find(start_tag)
    if start_index == -1:
        print("❌ DEBUG - No <response> tag found in output")
        # Fallback: try to find JSON directly
        start_json = llm_output.find('{')
        end_json = llm_output.rfind('}') + 1
        if start_json != -1 and end_json != 0:
            fallback_json = llm_output[start_json:end_json]
            print(f"🔄 DEBUG - Using fallback JSON extraction: {fallback_json}")
            return fallback_json
        raise ValueError(f"No <response> tags found and no JSON fallback available in: {llm_output}")
    
    start_index += len(start_tag)
    end_index = llm_output.find(end_tag, start_index)
    
    if end_index == -1:
        print("❌ DEBUG - No closing </response> tag found")
        # Use everything after <response> tag
        extracted_content = llm_output[start_index:].strip()
    else:
        extracted_content = llm_output[start_index:end_index].strip()
    
    print(f"✅ DEBUG - Extracted response content:\n{extracted_content}")
    return extracted_content

def _parse_quantity(quantity_str: str) -> float:
    """Parse quantity string to get numeric value for calculations"""
    # Remove common words and normalize
    quantity_str = quantity_str.lower().strip()
    
    # Handle fractions
    if "half" in quantity_str or "0.5" in quantity_str:
        return 0.5
    if "quarter" in quantity_str or "0.25" in quantity_str:
        return 0.25
    
    # Extract first number found
    numbers = re.findall(r'\d+\.?\d*', quantity_str)
    if numbers:
        return float(numbers[0])
    
    # Default for items like "1 piece", "not specified"
    return 1.0

def _calculate_macros(nutrition_per_100g: dict, quantity_str: str) -> dict:
    """Calculate macros based on quantity and nutrition per 100g"""
    quantity_value = _parse_quantity(quantity_str)
    
    # Simple scaling - assumes database values are per 100g
    scaling_factor = quantity_value
    
    # Basic unit conversion approximations
    if "kilogram" in quantity_str.lower() or "kilo" in quantity_str.lower():
        scaling_factor = quantity_value * 10  # 1 kg = 1000g = 10 * 100g
    elif "gram" in quantity_str.lower():
        scaling_factor = quantity_value / 100.0  # Convert grams to 100g units
    elif "cup" in quantity_str.lower():
        scaling_factor = quantity_value * 1.5  # Rough approximation: 1 cup ~ 150g
    elif "tablespoon" in quantity_str.lower():
        scaling_factor = quantity_value * 0.15  # 1 tbsp ~ 15g
    elif "scoop" in quantity_str.lower():
        scaling_factor = quantity_value * 0.3  # 1 scoop ~ 30g
    elif "piece" in quantity_str.lower() or "not specified" in quantity_str.lower():
        scaling_factor = quantity_value * 1.0  # Use database values as-is for pieces
    elif "pound" in quantity_str.lower():
        scaling_factor = quantity_value * 4.54  # 1 pound ~ 454g = 4.54 * 100g
    
    return {
        "calories": round(nutrition_per_100g["calories"] * scaling_factor),
        "protein_g": round(nutrition_per_100g["protein_g"] * scaling_factor, 1),
        "carbs_g": round(nutrition_per_100g["carbs_g"] * scaling_factor, 1),
        "fat_g": round(nutrition_per_100g["fat_g"] * scaling_factor, 1)
    }

def _lookup_nutrition(food_name: str, quantity: str) -> dict:
    """
    Look up nutrition information for a food item
    First tries USDA API, then falls back to local database
    """
    # First, try USDA API
    try:
        from usda_client import USDAClient, parse_quantity_to_grams
        
        # Convert quantity string to grams for USDA API
        quantity_g = parse_quantity_to_grams(quantity)
        
        # Get nutrition from USDA
        usda_client = USDAClient()
        usda_nutrition = usda_client.get_nutrition(food_name, quantity_g)
        
        # If USDA returned valid data, use it
        if usda_nutrition and usda_nutrition.get("source") == "usda":
            print(f"✅ USDA nutrition found for '{food_name}' ({quantity})")
            return usda_nutrition
        
        print(f"⚠️ USDA lookup failed for '{food_name}', trying local database...")
        
    except Exception as e:
        print(f"❌ USDA API error for '{food_name}': {e}")
        print(f"Falling back to local database...")
    
    # Fallback to local database
    return _lookup_local_nutrition(food_name, quantity)

def _lookup_local_nutrition(food_name: str, quantity: str) -> dict:
    """Look up nutrition from local database (original implementation)"""
    nutrition_db = _load_nutrition_database()
    
    # Try exact match first
    food_key = food_name.lower().strip()
    if food_key in nutrition_db:
        result = _calculate_macros(nutrition_db[food_key], quantity)
        result["source"] = "local_database"
        return result
    
    # Try partial matching
    for db_food in nutrition_db:
        if food_key in db_food or db_food in food_key:
            print(f"Partial match found: '{food_name}' -> '{db_food}'")
            result = _calculate_macros(nutrition_db[db_food], quantity)
            result["source"] = "local_database"
            return result
    
    # No match found
    print(f"Warning: No nutritional data found for '{food_name}' (quantity: {quantity})")
    return {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "source": "not_found"
    }

def process_food_text(text: str) -> dict:
    """
    Parse natural language food description into structured data
    
    Args:
        text: Natural language description of food consumed
        
    Returns:
        Dictionary with parsed food items
        
    Raises:
        Exception: If processing fails
    """
    if not text or not text.strip():
        raise ValueError("Empty food description provided")
    
    prompt = _load_prompt()
    client = Groq()
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\n{text}"
            }
        ],
        temperature=0.1,
        max_tokens=1500
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Extract JSON content from <response> tags and parse
    try:
        json_content = _extract_response_content(response_text)
        parsed_data = json.loads(json_content)
        print(f"✅ DEBUG - Successfully parsed JSON: {parsed_data}")
    except json.JSONDecodeError as e:
        print(f"❌ DEBUG - JSON parsing error: {e}")
        raise ValueError(f"Could not parse JSON from response: {response_text}")
    except Exception as e:
        print(f"❌ DEBUG - Response extraction error: {e}")
        # Log parsing error for review (simplified version for now)
        print(f"🔍 PARSER_ERROR - Input: {text}")
        print(f"🔍 PARSER_ERROR - LLM Response: {response_text[:500]}...")
        print(f"🔍 PARSER_ERROR - Error: {e}")
        
        # Fallback: return simple structure
        return {
            "items": [
                {
                    "food": text,
                    "quantity": "1 serving",
                    "estimated": True,
                    "unit": "serving",
                    "macros": {
                        "calories": 0,
                        "protein_g": 0,
                        "carbs_g": 0,
                        "fat_g": 0
                    }
                }
            ],
            "error": "Parser failed - used fallback"
        }
    
    # Add nutrition information to each food item
    if 'items' in parsed_data:
        for item in parsed_data['items']:
            if 'food' in item and 'quantity' in item:
                item['macros'] = _lookup_nutrition(item['food'], item['quantity'])
    
    return parsed_data

if __name__ == "__main__":
    test_descriptions = [
        "I ate 150 grams of chicken and half a cup of rice",
        "Had two eggs and a banana for breakfast"
    ]
    
    for desc in test_descriptions:
        try:
            result = process_food_text(desc)
            print(f"Input: {desc}")
            print(f"Output: {json.dumps(result, indent=2)}")
            print()
        except Exception as e:
            print(f"Error processing '{desc}': {e}")
            print()