#!/usr/bin/env python3
"""
Test script for Railway deployed API
Replace YOUR_RAILWAY_URL with your actual Railway URL
"""

import requests
import json

# Replace this with your actual Railway URL
RAILWAY_URL = "https://YOUR_APP_NAME.railway.app"

def test_railway_api():
    """Test the deployed Railway API"""
    print("🚀 Testing Railway Deployed API")
    print("=" * 50)
    print(f"Testing URL: {RAILWAY_URL}")
    
    # Test health
    try:
        response = requests.get(f"{RAILWAY_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test chat
    try:
        response = requests.post(
            f"{RAILWAY_URL}/chat",
            json={"message": "Hello! I want spicy food recommendations", "user_id": "test_user"}
        )
        print(f"\n✅ Chat Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response'][:200]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")

if __name__ == "__main__":
    test_railway_api()
