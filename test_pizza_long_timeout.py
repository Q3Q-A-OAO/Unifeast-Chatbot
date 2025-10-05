#!/usr/bin/env python3
import requests
import json
import time

def test_pizza_with_long_timeout():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🍕 TESTING PIZZA SEARCH WITH LONG TIMEOUT")
    print("=" * 50)
    
    payload = {
        "message": "Show me pizza options",
        "user_id": "test_user",
        "session_id": "test_session"
    }
    
    print("📝 Sending pizza query...")
    start_time = time.time()
    
    try:
        # Use longer timeout
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=120)  # 2 minutes
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS - Valid JSON response")
            
            # Check response structure
            search_metadata = data.get('search_metadata', {})
            filters_applied = search_metadata.get('filters_applied', [])
            total_results = search_metadata.get('total_results', 0)
            ui_cards = data.get('ui_cards', [])
            text_bubble = data.get('text_bubble', '')
            
            print(f"🔍 Filters applied: {filters_applied}")
            print(f"📊 Total results: {total_results}")
            print(f"🍕 UI cards count: {len(ui_cards)}")
            print(f"💬 Response text: {text_bubble[:200]}...")
            
            if total_results > 0:
                print("🎉 SUCCESS - Found pizza items!")
                for i, item in enumerate(ui_cards[:3]):
                    dish_name = item.get('dish_name', 'Unknown')
                    category = item.get('category', 'Unknown')
                    cuisine = item.get('cuisine_type', 'Unknown')
                    price = item.get('student_price', 'Unknown')
                    print(f"   {i+1}. {dish_name} - {category} ({cuisine}) - £{price}")
            else:
                print("❌ No pizza items found")
                if "iteration limit" in text_bubble.lower():
                    print("   ❌ Agent hit iteration limit")
                elif "time limit" in text_bubble.lower():
                    print("   ❌ Agent hit time limit")
                else:
                    print("   ❌ Unknown issue")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Request took longer than 2 minutes")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pizza_with_long_timeout()
