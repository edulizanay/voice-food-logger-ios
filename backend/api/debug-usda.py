from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get content length and read body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Extract food name to debug
            food_name = data.get('food', 'almonds')
            quantity_g = data.get('quantity_g', 100)
            
            debug_info = {
                'food_name': food_name,
                'quantity_g': quantity_g,
                'steps': []
            }
            
            try:
                # Step 1: Test USDA import
                debug_info['steps'].append({'step': 1, 'action': 'Import USDA client'})
                from usda_client import USDAClient, parse_quantity_to_grams
                debug_info['steps'].append({'step': 1, 'result': 'SUCCESS - USDA client imported'})
                
                # Step 2: Create client and test search terms
                debug_info['steps'].append({'step': 2, 'action': 'Generate search terms'})
                client = USDAClient()
                search_terms = client._generate_search_terms(food_name)
                debug_info['steps'].append({'step': 2, 'result': f'SUCCESS - Search terms: {search_terms}'})
                
                # Step 3: Test each search term
                for i, search_term in enumerate(search_terms):
                    debug_info['steps'].append({'step': f'3.{i+1}', 'action': f'Search USDA for: "{search_term}"'})
                    
                    search_results = client.search_food(search_term)
                    debug_info['steps'].append({
                        'step': f'3.{i+1}', 
                        'result': f'Found {len(search_results)} results'
                    })
                    
                    if search_results:
                        # Show first 3 results
                        first_results = []
                        for j, result in enumerate(search_results[:3]):
                            desc = result.get('description', 'Unknown')
                            nutrients = result.get('foodNutrients', [])
                            calories = 0
                            for nutrient in nutrients:
                                if nutrient.get('nutrientNumber') == '208':
                                    calories = nutrient.get('value', 0)
                                    break
                            first_results.append({'description': desc, 'calories_per_100g': calories})
                        
                        debug_info['steps'].append({
                            'step': f'3.{i+1}', 
                            'details': f'First 3 results: {first_results}'
                        })
                        
                        # Step 4: Test keyword filtering
                        debug_info['steps'].append({'step': f'4.{i+1}', 'action': f'Apply keyword filter for "{food_name}"'})
                        filtered_results = client._filter_by_food_name(search_results, food_name)
                        debug_info['steps'].append({
                            'step': f'4.{i+1}', 
                            'result': f'Filtered to {len(filtered_results)} results'
                        })
                        
                        if filtered_results:
                            selected = filtered_results[0]
                            debug_info['steps'].append({
                                'step': f'4.{i+1}', 
                                'selected': selected.get('description', 'Unknown')
                            })
                            
                            # Step 5: Extract nutrition
                            debug_info['steps'].append({'step': 5, 'action': 'Extract and scale nutrition'})
                            nutrition = client._extract_nutrition(selected, quantity_g)
                            debug_info['steps'].append({
                                'step': 5, 
                                'final_nutrition': nutrition
                            })
                            break
                        else:
                            debug_info['steps'].append({
                                'step': f'4.{i+1}', 
                                'result': 'No results passed keyword filter'
                            })
                
                # If no results found, test fallback
                if not any('final_nutrition' in step for step in debug_info['steps']):
                    debug_info['steps'].append({'step': 6, 'action': 'No USDA results, testing fallback'})
                    nutrition = client.get_nutrition(food_name, quantity_g)
                    debug_info['steps'].append({
                        'step': 6, 
                        'fallback_nutrition': nutrition
                    })
                
            except Exception as e:
                debug_info['steps'].append({
                    'step': 'ERROR', 
                    'error': str(e),
                    'error_type': type(e).__name__
                })
            
            # Return debug info
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'debug_info': debug_info
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': message
        }
        self.wfile.write(json.dumps(error_response).encode())