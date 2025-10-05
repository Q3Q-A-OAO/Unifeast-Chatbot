#!/usr/bin/env python3
import requests
import json

def test_direct_pizza_error():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🍕 TESTING DIRECT PIZZA ERROR")
    print("=" * 50)
    
    payload = {
        "message": "pizza",
        "user_id": "test_user",
        "session_id": "test_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            text_bubble = data.get('text_bubble', '')
            
            print(f"💬 Full response: {text_bubble}")
            
            if "error" in text_bubble.lower():
                print("❌ Error detected in response")
            elif "results" in text_bubble.lower() or "pizza" in text_bubble.lower():
                print("✅ Success - got pizza results")
            else:
                print("❓ Unclear response")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_direct_pizza_error()
