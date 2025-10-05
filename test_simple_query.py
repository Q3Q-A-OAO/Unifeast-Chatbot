#!/usr/bin/env python3
import requests
import json

def test_simple_query():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🧪 TESTING SIMPLE QUERIES")
    print("=" * 40)
    
    # Test very simple queries
    test_cases = [
        ("Hello", "Basic greeting"),
        ("Hi there", "Simple greeting"), 
        ("What can you do?", "Capability question"),
        ("Show me pizza", "Direct food request"),
    ]
    
    for message, description in test_cases:
        print(f"\n📝 Testing: '{message}' ({description})")
        
        payload = {
            "message": message,
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                                   data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                text_bubble = data.get('text_bubble', '')
                search_metadata = data.get('search_metadata', {})
                
                print(f"   ✅ Status: 200 OK")
                print(f"   📊 Results: {search_metadata.get('total_results', 0)}")
                print(f"   💬 Response: {text_bubble[:100]}...")
                
                if "iteration limit" in text_bubble.lower():
                    print(f"   ❌ HITTING ITERATION LIMIT")
                elif "time limit" in text_bubble.lower():
                    print(f"   ❌ HITTING TIME LIMIT")
                else:
                    print(f"   ✅ Working normally")
                    
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple_query()
