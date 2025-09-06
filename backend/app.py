import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from transcription import transcribe_file
from processing import process_food_text
from storage import store_food_data, get_today_entries, get_daily_totals, get_entries_by_date, get_daily_totals_by_date

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for iOS app integration
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Allow all origins for development
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def allowed_file(filename):
    """Check if file is a supported audio file"""
    supported_formats = ['.wav', '.webm', '.mp3', '.m4a', '.ogg']
    return any(filename.lower().endswith(fmt) for fmt in supported_formats)

# Web Interface Routes (keep original for backward compatibility)
@app.route('/')
def index():
    """Main page with recording interface and today's entries"""
    today_entries = get_today_entries()
    daily_totals = get_daily_totals()
    return render_template('index.html', entries=today_entries, daily_totals=daily_totals)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """Legacy web interface endpoint"""
    return process_audio_upload()

# iOS API Routes
@app.route('/api/process-audio', methods=['POST'])
def api_process_audio():
    """Main audio processing endpoint for iOS app"""
    return process_audio_upload()

def process_audio_upload():
    """Handle audio file upload and process through the pipeline"""
    try:
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Please select a supported audio file (WAV, WebM, MP3, etc.)'}), 400
        
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
            return jsonify({
                'success': True,
                'transcription': transcription,
                'items': parsed_data['items'],
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            # Clean up temporary file
            os.remove(temp_path)
            os.rmdir(temp_dir)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy web API endpoints (keep for backward compatibility)
@app.route('/entries')
def get_entries():
    """Legacy API endpoint to get today's entries"""
    entries = get_today_entries()
    return jsonify(entries)

@app.route('/daily_totals')
def get_daily_totals_api():
    """Legacy API endpoint to get daily macro totals"""
    totals = get_daily_totals()
    return jsonify(totals)

# iOS API endpoints
@app.route('/api/entries/<date>', methods=['GET'])
def api_get_entries_by_date(date):
    """Get food entries for a specific date (YYYY-MM-DD format)"""
    try:
        entries = get_entries_by_date(date)
        return jsonify({
            'success': True,
            'date': date,
            'entries': entries
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/entries', methods=['GET'])
def api_get_today_entries():
    """Get today's food entries"""
    try:
        entries = get_today_entries()
        return jsonify({
            'success': True,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'entries': entries
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-totals/<date>', methods=['GET'])
def api_get_daily_totals_by_date(date):
    """Get daily macro totals for a specific date (YYYY-MM-DD format)"""
    try:
        totals = get_daily_totals_by_date(date)
        return jsonify({
            'success': True,
            'date': date,
            'totals': totals
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-totals', methods=['GET'])
def api_get_today_totals():
    """Get today's daily macro totals"""
    try:
        totals = get_daily_totals()
        return jsonify({
            'success': True,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'totals': totals
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/nutrition-database', methods=['GET'])
def api_get_nutrition_database():
    """Get available foods in the nutrition database"""
    try:
        import json
        with open('data/nutrition_db.json', 'r') as f:
            nutrition_db = json.load(f)
        
        foods = []
        for food_name, macros in nutrition_db.items():
            foods.append({
                'name': food_name,
                'macros': macros
            })
        
        return jsonify({
            'success': True,
            'foods': foods,
            'count': len(foods)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/manual-entry', methods=['POST'])
def api_manual_entry():
    """Process a manual text food entry (for keyboard input)"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided. Please include "text" field in JSON.'
            }), 400
        
        # Process the text directly (skip transcription)
        text = data['text']
        parsed_data = process_food_text(text)
        
        # Store the data
        store_food_data(parsed_data['items'])
        
        return jsonify({
            'success': True,
            'original_text': text,
            'items': parsed_data['items'],
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_pipeline')
def test_pipeline():
    """Test endpoint to verify the pipeline works"""
    test_audio = "test_data/sample_food_recording.wav"
    
    if not os.path.exists(test_audio):
        return jsonify({
            'error': 'Test audio file not found',
            'message': 'Please add a sample WAV file at test_data/sample_food_recording.wav'
        }), 404
    
    try:
        transcription = transcribe_file(test_audio)
        parsed_data = process_food_text(transcription)
        
        return jsonify({
            'success': True,
            'transcription': transcription,
            'parsed_data': parsed_data,
            'message': 'Pipeline test successful'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if GROQ_API_KEY is set
    if not os.getenv('GROQ_API_KEY'):
        print("ERROR: GROQ_API_KEY environment variable not set!")
        print("Please set your API key in the .env file")
        exit(1)
    
    print("Voice Food Logger starting...")
    print("Access the app at: http://localhost:8080")
    print("Test pipeline at: http://localhost:8080/test_pipeline")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('test_data', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8080)