#!/usr/bin/env python3
"""
Test script for the deployed Railway API
"""
import requests
import json
import time
import os

# Use the Railway provided URL
API_URL = os.getenv("RAILWAY_API_URL", "https://unifeast-chatbot-production.up.railway.app")

def test_health_check():
    """Test the health endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health Check: {data['status']}")
        print(f"📊 Services: {data.get('services', {})}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat_endpoint(message: str, user_id: str = "test_user"):
    """Test the chat endpoint"""
    print(f"\n💬 Testing Chat: '{message}'")
    try:
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": f"test_session_{int(time.time())}"
        }
        
        response = requests.post(
            f"{API_URL}/chat", 
            json=payload, 
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Response: {data.get('response', 'No response')}")
        print(f"👤 User: {data.get('user_id', 'Unknown')}")
        print(f"⏰ Time: {data.get('timestamp', 'Unknown')}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"📝 Error details: {error_data}")
            except:
                print(f"📝 Error response: {e.response.text}")
        return False

def run_comprehensive_test():
    """Run a comprehensive test of the API"""
    print("🚀 Starting Comprehensive API Test")
    print("=" * 50)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Health check failed. Aborting tests.")
        return False
    
    # Wait a bit for the API to fully initialize
    print("\n⏳ Waiting for API to fully initialize...")
    time.sleep(10)
    
    # Test 2: Basic Chat
    test_messages = [
        "Hello! Can you help me find food?",
        "I'm looking for spicy food recommendations",
        "What about vegetarian options?",
        "Can you search for Indian restaurants?"
    ]
    
    print(f"\n🧪 Testing {len(test_messages)} chat messages...")
    success_count = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i}/{len(test_messages)} ---")
        if test_chat_endpoint(message):
            success_count += 1
        time.sleep(2)  # Small delay between requests
    
    print(f"\n📊 Test Results: {success_count}/{len(test_messages)} successful")
    
    if success_count == len(test_messages):
        print("🎉 All tests passed! Your API is working perfectly!")
        return True
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    print(f"🌐 Testing API at: {API_URL}")
    print("=" * 50)
    
    success = run_comprehensive_test()
    
    if success:
        print(f"\n✅ API is ready for your frontend team!")
        print(f"🔗 API URL: {API_URL}")
        print(f"📋 Endpoints:")
        print(f"   - GET  {API_URL}/health")
        print(f"   - POST {API_URL}/chat")
    else:
        print(f"\n❌ API needs debugging. Check Railway logs.")





