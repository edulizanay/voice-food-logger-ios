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
            
            # Extract food name and quantity to debug
            food_name = data.get('food', 'almonds')
            quantity_str = data.get('quantity', '100g')
            
            debug_info = {
                'input': {'food_name': food_name, 'quantity_str': quantity_str},
                'steps': []
            }
            
            try:
                # Step 1: Test quantity parsing
                debug_info['steps'].append({'step': 1, 'action': f'Parse quantity: "{quantity_str}"'})
                from usda_client import parse_quantity_to_grams
                quantity_g = parse_quantity_to_grams(quantity_str)
                debug_info['steps'].append({
                    'step': 1, 
                    'result': f'Parsed to: {quantity_g} grams (type: {type(quantity_g).__name__})'
                })
                
                # Step 2: Test USDA client creation and API key
                debug_info['steps'].append({'step': 2, 'action': 'Create USDA client'})
                from usda_client import USDAClient
                usda_client = USDAClient()
                debug_info['steps'].append({
                    'step': 2, 
                    'result': f'Client created. API key exists: {bool(usda_client.api_key)}'
                })
                
                # Step 3: Test direct USDA nutrition lookup (same as processing.py does)
                debug_info['steps'].append({'step': 3, 'action': f'Call get_nutrition("{food_name}", {quantity_g})'})
                usda_nutrition = usda_client.get_nutrition(food_name, quantity_g)
                debug_info['steps'].append({
                    'step': 3, 
                    'result': f'USDA result: {usda_nutrition}'
                })
                
                # Step 4: Test if result would be considered valid
                debug_info['steps'].append({'step': 4, 'action': 'Check if USDA result is valid'})
                is_valid = usda_nutrition and usda_nutrition.get("source") == "usda"
                debug_info['steps'].append({
                    'step': 4, 
                    'result': f'Valid USDA result: {is_valid}'
                })
                
                if not is_valid:
                    # Step 5: Test fallback to local database
                    debug_info['steps'].append({'step': 5, 'action': 'Test local database fallback'})
                    from processing import _lookup_local_nutrition
                    local_nutrition = _lookup_local_nutrition(food_name, quantity_str)
                    debug_info['steps'].append({
                        'step': 5, 
                        'result': f'Local DB result: {local_nutrition}'
                    })
                
                # Step 6: Compare with full processing pipeline
                debug_info['steps'].append({'step': 6, 'action': 'Test full _lookup_nutrition function'})
                from processing import _lookup_nutrition
                full_result = _lookup_nutrition(food_name, quantity_str)
                debug_info['steps'].append({
                    'step': 6, 
                    'result': f'Full pipeline result: {full_result}'
                })
                
            except Exception as e:
                debug_info['steps'].append({
                    'step': 'ERROR', 
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                import traceback
                debug_info['steps'].append({
                    'step': 'ERROR_TRACEBACK',
                    'traceback': traceback.format_exc()
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