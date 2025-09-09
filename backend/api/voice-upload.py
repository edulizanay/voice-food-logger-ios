import os
import sys
import json
import tempfile
from datetime import datetime

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from transcription import transcribe_file
from processing import process_food_text
from supabase_storage import store_food_data

def handler(request):
    """Vercel serverless function handler for voice upload"""
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No audio file provided'})
            }
        
        file = request.files['audio']
        if not file.filename or not allowed_file(file.filename):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Please select a supported audio file (WAV, WebM, MP3, etc.)'})
            }
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Step 1: Transcribe audio
            transcription = transcribe_file(temp_path)
            
            # Step 2: Process food description
            parsed_data = process_food_text(transcription)
            
            # Step 3: Store food data
            store_food_data(parsed_data['items'])
            
            # Return success response
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'transcription': transcription,
                    'items': parsed_data['items'],
                    'timestamp': datetime.now().isoformat()
                })
            }
            
        finally:
            # Clean up temporary file
            os.remove(temp_path)
            os.rmdir(temp_dir)
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def allowed_file(filename):
    """Check if file is a supported audio file"""
    supported_formats = ['.wav', '.webm', '.mp3', '.m4a', '.ogg']
    return any(filename.lower().endswith(fmt) for fmt in supported_formats)

def secure_filename(filename):
    """Basic secure filename function"""
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename or 'audio.wav'