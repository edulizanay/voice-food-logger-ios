import os
import sys
import json
import tempfile
import cgi
import io
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from transcription import transcribe_file
from processing import process_food_text
from supabase_storage import store_food_data

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for voice upload"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error_response(400, 'Multipart form data required')
                return
            
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, 'No data received')
                return
            
            # Read the body
            body = self.rfile.read(content_length)
            
            # Parse multipart data
            form_data = cgi.FieldStorage(
                fp=io.BytesIO(body),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Check for audio file
            if 'audio' not in form_data:
                self.send_error_response(400, 'No audio file provided')
                return
            
            audio_field = form_data['audio']
            if not hasattr(audio_field, 'filename') or not audio_field.filename:
                self.send_error_response(400, 'Invalid audio file')
                return
            
            if not allowed_file(audio_field.filename):
                self.send_error_response(400, 'Unsupported file format')
                return
            
            # Save uploaded file temporarily
            filename = secure_filename(audio_field.filename)
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(audio_field.file.read())
            
            try:
                # Step 1: Transcribe audio
                transcription = transcribe_file(temp_path)
                
                # Step 2: Process food description
                parsed_data = process_food_text(transcription)
                
                # Step 3: Store food data
                store_food_data(parsed_data['items'])
                
                # Return success response
                response_data = {
                    'success': True,
                    'transcription': transcription,
                    'items': parsed_data['items'],
                    'timestamp': datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_data).encode())
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
        
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
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

def allowed_file(filename):
    """Check if file is a supported audio file"""
    supported_formats = ['.wav', '.webm', '.mp3', '.m4a', '.ogg']
    return any(filename.lower().endswith(fmt) for fmt in supported_formats)

def secure_filename(filename):
    """Basic secure filename function"""
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename or 'audio.wav'