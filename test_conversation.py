#!/usr/bin/env python3
"""
Test script to have a conversation with the deployed Railway API
"""

import requests
import json
import time

# Your Railway API URL
API_URL = "https://unifeast-chatbot-production.up.railway.app"

def send_message(message, user_id="test_user", session_id="conversation_1"):
    """Send a message to the API and return the response"""
    try:
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id
        }
        
        print(f"🤖 You: {message}")
        
        response = requests.post(f"{API_URL}/chat", json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"🤖 Bot: {data['response']}")
        print(f"⏰ Time: {data.get('timestamp', 'N/A')}")
        print("-" * 50)
        
        return data['response']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"🏥 Health Check: {data}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    print("🚀 Starting conversation test with UniFeast MCP Chatbot API")
    print("=" * 60)
    
    # Test health first
    if not test_health():
        print("❌ API is not healthy. Exiting.")
        return
    
    print("\n💬 Starting conversation...")
    print("=" * 60)
    
    # Test conversation
    conversation = [
        "Hello! I'm looking for food recommendations.",
        "I love spicy food, what do you recommend?",
        "I'm also vegetarian, so no meat please.",
        "What about Indian cuisine?",
        "Can you help me find restaurants near me?"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n📝 Message {i}:")
        response = send_message(message)
        if not response:
            print("❌ Failed to get response. Stopping conversation.")
            break
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n✅ Conversation test completed!")
    print(f"🌐 API URL: {API_URL}")

if __name__ == "__main__":
    main()


