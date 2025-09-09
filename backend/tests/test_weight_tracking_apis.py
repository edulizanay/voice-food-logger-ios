#!/usr/bin/env python3

# ABOUTME: Comprehensive tests for weight tracking API endpoints
# ABOUTME: Tests weight-entries, user-goals, weight-history, and calorie-history endpoints

import pytest
import requests
import json
import os
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:5001"  # Local testing
# BASE_URL = "https://voice-food-logger-backend.vercel.app"  # Production testing

def test_user_goals_get():
    """Test GET /api/user-goals endpoint"""
    response = requests.get(f"{BASE_URL}/api/user-goals")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "data" in data
    assert "calorie_goal" in data["data"]
    assert "protein_goal" in data["data"]
    assert "weight_goal_kg" in data["data"]
    
    # Verify default values
    assert data["data"]["calorie_goal"] == 1800
    assert data["data"]["protein_goal"] == 160.0
    assert data["data"]["weight_goal_kg"] == 70.0

def test_user_goals_update():
    """Test POST /api/user-goals endpoint"""
    new_goals = {
        "calorie_goal": 2000,
        "protein_goal": 150.0,
        "weight_goal_kg": 68.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-goals",
        json=new_goals,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert data["data"]["calorie_goal"] == 2000
    assert data["data"]["protein_goal"] == 150.0
    assert data["data"]["weight_goal_kg"] == 68.0
    
    # Test validation - invalid calorie goal
    invalid_goals = {"calorie_goal": 100}  # Too low
    response = requests.post(
        f"{BASE_URL}/api/user-goals",
        json=invalid_goals,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400
    assert "must be between" in response.json()["error"]

def test_weight_entries_post():
    """Test POST /api/weight-entries endpoint"""
    weight_data = {
        "weight_kg": 72.3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/weight-entries",
        json=weight_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "Weight entry added successfully" in data["message"]
    
    # Test validation - invalid weight
    invalid_weight = {"weight_kg": 500}  # Too high
    response = requests.post(
        f"{BASE_URL}/api/weight-entries",
        json=invalid_weight,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400
    assert "between 20 and 300" in response.json()["error"]

def test_weight_entries_get():
    """Test GET /api/weight-entries endpoint"""
    response = requests.get(f"{BASE_URL}/api/weight-entries")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "data" in data
    assert isinstance(data["data"], list)
    assert data["count"] >= 0
    
    # Test date filtering
    today = datetime.now().date().isoformat()
    response = requests.get(f"{BASE_URL}/api/weight-entries?start_date={today}&end_date={today}")
    
    assert response.status_code == 200

def test_weight_history_periods():
    """Test GET /api/weight-history with different periods"""
    periods = ["today", "week", "month"]
    
    for period in periods:
        response = requests.get(f"{BASE_URL}/api/weight-history?period={period}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["period"] == period
        assert isinstance(data["data"], list)
        
        # Verify data structure
        if data["data"]:
            entry = data["data"][0]
            assert "date" in entry
            assert "weight_kg" in entry
            assert "goal_weight_kg" in entry

def test_weight_history_latest():
    """Test GET /api/weight-history/latest endpoint"""
    response = requests.get(f"{BASE_URL}/api/weight-history/latest")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    if data["data"]:  # May be None if no entries
        assert "weight_kg" in data["data"]
        assert "created_at" in data["data"]

def test_weight_history_summary():
    """Test GET /api/weight-history/summary endpoint"""
    response = requests.get(f"{BASE_URL}/api/weight-history/summary")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "data" in data
    
    summary = data["data"]
    expected_fields = [
        "current_weight", "goal_weight", "weight_change_month",
        "weight_change_week", "progress_to_goal", "entries_count"
    ]
    
    for field in expected_fields:
        assert field in summary

def test_calorie_history_periods():
    """Test GET /api/calorie-history with different periods"""
    periods = ["today", "week", "month"]
    
    for period in periods:
        response = requests.get(f"{BASE_URL}/api/calorie-history?period={period}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["period"] == period
        assert isinstance(data["data"], list)
        
        # Verify data structure
        if data["data"]:
            entry = data["data"][0]
            assert "date" in entry
            assert "calories" in entry
            assert "goal_calories" in entry

def test_calorie_history_today():
    """Test GET /api/calorie-history/today endpoint"""
    response = requests.get(f"{BASE_URL}/api/calorie-history/today")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "data" in data
    
    progress = data["data"]
    expected_fields = [
        "date", "current_calories", "goal_calories",
        "remaining_calories", "progress_percentage", "is_over_goal"
    ]
    
    for field in expected_fields:
        assert field in progress

def test_calorie_history_summary():
    """Test GET /api/calorie-history/summary endpoint"""
    periods = ["week", "month"]
    
    for period in periods:
        response = requests.get(f"{BASE_URL}/api/calorie-history/summary?period={period}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        summary = data["data"]
        
        expected_fields = [
            "period", "avg_calories", "goal_calories",
            "days_under_goal", "days_over_goal", "total_days"
        ]
        
        for field in expected_fields:
            assert field in summary

def test_error_handling():
    """Test error handling for invalid requests"""
    # Invalid period
    response = requests.get(f"{BASE_URL}/api/weight-history?period=invalid")
    assert response.status_code == 400
    
    # Missing request body
    response = requests.post(f"{BASE_URL}/api/weight-entries")
    assert response.status_code == 400
    
    # Invalid JSON
    response = requests.post(
        f"{BASE_URL}/api/user-goals",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400

def test_weight_entry_crud():
    """Test complete CRUD cycle for weight entries"""
    # Create
    weight_data = {"weight_kg": 71.5}
    response = requests.post(
        f"{BASE_URL}/api/weight-entries",
        json=weight_data,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    
    # Read - verify it exists
    response = requests.get(f"{BASE_URL}/api/weight-entries")
    assert response.status_code == 200
    entries = response.json()["data"]
    
    # Find our entry
    test_entry = None
    for entry in entries:
        if abs(float(entry["weight_kg"]) - 71.5) < 0.01:
            test_entry = entry
            break
    
    assert test_entry is not None
    entry_id = test_entry["id"]
    
    # Delete
    response = requests.delete(f"{BASE_URL}/api/weight-entries/{entry_id}")
    assert response.status_code == 200

if __name__ == "__main__":
    # Run basic connectivity test
    print("🧪 Running Weight Tracking API Tests...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✅ Server accessible at {BASE_URL}")
        
        # Run key tests manually
        test_user_goals_get()
        print("✅ User goals GET test passed")
        
        test_weight_entries_get()
        print("✅ Weight entries GET test passed")
        
        test_weight_history_periods()
        print("✅ Weight history periods test passed")
        
        test_calorie_history_today()
        print("✅ Calorie history today test passed")
        
        print("\n🎉 All key tests passed!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("Please ensure the server is running locally or update BASE_URL for production testing")
    except Exception as e:
        print(f"❌ Test failed: {e}")