import os
import sys
import json
import re
from http.server import BaseHTTPRequestHandler

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import _get_supabase_client
from processing import _load_nutrition_database

class handler(BaseHTTPRequestHandler):
    def do_PUT(self):
        """Handle PUT requests for updating individual items within a session"""
        try:
            # Extract session ID from path: /api/entries/{session_id}/items
            path = self.path
            session_match = re.search(r'/api/entries/([a-f0-9\-]+)/items', path)
            
            if not session_match:
                self.send_error_response(400, "Invalid session ID format")
                return
            
            session_id = session_match.group(1)
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            request_data = json.loads(body)
            
            # Expect array of item updates: [{food: "chicken", quantity: "250g"}, ...]
            item_updates = request_data.get('items', [])
            if not item_updates:
                self.send_error_response(400, "Missing 'items' field")
                return
            
            # Load nutrition database for macro recalculation
            nutrition_db = _load_nutrition_database()
            
            supabase = _get_supabase_client()
            updated_items = []
            
            for item_update in item_updates:
                food_name = item_update.get('food')
                new_quantity = item_update.get('quantity')
                
                if not food_name or not new_quantity:
                    continue
                
                # Calculate new macros based on new quantity
                new_macros = self._calculate_macros(food_name, new_quantity, nutrition_db)
                
                # Update the specific item in database
                result = supabase.table("food_entries").update({
                    "quantity": new_quantity,
                    "calories": new_macros.get("calories", 0),
                    "protein": new_macros.get("protein_g", 0),
                    "carbs": new_macros.get("carbs_g", 0),
                    "fat": new_macros.get("fat_g", 0)
                }).eq("session_id", session_id).eq("food_name", food_name).execute()
                
                if result.data:
                    updated_items.append({
                        "food": food_name,
                        "quantity": new_quantity,
                        "macros": new_macros
                    })
            
            if not updated_items:
                self.send_error_response(404, "No items found to update")
                return
            
            response_data = {
                'success': True,
                'message': f'Updated {len(updated_items)} items in session {session_id}',
                'updated_items': updated_items
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _calculate_macros(self, food_name: str, quantity: str, nutrition_db: dict) -> dict:
        """Calculate macros for updated quantity"""
        # Extract numeric quantity (e.g., "250g" -> 250)
        import re
        quantity_match = re.search(r'(\d+(?:\.\d+)?)', quantity)
        if not quantity_match:
            return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
        
        quantity_num = float(quantity_match.group(1))
        
        # Look up food in nutrition database (simplified lookup)
        food_key = food_name.lower().strip()
        
        # Try exact match first
        if food_key in nutrition_db:
            base_nutrition = nutrition_db[food_key]
        else:
            # Try partial match
            partial_matches = [key for key in nutrition_db.keys() if food_key in key or key in food_key]
            if partial_matches:
                base_nutrition = nutrition_db[partial_matches[0]]
            else:
                # Default fallback values
                return {"calories": int(quantity_num * 1.5), "protein_g": quantity_num * 0.2, "carbs_g": quantity_num * 0.1, "fat_g": quantity_num * 0.05}
        
        # Scale nutrition values based on quantity (assuming base is per 100g)
        scale_factor = quantity_num / 100.0
        
        return {
            "calories": int(base_nutrition.get("calories", 0) * scale_factor),
            "protein_g": round(base_nutrition.get("protein", 0) * scale_factor, 1),
            "carbs_g": round(base_nutrition.get("carbs", 0) * scale_factor, 1),
            "fat_g": round(base_nutrition.get("fat", 0) * scale_factor, 1)
        }
    
    def send_error_response(self, status_code, message):
        """Send JSON error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': message
        }
        self.wfile.write(json.dumps(error_response).encode())