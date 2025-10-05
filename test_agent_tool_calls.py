#!/usr/bin/env python3
"""
Test to see if the agent is actually calling knowledge base tools
"""
import requests
import json

def test_agent_tool_usage():
    """Test what tools the agent is actually calling"""
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔍 TESTING AGENT TOOL USAGE")
    print("=" * 50)
    
    # Test 1: Pizza query - should call knowledge base first
    print("\n1️⃣ Testing pizza query tool calls:")
    payload = {
        "message": "Show me pizza options",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check search metadata for clues about tool usage
            search_metadata = data.get('search_metadata', {})
            filters_applied = search_metadata.get('filters_applied', [])
            
            print(f"✅ Response received")
            print(f"🔍 Filters applied: {filters_applied}")
            print(f"📊 Total results: {search_metadata.get('total_results', 0)}")
            
            # Analyze the response text for clues
            text_bubble = data.get('text_bubble', '')
            print(f"💬 Response text: {text_bubble}")
            
            # Check if it mentions knowledge base usage
            if "knowledge" in text_bubble.lower() or "database" in text_bubble.lower():
                print("✅ Response mentions knowledge/database")
            else:
                print("❌ Response does NOT mention knowledge/database")
                
            # Check if it mentions International cuisine
            if "International" in text_bubble:
                print("✅ Response mentions International cuisine")
            else:
                print("❌ Response does NOT mention International cuisine")
                
            # Check if it mentions Italian cuisine
            if "Italian" in text_bubble:
                print("❌ Response mentions Italian cuisine (wrong)")
            else:
                print("✅ Response does NOT mention Italian cuisine (correct)")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Knowledge base query - should definitely call knowledge base
    print("\n2️⃣ Testing knowledge base query:")
    payload = {
        "message": "What cuisines are available?",
        "user_id": "debug_user", 
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            text_bubble = data.get('text_bubble', '')
            
            print(f"✅ Knowledge base query successful")
            print(f"💬 Response: {text_bubble}")
            
            # Check if it mentions International
            if "International" in text_bubble:
                print("✅ Knowledge base response mentions International")
            else:
                print("❌ Knowledge base response does NOT mention International")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS:")
    print("If agent calls knowledge base tools:")
    print("  - Pizza query should mention International cuisine")
    print("  - Should apply correct filters: category: Pizza, cuisine_type: International")
    print("  - Should return 5 pizza results")
    print("\nIf agent does NOT call knowledge base tools:")
    print("  - Pizza query will use wrong filters: cuisine_type: Italian")
    print("  - Will return 0 results")
    print("  - Response won't mention knowledge base")

if __name__ == "__main__":
    test_agent_tool_usage()
