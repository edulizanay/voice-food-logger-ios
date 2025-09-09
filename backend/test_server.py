#!/usr/bin/env python3

# ABOUTME: Local test server for weight tracking API endpoints
# ABOUTME: Combines all API endpoints into one Flask app for testing

from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

# Import storage functions directly
from supabase_storage import get_user_goals, update_user_goals, store_weight_entry, get_weight_entries, delete_weight_entry
from datetime import datetime, timedelta

app = Flask(__name__)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Weight tracking API server is running"})

# User goals endpoints
@app.route('/api/user-goals', methods=['GET'])
def user_goals_get():
    try:
        goals = get_user_goals()
        return jsonify({"success": True, "data": goals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user-goals', methods=['POST'])
def user_goals_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Missing request body"}), 400
        
        # Basic validation
        calorie_goal = data.get('calorie_goal')
        if calorie_goal is not None and (calorie_goal < 800 or calorie_goal > 5000):
            return jsonify({"success": False, "error": "Calorie goal must be between 800 and 5000"}), 400
        
        success = update_user_goals(data)
        if success:
            updated_goals = get_user_goals()
            return jsonify({"success": True, "message": "Goals updated successfully", "data": updated_goals})
        else:
            return jsonify({"success": False, "error": "Failed to update goals"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Weight entries endpoints  
@app.route('/api/weight-entries', methods=['GET'])
def weight_entries_get():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date().isoformat()
        if not end_date:
            end_date = datetime.now().date().isoformat()
            
        entries = get_weight_entries(start_date, end_date)
        return jsonify({"success": True, "data": entries, "count": len(entries)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/weight-entries', methods=['POST'])
def weight_entries_post():
    try:
        data = request.get_json()
        if not data or 'weight_kg' not in data:
            return jsonify({"success": False, "error": "Missing weight_kg in request body"}), 400
        
        weight_kg = float(data['weight_kg'])
        if weight_kg < 20 or weight_kg > 300:
            return jsonify({"success": False, "error": "Weight must be between 20 and 300 kg"}), 400
        
        success = store_weight_entry(weight_kg)
        if success:
            return jsonify({"success": True, "message": "Weight entry added successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to store weight entry"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/weight-entries/<int:entry_id>', methods=['DELETE'])
def weight_entries_delete(entry_id):
    try:
        success = delete_weight_entry(entry_id)
        if success:
            return jsonify({"success": True, "message": f"Weight entry {entry_id} deleted successfully"})
        else:
            return jsonify({"success": False, "error": f"Weight entry {entry_id} not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Basic endpoints for other tests
@app.route('/api/weight-history', methods=['GET'])
def weight_history_get():
    try:
        period = request.args.get('period', 'week')
        if period not in ['today', 'week', 'month']:
            return jsonify({"success": False, "error": "Invalid period"}), 400
            
        # Simple implementation for testing
        entries = get_weight_entries(
            (datetime.now() - timedelta(days=7)).date().isoformat(),
            datetime.now().date().isoformat()
        )
        
        goals = get_user_goals()
        history_data = []
        for entry in entries:
            history_data.append({
                "date": entry["created_at"].split("T")[0],
                "weight_kg": entry["weight_kg"],
                "goal_weight_kg": goals.get("weight_goal_kg")
            })
        
        return jsonify({"success": True, "data": history_data, "period": period, "count": len(history_data)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/weight-history/latest', methods=['GET'])
def weight_history_latest():
    try:
        entries = get_weight_entries(
            (datetime.now() - timedelta(days=30)).date().isoformat(),
            datetime.now().date().isoformat()
        )
        
        if entries:
            latest = entries[-1]  # Last entry
            return jsonify({
                "success": True,
                "data": {
                    "weight_kg": latest["weight_kg"],
                    "created_at": latest["created_at"],
                    "entry_id": latest["id"]
                }
            })
        else:
            return jsonify({"success": True, "data": None, "message": "No weight entries found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Calorie history - simplified for testing
@app.route('/api/calorie-history/today', methods=['GET'])
def calorie_history_today():
    try:
        from supabase_storage import get_daily_totals
        
        today = datetime.now().date().isoformat()
        daily_totals = get_daily_totals()  # Today's totals
        goals = get_user_goals()
        
        goal_calories = goals.get("calorie_goal", 1800)
        progress_percentage = (daily_totals["calories"] / goal_calories * 100) if goal_calories > 0 else 0
        
        return jsonify({
            "success": True,
            "data": {
                "date": today,
                "current_calories": daily_totals["calories"],
                "goal_calories": goal_calories,
                "remaining_calories": max(0, goal_calories - daily_totals["calories"]),
                "progress_percentage": round(progress_percentage, 1),
                "is_over_goal": daily_totals["calories"] > goal_calories,
                "macros": {
                    "protein_g": daily_totals["protein_g"],
                    "carbs_g": daily_totals["carbs_g"],
                    "fat_g": daily_totals["fat_g"]
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Weight Tracking API Test Server...")
    print("📡 Server will be available at: http://localhost:5001")
    print("🩺 Health check: http://localhost:5001/api/health")
    app.run(debug=True, port=5001)