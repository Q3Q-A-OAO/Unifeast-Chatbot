#!/usr/bin/env python3
import requests
import json

def test_file_loading():
    """Test if the deployed API can access our knowledge base file"""
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    # Test with a message that should trigger knowledge base usage
    payload = {
        "message": "What pizza restaurants do you have?",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("RESPONSE:")
            print(f"Text: {data.get('text_bubble', 'No text')}")
            print(f"Filters: {data.get('search_metadata', {}).get('filters_applied', [])}")
            
            # Check if it mentions Pizza Pi (our updated restaurant)
            text = data.get('text_bubble', '').lower()
            if 'pizza pi' in text:
                print("✅ Pizza Pi mentioned - knowledge base is updated!")
            else:
                print("❌ Pizza Pi NOT mentioned - using old knowledge base")
                
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_file_loading()
