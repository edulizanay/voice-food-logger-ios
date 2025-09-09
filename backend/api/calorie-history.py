# ABOUTME: API endpoint for calorie history data aggregated by time periods
# ABOUTME: Extends existing daily-totals logic for chart consumption with goal calorie overlay

from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import _get_supabase_client, get_daily_totals_by_date

app = Flask(__name__)

def get_calorie_history_by_period(period: str, start_date: str = None, end_date: str = None) -> list:
    """Get calorie data aggregated by time period for charts"""
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
        
        # Get current user goals for goal calories
        goals_result = supabase.table("user_goals").select("calorie_goal").limit(1).execute()
        goal_calories = goals_result.data[0]["calorie_goal"] if goals_result.data else 1800
        
        # Generate date range
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        chart_data = []
        current_date = start_dt
        
        while current_date <= end_dt:
            date_str = current_date.date().isoformat()
            
            # Get daily totals for this date (reusing existing function)
            daily_totals = get_daily_totals_by_date(date_str)
            
            chart_data.append({
                "date": date_str,
                "calories": daily_totals["calories"],
                "goal_calories": goal_calories,
                "protein_g": daily_totals["protein_g"],
                "carbs_g": daily_totals["carbs_g"],
                "fat_g": daily_totals["fat_g"]
            })
            
            current_date += timedelta(days=1)
        
        return chart_data
        
    except Exception as e:
        print(f"Error retrieving calorie history: {e}")
        return []

def get_calorie_summary(period: str = "week") -> dict:
    """Get calorie intake summary statistics"""
    try:
        history = get_calorie_history_by_period(period)
        
        if not history:
            return {
                "period": period,
                "avg_calories": 0,
                "goal_calories": 1800,
                "days_under_goal": 0,
                "days_over_goal": 0,
                "total_days": 0
            }
        
        # Calculate statistics
        total_calories = sum(day["calories"] for day in history)
        goal_calories = history[0]["goal_calories"] if history else 1800
        
        days_under_goal = sum(1 for day in history if day["calories"] < goal_calories)
        days_over_goal = sum(1 for day in history if day["calories"] > goal_calories)
        days_at_goal = len(history) - days_under_goal - days_over_goal
        
        avg_calories = total_calories / len(history) if history else 0
        
        return {
            "period": period,
            "avg_calories": round(avg_calories),
            "goal_calories": goal_calories,
            "days_under_goal": days_under_goal,
            "days_over_goal": days_over_goal,
            "days_at_goal": days_at_goal,
            "total_days": len(history)
        }
        
    except Exception as e:
        print(f"Error calculating calorie summary: {e}")
        return {}

@app.route('/api/calorie-history', methods=['GET'])
def get_calorie_history_endpoint():
    """GET /api/calorie-history - Calorie data aggregated by time period"""
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
        
        # Get calorie history
        history = get_calorie_history_by_period(period, start_date, end_date)
        
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

@app.route('/api/calorie-history/summary', methods=['GET'])
def get_calorie_summary_endpoint():
    """GET /api/calorie-history/summary - Get calorie intake summary statistics"""
    try:
        period = request.args.get('period', 'week')
        
        # Validate period
        valid_periods = ['today', 'week', 'month']
        if period not in valid_periods:
            return jsonify({
                "success": False,
                "error": f"Invalid period. Must be one of: {', '.join(valid_periods)}"
            }), 400
        
        summary = get_calorie_summary(period)
        
        return jsonify({
            "success": True,
            "data": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/calorie-history/today', methods=['GET'])
def get_today_calorie_progress():
    """GET /api/calorie-history/today - Get today's calorie progress"""
    try:
        today = datetime.now().date().isoformat()
        
        # Get today's totals (reusing existing function)
        daily_totals = get_daily_totals_by_date(today)
        
        # Get goal calories
        supabase = _get_supabase_client()
        goals_result = supabase.table("user_goals").select("calorie_goal").limit(1).execute()
        goal_calories = goals_result.data[0]["calorie_goal"] if goals_result.data else 1800
        
        # Calculate progress
        progress_percentage = (daily_totals["calories"] / goal_calories * 100) if goal_calories > 0 else 0
        remaining_calories = max(0, goal_calories - daily_totals["calories"])
        
        progress_data = {
            "date": today,
            "current_calories": daily_totals["calories"],
            "goal_calories": goal_calories,
            "remaining_calories": remaining_calories,
            "progress_percentage": round(progress_percentage, 1),
            "is_over_goal": daily_totals["calories"] > goal_calories,
            "macros": {
                "protein_g": daily_totals["protein_g"],
                "carbs_g": daily_totals["carbs_g"],
                "fat_g": daily_totals["fat_g"]
            }
        }
        
        return jsonify({
            "success": True,
            "data": progress_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)