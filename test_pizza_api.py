#!/usr/bin/env python3
"""
Test script for pizza search API after knowledge base fixes
"""
import requests
import json
import time
from datetime import datetime

# API Configuration
API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"

def test_api_endpoint(message, test_name):
    """Test a single API endpoint"""
    print(f"\n🧪 Testing: {test_name}")
    print(f"📝 Message: '{message}'")
    print("=" * 60)
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "message": message,
        "user_id": "test_user_pizza",
        "session_id": f"test_session_{int(time.time())}"
    }
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=60)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS - Valid JSON response")
            
            # Check response structure
            required_fields = ["text_bubble", "ui_cards", "search_metadata"]
            for field in required_fields:
                if field in data:
                    print(f"✅ {field}: Present")
                else:
                    print(f"❌ {field}: Missing")
            
            # Analyze results
            if "ui_cards" in data and data["ui_cards"]:
                print(f"🍕 Food items found: {len(data['ui_cards'])}")
                for i, item in enumerate(data["ui_cards"][:3]):  # Show first 3
                    dish_name = item.get("dish_name", "Unknown")
                    category = item.get("category", "Unknown")
                    cuisine = item.get("cuisine_type", "Unknown")
                    price = item.get("student_price", "Unknown")
                    print(f"   {i+1}. {dish_name} - {category} ({cuisine}) - £{price}")
            else:
                print("❌ No food items in ui_cards")
            
            if "search_metadata" in data:
                metadata = data["search_metadata"]
                print(f"🔍 Filters applied: {metadata.get('filters_applied', [])}")
                print(f"📊 Total results: {metadata.get('total_results', 0)}")
            
            print(f"💬 Response text: {data.get('text_bubble', 'No text_bubble')[:100]}...")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Request took too long (>60s)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError:
        print("❌ Invalid JSON response")
        print(f"Raw response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def main():
    """Run all pizza-related tests"""
    print("🍕 PIZZA API TESTING SUITE")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API URL: {API_URL}")
    
    # Test cases
    test_cases = [
        ("Show me pizza options", "Basic Pizza Search"),
        ("I want pizza", "Casual Pizza Request"),
        ("What pizza do you have?", "Question Format Pizza"),
        ("Pizza please", "Simple Pizza Request"),
        ("Show me Italian food", "Italian Cuisine Test"),
        ("What restaurants serve pizza?", "Pizza Restaurant Query"),
    ]
    
    for message, test_name in test_cases:
        test_api_endpoint(message, test_name)
        time.sleep(2)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print("🎯 TESTING COMPLETE")
    print("Expected Results:")
    print("✅ Pizza searches should return 5 items with cuisine_type: International")
    print("✅ No more 'Italian' cuisine confusion")
    print("✅ Agent should use correct filters: category: Pizza, cuisine_type: International")

if __name__ == "__main__":
    main()
