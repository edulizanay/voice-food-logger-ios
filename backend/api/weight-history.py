# ABOUTME: API endpoint for weight history data aggregated by time periods
# ABOUTME: Provides weight data formatted for chart consumption with goal weight overlay

from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import _get_supabase_client

app = Flask(__name__)

def get_weight_history_by_period(period: str, start_date: str = None, end_date: str = None) -> list:
    """Get weight data aggregated by time period for charts"""
    try:
        supabase = _get_supabase_client()
        
        # Calculate date range based on period
        now = datetime.now()
        
        if not start_date or not end_date:
            if period == "today":
                start_date = now.date().isoformat()
                end_date = now.date().isoformat()
            elif period == "week":
                start_date = (now - timedelta(days=7)).date().isoformat()
                end_date = now.date().isoformat()
            elif period == "month":
                start_date = (now - timedelta(days=30)).date().isoformat()
                end_date = now.date().isoformat()
            else:
                # Default to week if unknown period
                start_date = (now - timedelta(days=7)).date().isoformat()
                end_date = now.date().isoformat()
        
        # Query weight entries in date range
        result = supabase.table("weight_entries") \
            .select("*") \
            .gte("created_at", f"{start_date}T00:00:00") \
            .lte("created_at", f"{end_date}T23:59:59") \
            .order("created_at", desc=False) \
            .execute()
        
        # Get current user goals for goal weight
        goals_result = supabase.table("user_goals").select("weight_goal_kg").limit(1).execute()
        goal_weight_kg = goals_result.data[0]["weight_goal_kg"] if goals_result.data else None
        
        # Format data for charts
        chart_data = []
        for entry in result.data:
            chart_data.append({
                "date": entry["created_at"].split("T")[0],  # Just the date part
                "weight_kg": float(entry["weight_kg"]),
                "goal_weight_kg": float(goal_weight_kg) if goal_weight_kg else None,
                "entry_id": entry["id"]
            })
        
        return chart_data
        
    except Exception as e:
        print(f"Error retrieving weight history: {e}")
        return []

def get_latest_weight() -> dict:
    """Get the most recent weight entry"""
    try:
        supabase = _get_supabase_client()
        
        result = supabase.table("weight_entries") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        if result.data:
            entry = result.data[0]
            return {
                "weight_kg": float(entry["weight_kg"]),
                "created_at": entry["created_at"],
                "entry_id": entry["id"]
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error retrieving latest weight: {e}")
        return None

@app.route('/api/weight-history', methods=['GET'])
def get_weight_history_endpoint():
    """GET /api/weight-history - Weight data aggregated by time period"""
    try:
        # Get query parameters
        period = request.args.get('period', 'week')  # today, week, month
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate period
        valid_periods = ['today', 'week', 'month']
        if period not in valid_periods:
            return jsonify({
                "success": False,
                "error": f"Invalid period. Must be one of: {', '.join(valid_periods)}"
            }), 400
        
        # Get weight history
        history = get_weight_history_by_period(period, start_date, end_date)
        
        return jsonify({
            "success": True,
            "data": history,
            "period": period,
            "count": len(history)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weight-history/latest', methods=['GET'])
def get_latest_weight_endpoint():
    """GET /api/weight-history/latest - Get most recent weight entry"""
    try:
        latest = get_latest_weight()
        
        if latest:
            return jsonify({
                "success": True,
                "data": latest
            })
        else:
            return jsonify({
                "success": True,
                "data": None,
                "message": "No weight entries found"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weight-history/summary', methods=['GET'])
def get_weight_summary_endpoint():
    """GET /api/weight-history/summary - Get weight progress summary"""
    try:
        # Get weight history for the past month
        history = get_weight_history_by_period("month")
        
        if not history:
            return jsonify({
                "success": True,
                "data": {
                    "current_weight": None,
                    "goal_weight": None,
                    "weight_change_month": 0,
                    "weight_change_week": 0,
                    "progress_to_goal": 0,
                    "entries_count": 0
                }
            })
        
        # Calculate summary statistics
        current_weight = history[-1]["weight_kg"] if history else None
        goal_weight = history[-1]["goal_weight_kg"] if history else None
        
        # Weight change calculations
        weight_change_month = 0
        weight_change_week = 0
        
        if len(history) > 1:
            weight_change_month = current_weight - history[0]["weight_kg"]
            
            # Calculate week change (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
            week_entries = [h for h in history if h["date"] >= week_ago]
            if len(week_entries) > 1:
                weight_change_week = current_weight - week_entries[0]["weight_kg"]
        
        # Progress to goal
        progress_to_goal = 0
        if goal_weight and current_weight and goal_weight != current_weight:
            if goal_weight < current_weight:  # Weight loss goal
                initial_weight = history[0]["weight_kg"] if history else current_weight
                total_to_lose = initial_weight - goal_weight
                lost_so_far = initial_weight - current_weight
                if total_to_lose > 0:
                    progress_to_goal = (lost_so_far / total_to_lose) * 100
            else:  # Weight gain goal
                initial_weight = history[0]["weight_kg"] if history else current_weight
                total_to_gain = goal_weight - initial_weight
                gained_so_far = current_weight - initial_weight
                if total_to_gain > 0:
                    progress_to_goal = (gained_so_far / total_to_gain) * 100
        
        summary = {
            "current_weight": current_weight,
            "goal_weight": goal_weight,
            "weight_change_month": round(weight_change_month, 1),
            "weight_change_week": round(weight_change_week, 1),
            "progress_to_goal": round(progress_to_goal, 1),
            "entries_count": len(history)
        }
        
        return jsonify({
            "success": True,
            "data": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)