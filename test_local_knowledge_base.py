#!/usr/bin/env python3
"""
Test the knowledge base locally to verify our fixes are working
"""
import asyncio
import sys
import os

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from langchain_agent.knowledge_base.simple_knowledge_base import query_database_knowledge

async def test_knowledge_base():
    """Test the knowledge base directly"""
    print("🧪 TESTING LOCAL KNOWLEDGE BASE")
    print("=" * 50)
    
    # Test 1: Query for pizza
    print("\n1️⃣ Testing pizza query:")
    try:
        result = await query_database_knowledge.invoke({"query_text": "pizza"})
        print(f"Result: {result}")
        
        # Check if it mentions International cuisine
        if "International" in result:
            print("✅ International cuisine mentioned for pizza")
        else:
            print("❌ International cuisine NOT mentioned")
            
        # Check if it mentions Italian cuisine
        if "Italian" in result:
            print("❌ Italian cuisine still mentioned (should be removed)")
        else:
            print("✅ Italian cuisine removed from pizza")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Query for cuisines
    print("\n2️⃣ Testing cuisines query:")
    try:
        result = await query_database_knowledge.invoke({"query_text": "cuisines"})
        print(f"Result: {result}")
        
        # Check if International is mentioned
        if "International" in result:
            print("✅ International cuisine mentioned")
        else:
            print("❌ International cuisine NOT mentioned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Query for restaurants
    print("\n3️⃣ Testing restaurants query:")
    try:
        result = await query_database_knowledge.invoke({"query_text": "restaurants"})
        print(f"Result: {result}")
        
        # Check if Pizza Pi is mentioned
        if "Pizza Pi" in result:
            print("✅ Pizza Pi restaurant mentioned")
        else:
            print("❌ Pizza Pi restaurant NOT mentioned")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_knowledge_base())
