#!/usr/bin/env python3
"""
API Pizza Test
==============

This script tests the deployed API to see what the agent actually returns
for pizza queries.
"""

import requests
import json
import time

def test_api_pizza_search():
    """Test pizza search through the deployed API."""
    
    print("🍕 Testing API Pizza Search")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "Show me pizza options",
        "I want pizza",
        "Find me pizza",
        "pizza"
    ]
    
    # You'll need to replace this with your actual Railway API URL
    api_url = "https://your-railway-app.railway.app/chat"  # Replace with actual URL
    
    print(f"🌐 Testing API at: {api_url}")
    print("⚠️  NOTE: You need to replace the URL with your actual Railway deployment URL")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: '{query}'")
        
        payload = {
            "message": query,
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        try:
            print(f"   📤 Sending request...")
            response = requests.post(api_url, json=payload, timeout=30)
            
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS!")
                
                # Check response structure
                ui_cards = result.get('ui_cards', [])
                text_bubble = result.get('text_bubble', '')
                total_results = result.get('search_metadata', {}).get('total_results', 0)
                
                print(f"   📋 Response Analysis:")
                print(f"      - UI Cards: {len(ui_cards)} items")
                print(f"      - Text Bubble: {text_bubble[:100]}...")
                print(f"      - Total Results: {total_results}")
                
                if ui_cards:
                    print(f"   🍕 Pizza Items Found:")
                    for j, card in enumerate(ui_cards[:3]):
                        dish_name = card.get('dish_name', 'Unknown')
                        category = card.get('category', 'Unknown')
                        print(f"      {j+1}. {dish_name} - {category}")
                else:
                    print(f"   ❌ No pizza items in ui_cards")
                    
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Request took too long")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 CONNECTION ERROR - Can't reach API")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        time.sleep(1)  # Wait between requests

def test_local_api():
    """Test local API if running."""
    
    print(f"\n🏠 Testing Local API")
    print("=" * 30)
    
    local_url = "http://localhost:8000/chat"
    
    payload = {
        "message": "Show me pizza options",
        "user_id": "test_user", 
        "session_id": "test_session"
    }
    
    try:
        print(f"📤 Testing local API at {local_url}")
        response = requests.post(local_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Local API working!")
            
            ui_cards = result.get('ui_cards', [])
            print(f"🍕 Found {len(ui_cards)} pizza items locally")
            
        else:
            print(f"❌ Local API failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Local API not running")
    except Exception as e:
        print(f"❌ Local API error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("📝 Instructions:")
    print("1. Replace 'your-railway-app.railway.app' with your actual Railway URL")
    print("2. Make sure your Railway deployment is running")
    print("3. Run this script to see what the agent actually returns")
    print()
    
    # Test local first
    test_local_api()
    
    # Then test deployed API (you'll need to update the URL)
    test_api_pizza_search()
