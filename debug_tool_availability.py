#!/usr/bin/env python3
"""
Debug what tools are available to the agent
"""
import requests
import json

def debug_tool_availability():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔧 DEBUGGING TOOL AVAILABILITY")
    print("=" * 50)
    
    # Test with a query that should definitely use tools
    payload = {
        "message": "What tools do you have available?",
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
            
            # Check if it mentions specific tools
            tools_mentioned = []
            if 'search_pinecone' in text_bubble.lower():
                tools_mentioned.append('search_pinecone')
            if 'get_item' in text_bubble.lower():
                tools_mentioned.append('get_item')
            if 'knowledge' in text_bubble.lower():
                tools_mentioned.append('knowledge_base_tools')
                
            if tools_mentioned:
                print(f"✅ Tools mentioned: {tools_mentioned}")
            else:
                print("❌ No specific tools mentioned")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with a query that should use get_item
    print("\n🔍 Testing get_item tool availability:")
    payload = {
        "message": "What are my dietary preferences?",
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
            
            if "dietary" in text_bubble.lower() or "preferences" in text_bubble.lower():
                print("✅ get_item tool appears to work")
            else:
                print("❌ get_item tool may not be working")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_tool_availability()
