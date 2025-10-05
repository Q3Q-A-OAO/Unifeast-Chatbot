#!/usr/bin/env python3
"""
Debug why the agent cannot call any tools
"""
import requests
import json

def debug_tool_setup():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔧 DEBUGGING TOOL SETUP")
    print("=" * 50)
    
    # Test if the agent can even see that it has tools
    payload = {
        "message": "What functions or tools do you have available? List all of them.",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            text_bubble = data.get('text_bubble', '')
            
            print(f"💬 Response: {text_bubble}")
            
            # Check if it mentions any tools
            if any(keyword in text_bubble.lower() for keyword in ['function', 'tool', 'search_pinecone', 'get_item']):
                print("✅ Agent mentions tools/functions")
            else:
                print("❌ Agent does NOT mention any tools/functions")
                print("   This suggests tools are not properly loaded or accessible")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with a very explicit tool request
    print("\n🔍 Testing explicit tool request:")
    payload = {
        "message": "Please call the search_pinecone function with query 'pizza' and no filters",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            text_bubble = data.get('text_bubble', '')
            
            print(f"💬 Response: {text_bubble}")
            
            if "iteration limit" in text_bubble.lower():
                print("❌ Still hitting iteration limit even with explicit tool request")
            elif "search_pinecone" in text_bubble.lower():
                print("✅ Agent attempted to use search_pinecone")
            else:
                print("❓ Unclear response")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_tool_setup()
