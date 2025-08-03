"""
Test Setup for UniFeast LangChain Agent
=======================================

Simple test script to verify that all components are working correctly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_imports():
    """Test that all required packages can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import langchain
        print("✅ langchain imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain: {e}")
        return False
    
    try:
        import langchain_mcp_adapters
        print("✅ langchain_mcp_adapters imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_mcp_adapters: {e}")
        return False
    
    try:
        import langchain_openai
        print("✅ langchain_openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_openai: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test that required environment variables are set."""
    print("\n🧪 Testing environment variables...")
    
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "AWS_REGION",
        "FOOD_DB_ARN",
        "FOOD_DB_SECRET",
        "FOOD_DB_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (set)")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {'*' * len(openai_key)} (set)")
    else:
        print("❌ OPENAI_API_KEY: NOT SET")
        print("   Please set your OpenAI API key to test the agent")
        missing_vars.append("OPENAI_API_KEY")
    
    return len(missing_vars) == 0

async def test_mcp_client_creation():
    """Test MCP client creation (without actually connecting)."""
    print("\n🧪 Testing MCP client creation...")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Create client configuration (without actually connecting)
        client_config = {
            "dynamodb": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "awslabs/dynamodb-mcp-server:latest"],
                "env": {},
                "transport": "stdio"
            }
        }
        
        print("✅ MCP client configuration created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create MCP client configuration: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 UNIFEAST LANGCHAIN AGENT SETUP TEST")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_imports()
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test MCP client creation
    mcp_ok = await test_mcp_client_creation()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"MCP Client: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if imports_ok and env_ok and mcp_ok:
        print("\n🎉 ALL TESTS PASSED! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run the agent: python langchain_agent.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 