#!/usr/bin/env python3
"""
Test what happens when we try to trigger specific tools
"""
import requests
import json

def test_tool_triggers():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔧 TESTING TOOL TRIGGERS")
    print("=" * 50)
    
    # Test queries that should trigger specific tools
    test_cases = [
        ("What are my dietary preferences?", "Should trigger get_item"),
        ("Show me my profile", "Should trigger get_item"),
        ("pizza", "Should trigger search_pinecone"),
        ("coffee", "Should trigger search_pinecone"),
        ("What cuisines are available?", "Should trigger knowledge base or direct response"),
    ]
    
    for message, expected_tool in test_cases:
        print(f"\n📝 Testing: '{message}'")
        print(f"   Expected: {expected_tool}")
        
        payload = {
            "message": message,
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                                   data=json.dumps(payload), timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                text_bubble = data.get('text_bubble', '')
                search_metadata = data.get('search_metadata', {})
                
                print(f"   ✅ Status: 200 OK")
                print(f"   💬 Response: {text_bubble[:150]}...")
                
                if "iteration limit" in text_bubble.lower():
                    print(f"   ❌ HITTING ITERATION LIMIT - Tool calling failed")
                elif "time limit" in text_bubble.lower():
                    print(f"   ❌ HITTING TIME LIMIT - Tool execution failed")
                elif search_metadata.get('total_results', 0) > 0:
                    print(f"   ✅ SUCCESS - Tool worked, got {search_metadata.get('total_results', 0)} results")
                elif "dietary" in text_bubble.lower() or "preferences" in text_bubble.lower():
                    print(f"   ✅ SUCCESS - get_item tool worked")
                elif "cuisine" in text_bubble.lower() or "available" in text_bubble.lower():
                    print(f"   ✅ SUCCESS - Knowledge base or direct response worked")
                else:
                    print(f"   ❓ UNCLEAR - No clear indication of tool usage")
                    
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_tool_triggers()
