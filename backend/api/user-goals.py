# ABOUTME: API endpoint for user goals management 
# ABOUTME: Handles GET (fetch) and POST (update) user goals for weight/calorie targets

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

def get_user_goals():
    """Get current user goals from Supabase"""
    try:
        supabase = _get_supabase_client()
        
        # Get the most recent goals entry (there should typically be only one)
        result = supabase.table("user_goals").select("*").order("created_at", desc=True).limit(1).execute()
        
        if result.data:
            return result.data[0]
        else:
            # Return default goals if none exist
            return {
                "id": None,
                "calorie_goal": 1800,
                "protein_goal": 160.0,
                "weight_goal_kg": 70.0,
                "created_at": None,
                "updated_at": None
            }
            
    except Exception as e:
        print(f"Error retrieving user goals: {e}")
        return None

def update_user_goals(goals_data: dict) -> bool:
    """Update or insert user goals"""
    try:
        supabase = _get_supabase_client()
        
        # Check if goals already exist
        existing = supabase.table("user_goals").select("id").limit(1).execute()
        
        goals_update = {
            "calorie_goal": goals_data.get("calorie_goal", 1800),
            "protein_goal": goals_data.get("protein_goal", 160.0),
            "weight_goal_kg": goals_data.get("weight_goal_kg", 70.0),
            "updated_at": datetime.now().isoformat()
        }
        
        if existing.data:
            # Update existing goals
            goal_id = existing.data[0]['id']
            result = supabase.table("user_goals").update(goals_update).eq("id", goal_id).execute()
        else:
            # Insert new goals
            goals_update["created_at"] = datetime.now().isoformat()
            result = supabase.table("user_goals").insert(goals_update).execute()
        
        return True
        
    except Exception as e:
        print(f"Error updating user goals: {e}")
        return False

@app.route('/api/user-goals', methods=['GET'])
def get_user_goals_endpoint():
    """GET /api/user-goals - Fetch current user goals"""
    try:
        goals = get_user_goals()
        
        if goals is not None:
            return jsonify({
                "success": True,
                "data": goals
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to retrieve user goals"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user-goals', methods=['POST'])
def update_user_goals_endpoint():
    """POST /api/user-goals - Update user goals"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request body"
            }), 400
        
        # Validate input data
        calorie_goal = data.get('calorie_goal')
        protein_goal = data.get('protein_goal')
        weight_goal_kg = data.get('weight_goal_kg')
        
        # Basic validation
        if calorie_goal is not None:
            calorie_goal = int(calorie_goal)
            if calorie_goal < 800 or calorie_goal > 5000:
                return jsonify({
                    "success": False,
                    "error": "Calorie goal must be between 800 and 5000"
                }), 400
        
        if protein_goal is not None:
            protein_goal = float(protein_goal)
            if protein_goal < 20 or protein_goal > 500:
                return jsonify({
                    "success": False,
                    "error": "Protein goal must be between 20 and 500g"
                }), 400
        
        if weight_goal_kg is not None:
            weight_goal_kg = float(weight_goal_kg)
            if weight_goal_kg < 20 or weight_goal_kg > 300:
                return jsonify({
                    "success": False,
                    "error": "Weight goal must be between 20 and 300 kg"
                }), 400
        
        # Update goals
        success = update_user_goals(data)
        
        if success:
            # Return updated goals
            updated_goals = get_user_goals()
            return jsonify({
                "success": True,
                "message": "Goals updated successfully",
                "data": updated_goals
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update goals"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)