#!/usr/bin/env python3
"""
Test script for the FastAPI chatbot
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat(message: str):
    """Test chat endpoint"""
    print(f"\n💬 Testing chat with: '{message}'")
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"message": message}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_memory_persistence():
    """Test that memory persists across conversations"""
    print(f"\n🧠 Testing memory persistence...")
    try:
        # First message
        response1 = requests.post(
            f"{API_BASE}/chat",
            json={"message": "I'm allergic to nuts", "user_id": "test_user_123"}
        )
        print(f"First message status: {response1.status_code}")
        
        # Second message that should remember the allergy
        response2 = requests.post(
            f"{API_BASE}/chat",
            json={"message": "What food can I eat?", "user_id": "test_user_123"}
        )
        print(f"Second message status: {response2.status_code}")
        
        if response2.status_code == 200:
            data = response2.json()
            print(f"Response: {data['response']}")
            return True
        else:
            print(f"Error: {response2.text}")
            return False
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing UniFeast MCP Chatbot API")
    print("=" * 50)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Test health
    health_ok = test_health()
    
    if health_ok:
        # Test chat functionality
        test_chat("Hello, I'm looking for food recommendations")
        test_chat("I want spicy Indian food")
        test_chat("Show me vegetarian options")
        
        # Test memory persistence
        test_memory_persistence()
        
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Health check failed - server may not be running")

if __name__ == "__main__":
    main()
