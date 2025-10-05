#!/usr/bin/env python3
"""
Test with minimal queries to isolate the agent loop issue
"""
import requests
import json

def test_minimal_agent():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🧪 TESTING MINIMAL AGENT BEHAVIOR")
    print("=" * 50)
    
    # Test with the simplest possible queries
    test_cases = [
        ("Hi", "Minimal greeting"),
        ("Hello", "Basic greeting"),
        ("Help", "Help request"),
        ("Test", "Single word"),
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
                
                print(f"   ✅ Status: 200 OK")
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
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("If ALL queries hit iteration limits:")
    print("  - Problem is in agent configuration or system prompt")
    print("  - Agent can't use any tools at all")
    print("  - Need to check agent setup or reduce system prompt complexity")
    print("\nIf only SOME queries hit limits:")
    print("  - Problem is specific to certain tool combinations")
    print("  - Need to debug specific tool interactions")

if __name__ == "__main__":
    test_minimal_agent()
