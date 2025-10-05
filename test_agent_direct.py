#!/usr/bin/env python3
"""
Direct Agent Test
=================

This script tests the agent directly by calling the search_pinecone tool
and simulating what the agent should do for a pizza search.
"""

import asyncio
import sys
import os
import json

# Add langchain_agent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from agent.pinecone_search import search_pinecone

def test_agent_pizza_search():
    """Test what the agent should do for a pizza search."""
    
    print("🍕 Testing Agent Pizza Search Logic")
    print("=" * 50)
    
    # Step 1: Simulate knowledge base query (what the agent should do first)
    print("\n📚 Step 1: Knowledge Base Query")
    print("   Agent should call: query_database_knowledge('pizza')")
    print("   Expected result: Find that 'Pizza' is a valid category")
    print("   ✅ Knowledge base would return: Pizza is available in categories")
    
    # Step 2: Simulate search_pinecone call (what the agent should do second)
    print("\n🔍 Step 2: Pinecone Search")
    print("   Agent should call: search_pinecone with pizza filters")
    
    # Test different filter combinations the agent might use
    test_cases = [
        {
            "name": "Simple category filter",
            "query": "pizza",
            "filter": {"category": "Pizza"}
        },
        {
            "name": "Category with $eq",
            "query": "pizza", 
            "filter": {"category": {"$eq": "Pizza"}}
        },
        {
            "name": "Category + cuisine_type",
            "query": "pizza",
            "filter": {"category": {"$eq": "Pizza"}, "cuisine_type": {"$eq": "International"}}
        },
        {
            "name": "No filter (semantic search only)",
            "query": "pizza",
            "filter": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   🧪 Test {i}: {test_case['name']}")
        try:
            result = search_pinecone.invoke({
                "query_text": test_case["query"],
                "filter_dict": test_case["filter"]
            })
            
            total_results = result.get('total_results', 0)
            print(f"      Query: {test_case['query']}")
            print(f"      Filter: {test_case['filter']}")
            print(f"      Results: {total_results} items")
            
            if total_results > 0:
                print("      ✅ SUCCESS - Found pizza items!")
                for j, item in enumerate(result['food_items'][:3]):
                    dish_name = item.get('metadata', {}).get('dish_name', 'Unknown')
                    category = item.get('metadata', {}).get('category', 'Unknown')
                    print(f"         {j+1}. {dish_name} - {category}")
            else:
                print("      ❌ FAILED - No pizza items found")
                
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
    
    # Step 3: What the agent should return
    print(f"\n📤 Step 3: Agent Response Format")
    print("   Agent should return JSON with:")
    print("   - text_bubble: Conversational response")
    print("   - ui_cards: Array of food items found")
    print("   - search_metadata: Query info")
    
    # Step 4: Expected final result
    print(f"\n🎯 Expected Final Result:")
    print("   If agent works correctly:")
    print("   1. Calls knowledge base → finds Pizza category")
    print("   2. Calls search_pinecone with category filter")
    print("   3. Gets 5 pizza items back")
    print("   4. Returns JSON with pizza items in ui_cards")
    print("   5. User sees: Pepperoni Pizza, Chicken BBQ Pizza, etc.")

if __name__ == "__main__":
    test_agent_pizza_search()
