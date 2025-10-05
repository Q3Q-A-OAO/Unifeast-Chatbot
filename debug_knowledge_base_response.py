#!/usr/bin/env python3
import requests
import json

def get_full_response():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    payload = {
        "message": "What cuisines are available?",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("FULL RESPONSE:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_full_response()
