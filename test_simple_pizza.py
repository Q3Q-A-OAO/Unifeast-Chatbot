#!/usr/bin/env python3
import requests
import json
import time

def test_simple_pizza():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🍕 TESTING SIMPLE PIZZA QUERIES")
    print("=" * 50)
    
    # Test different pizza query variations
    test_cases = [
        ("pizza", "Single word"),
        ("I want pizza", "Simple request"),
        ("Show pizza", "Short request"),
        ("Pizza please", "Polite request"),
    ]
    
    for message, description in test_cases:
        print(f"\n📝 Testing: '{message}' ({description})")
        
        payload = {
            "message": message,
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        try:
            start_time = time.time()
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                                   data=json.dumps(payload), timeout=90)
            end_time = time.time()
            
            print(f"   ⏱️  Time: {end_time - start_time:.2f}s")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                search_metadata = data.get('search_metadata', {})
                filters_applied = search_metadata.get('filters_applied', [])
                total_results = search_metadata.get('total_results', 0)
                text_bubble = data.get('text_bubble', '')
                
                print(f"   🔍 Filters: {filters_applied}")
                print(f"   📊 Results: {total_results}")
                
                if "iteration limit" in text_bubble.lower():
                    print(f"   ❌ Hit iteration limit")
                elif "time limit" in text_bubble.lower():
                    print(f"   ❌ Hit time limit")
                elif total_results > 0:
                    print(f"   ✅ SUCCESS - Found {total_results} results!")
                else:
                    print(f"   ❌ No results found")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple_pizza()
