#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:5001"

def test_basic_connectivity():
    """Test basic server connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def test_user_goals():
    """Test user goals endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/user-goals")
        print(f"User goals GET: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"User goals error: {e}")
        return False

def test_weight_entries():
    """Test weight entries endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/weight-entries")
        print(f"Weight entries GET: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Weight entries error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debug API Testing...")
    
    if test_basic_connectivity():
        print("✅ Server accessible")
        
        if test_user_goals():
            print("✅ User goals working")
        else:
            print("❌ User goals failed")
            
        if test_weight_entries():
            print("✅ Weight entries working")
        else:
            print("❌ Weight entries failed")
    else:
        print("❌ Server not accessible")