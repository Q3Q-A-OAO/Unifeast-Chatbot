#!/usr/bin/env python3
"""
Test if knowledge base tools are available to the agent
"""
import requests
import json

def test_tool_availability():
    """Test if tools are available by trying different queries"""
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔧 TESTING TOOL AVAILABILITY")
    print("=" * 50)
    
    # Test different types of queries to see what tools are available
    test_cases = [
        ("What cuisines do you have?", "Should call get_available_cuisines"),
        ("What restaurants are available?", "Should call get_available_restaurants"), 
        ("What categories are available?", "Should call get_available_categories"),
        ("Show me pizza options", "Should call query_database_knowledge + search_pinecone"),
        ("What dietary options are available?", "Should call get_dietary_options"),
    ]
    
    for message, expected_tool in test_cases:
        print(f"\n🧪 Testing: '{message}'")
        print(f"   Expected: {expected_tool}")
        
        payload = {
            "message": message,
            "user_id": "debug_user",
            "session_id": "debug_session"
        }
        
        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                                   data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                text_bubble = data.get('text_bubble', '')
                search_metadata = data.get('search_metadata', {})
                filters_applied = search_metadata.get('filters_applied', [])
                
                print(f"   ✅ Status: 200 OK")
                print(f"   🔍 Filters: {filters_applied}")
                print(f"   📊 Results: {search_metadata.get('total_results', 0)}")
                print(f"   💬 Response: {text_bubble[:100]}...")
                
                # Check if it looks like a knowledge base response
                if any(keyword in text_bubble.lower() for keyword in ['cuisine', 'restaurant', 'category', 'available']):
                    print(f"   ✅ Looks like knowledge base response")
                else:
                    print(f"   ❌ Does NOT look like knowledge base response")
                    
            elif response.status_code == 500:
                print(f"   ❌ Status: 500 Error")
                error_text = response.text
                if "validation errors" in error_text:
                    print(f"   ❌ Validation error - tool returning wrong format")
                else:
                    print(f"   ❌ Server error: {error_text[:100]}...")
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("If knowledge base tools are available:")
    print("  - Queries should return structured information")
    print("  - Should mention specific cuisines, restaurants, categories")
    print("  - Should NOT return 500 validation errors")
    print("\nIf knowledge base tools are NOT available:")
    print("  - Agent will use hardcoded information")
    print("  - Pizza queries will use wrong filters")
    print("  - Knowledge base queries may return 500 errors")

if __name__ == "__main__":
    test_tool_availability()
