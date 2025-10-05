#!/usr/bin/env python3
import requests
import json

def test_pizza_search():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    payload = {
        "message": "Show me pizza options",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("PIZZA SEARCH RESPONSE:")
            print(f"Filters applied: {data.get('search_metadata', {}).get('filters_applied', [])}")
            print(f"Total results: {data.get('search_metadata', {}).get('total_results', 0)}")
            print(f"UI cards count: {len(data.get('ui_cards', []))}")
            
            if data.get('ui_cards'):
                print("\nFirst item:")
                print(json.dumps(data['ui_cards'][0], indent=2))
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pizza_search()
