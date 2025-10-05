#!/usr/bin/env python3
"""
Debug script to test knowledge base directly
"""
import requests
import json

def test_knowledge_base_query():
    """Test if knowledge base is working"""
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    # Test knowledge base query directly
    message = "What cuisines are available?"
    
    payload = {
        "message": message,
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Knowledge base query successful")
            print(f"Response: {data.get('text_bubble', 'No text')}")
            
            # Check if it mentions International cuisine
            text = data.get('text_bubble', '').lower()
            if 'international' in text:
                print("✅ International cuisine mentioned")
            else:
                print("❌ International cuisine NOT mentioned")
                
        else:
            print(f"❌ Knowledge base query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Knowledge Base on Deployed API")
    print("=" * 50)
    test_knowledge_base_query()
