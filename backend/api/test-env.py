import os
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Test endpoint to check environment variables"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Check key environment variables (don't expose full values)
        env_status = {
            'GROQ_API_KEY': 'SET' if os.getenv('GROQ_API_KEY') else 'MISSING',
            'SUPABASE_URL': 'SET' if os.getenv('SUPABASE_URL') else 'MISSING',
            'SUPABASE_KEY': 'SET' if os.getenv('SUPABASE_KEY') else 'MISSING',
            'python_path': os.getcwd(),
            'shared_exists': os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'shared'))
        }
        
        response = {
            'success': True,
            'environment': env_status
        }
        
        self.wfile.write(json.dumps(response).encode())
        return