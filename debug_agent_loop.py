#!/usr/bin/env python3
"""
Debug script to examine what's causing the agent loop
"""
import requests
import json
import time

def debug_agent_loop():
    API_URL = "https://unifeast-chatbot-production.up.railway.app/chat"
    
    print("🔍 DEBUGGING AGENT LOOP")
    print("=" * 50)
    
    payload = {
        "message": "pizza",
        "user_id": "debug_user",
        "session_id": "debug_session"
    }
    
    print("📝 Sending simple pizza query...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, 
                               data=json.dumps(payload), timeout=90)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            text_bubble = data.get('text_bubble', '')
            search_metadata = data.get('search_metadata', {})
            
            print(f"💬 Full response text: {text_bubble}")
            print(f"🔍 Filters applied: {search_metadata.get('filters_applied', [])}")
            print(f"📊 Total results: {search_metadata.get('total_results', 0)}")
            
            # Analyze the response for clues about what went wrong
            print("\n🔍 LOOP ANALYSIS:")
            
            if "iteration limit" in text_bubble.lower():
                print("❌ Agent hit iteration limit")
                print("   This means the agent called tools repeatedly without stopping")
                
            if "time limit" in text_bubble.lower():
                print("❌ Agent hit time limit")
                print("   This means the agent took too long to complete")
                
            if len(search_metadata.get('filters_applied', [])) == 0:
                print("❌ No filters were applied")
                print("   This suggests the agent never successfully called search_pinecone")
                
            if search_metadata.get('total_results', 0) == 0:
                print("❌ Zero results returned")
                print("   This suggests either no search was performed or search failed")
                
            # Check if the agent mentioned any tools
            if any(keyword in text_bubble.lower() for keyword in ['search', 'pinecone', 'tool', 'function']):
                print("✅ Agent mentioned tools/functions")
            else:
                print("❌ Agent did NOT mention tools/functions")
                print("   This suggests the agent may not have attempted to use tools")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_agent_loop()
