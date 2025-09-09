# ABOUTME: API endpoint for weight entries CRUD operations
# ABOUTME: Handles GET (fetch), POST (add), and DELETE (remove) weight entries

from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import _get_supabase_client

app = Flask(__name__)

def store_weight_entry(weight_kg: float, timestamp: datetime = None) -> bool:
    """Store a weight entry to Supabase database"""
    try:
        supabase = _get_supabase_client()
        
        if timestamp is None:
            timestamp = datetime.now()
        
        entry_data = {
            "weight_kg": weight_kg,
            "created_at": timestamp.isoformat()
        }
        
        result = supabase.table("weight_entries").insert(entry_data).execute()
        return True
        
    except Exception as e:
        print(f"Error storing weight entry: {e}")
        return False

def get_weight_entries(start_date: str = None, end_date: str = None, limit: int = 100) -> list:
    """Get weight entries from Supabase with optional date filtering"""
    try:
        supabase = _get_supabase_client()
        
        query = supabase.table("weight_entries").select("*")
        
        if start_date:
            query = query.gte("created_at", f"{start_date}T00:00:00")
        
        if end_date:
            query = query.lte("created_at", f"{end_date}T23:59:59")
            
        query = query.order("created_at", desc=False).limit(limit)
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        print(f"Error retrieving weight entries: {e}")
        return []

def delete_weight_entry(entry_id: int) -> bool:
    """Delete a weight entry by ID"""
    try:
        supabase = _get_supabase_client()
        
        result = supabase.table("weight_entries").delete().eq("id", entry_id).execute()
        return len(result.data) > 0
        
    except Exception as e:
        print(f"Error deleting weight entry {entry_id}: {e}")
        return False

@app.route('/api/weight-entries', methods=['GET'])
def get_weight_entries_endpoint():
    """GET /api/weight-entries - Fetch weight entries by date range"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        # Fetch entries
        entries = get_weight_entries(start_date, end_date, limit)
        
        return jsonify({
            "success": True,
            "data": entries,
            "count": len(entries)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weight-entries', methods=['POST'])
def add_weight_entry_endpoint():
    """POST /api/weight-entries - Add new weight entry"""
    try:
        data = request.get_json()
        
        if not data or 'weight_kg' not in data:
            return jsonify({
                "success": False,
                "error": "Missing weight_kg in request body"
            }), 400
        
        weight_kg = float(data['weight_kg'])
        
        # Validate weight range (reasonable human weight: 20-300 kg)
        if weight_kg < 20 or weight_kg > 300:
            return jsonify({
                "success": False,
                "error": "Weight must be between 20 and 300 kg"
            }), 400
        
        # Parse timestamp if provided, otherwise use current time
        timestamp = None
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except:
                pass  # Use current time if parsing fails
        
        # Store the weight entry
        success = store_weight_entry(weight_kg, timestamp)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Weight entry added successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to store weight entry"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weight-entries/<int:entry_id>', methods=['DELETE'])
def delete_weight_entry_endpoint(entry_id):
    """DELETE /api/weight-entries/{id} - Remove weight entry by ID"""
    try:
        success = delete_weight_entry(entry_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Weight entry {entry_id} deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Weight entry {entry_id} not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)