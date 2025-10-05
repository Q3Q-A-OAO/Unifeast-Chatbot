#!/usr/bin/env python3
"""
Test the local agent to see if it uses the knowledge base correctly
"""
import asyncio
import sys
import os

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from langchain_agent.agent.mcp_tester import MCPToolsTester

async def test_local_agent():
    """Test the local agent with pizza query"""
    print("🤖 TESTING LOCAL AGENT")
    print("=" * 50)
    
    try:
        # Initialize the agent
        tester = MCPToolsTester()
        await tester.initialize()
        
        print("✅ Agent initialized successfully")
        
        # Test pizza query
        print("\n🍕 Testing pizza query:")
        response = await tester.get_chat_response(
            message="Show me pizza options",
            user_id="test_user",
            session_id="test_session"
        )
        
        print(f"Response: {response}")
        
        # Check if it mentions International cuisine
        if "International" in response:
            print("✅ Response mentions International cuisine")
        else:
            print("❌ Response does NOT mention International cuisine")
            
        # Check if it mentions Italian cuisine
        if "Italian" in response:
            print("❌ Response still mentions Italian cuisine")
        else:
            print("✅ Response does NOT mention Italian cuisine")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_local_agent())
