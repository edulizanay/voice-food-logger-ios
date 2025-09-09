import os
import sys
import json
import re
from http.server import BaseHTTPRequestHandler

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import _get_supabase_client

class handler(BaseHTTPRequestHandler):
    def do_DELETE(self):
        """Handle DELETE requests for individual entries"""
        try:
            # Extract entry ID from path: /api/entry/123 or /api/entries/123
            path = self.path
            entry_id_match = re.search(r'/api/entr(?:y|ies)/([a-f0-9\-]+)', path)
            
            if not entry_id_match:
                self.send_error_response(400, "Invalid entry ID format")
                return
            
            entry_id = entry_id_match.group(1)
            
            # Delete from Supabase - try session_id first, then id
            supabase = _get_supabase_client()
            
            # First try to delete by session_id (for grouped entries)
            result = supabase.table("food_entries").delete().eq("session_id", entry_id).execute()
            
            # If no rows deleted by session_id, try by id (for individual entries)
            if not result.data:
                result = supabase.table("food_entries").delete().eq("id", entry_id).execute()
            
            if not result.data:
                self.send_error_response(404, "Entry not found")
                return
            
            response_data = {
                'success': True,
                'message': f'Entry {entry_id} deleted successfully'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_PUT(self):
        """Handle PUT requests for updating entries"""
        try:
            # Extract entry ID from path
            path = self.path
            entry_id_match = re.search(r'/api/entr(?:y|ies)/([a-f0-9\-]+)', path)
            
            if not entry_id_match:
                self.send_error_response(400, "Invalid entry ID format")
                return
            
            entry_id = entry_id_match.group(1)
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            request_data = json.loads(body)
            
            new_quantity = request_data.get('quantity')
            if not new_quantity:
                self.send_error_response(400, "Missing 'quantity' field")
                return
            
            # Update in Supabase
            supabase = _get_supabase_client()
            result = supabase.table("food_entries").update({
                "quantity": new_quantity
            }).eq("id", entry_id).execute()
            
            if not result.data:
                self.send_error_response(404, "Entry not found")
                return
            
            response_data = {
                'success': True,
                'message': f'Entry {entry_id} updated successfully',
                'updated_entry': result.data[0]
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
        self.send_header('Access-Control-Allow-Methods', 'GET, DELETE, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
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