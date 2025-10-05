#!/usr/bin/env python3
"""
Simple Agent Test
=================

This script tests the agent by directly calling the search_pinecone tool
and simulating the agent's workflow for pizza search.
"""

import sys
import os
import json

# Add langchain_agent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from agent.pinecone_search import search_pinecone

def simulate_agent_workflow():
    """Simulate what the agent should do for pizza search."""
    
    print("🤖 Simulating Agent Pizza Search Workflow")
    print("=" * 50)
    
    # Step 1: Knowledge Base Query (simulated)
    print("\n📚 Step 1: Knowledge Base Query")
    print("   Agent calls: query_database_knowledge('pizza')")
    print("   Knowledge base returns: 'Pizza' is a valid category")
    print("   ✅ Agent learns: Use category filter 'Pizza'")
    
    # Step 2: Search Pinecone (actual call)
    print("\n🔍 Step 2: Pinecone Search")
    print("   Agent calls: search_pinecone('pizza', {'category': 'Pizza'})")
    
    try:
        result = search_pinecone.invoke({
            "query_text": "pizza",
            "filter_dict": {"category": "Pizza"}
        })
        
        total_results = result.get('total_results', 0)
        food_items = result.get('food_items', [])
        
        print(f"   📊 Search Results: {total_results} items found")
        
        if total_results > 0:
            print("   ✅ SUCCESS - Agent found pizza items!")
            print("   🍕 Pizza Items:")
            for i, item in enumerate(food_items):
                metadata = item.get('metadata', {})
                dish_name = metadata.get('dish_name', 'Unknown')
                category = metadata.get('category', 'Unknown')
                score = item.get('score', 0)
                print(f"      {i+1}. {dish_name} - {category} (score: {score:.3f})")
        else:
            print("   ❌ FAILED - No pizza items found")
            return
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return
    
    # Step 3: Agent Response Construction (simulated)
    print(f"\n📤 Step 3: Agent Response Construction")
    print("   Agent constructs JSON response:")
    
    # Simulate the agent's response
    agent_response = {
        "text_bubble": f"I found {total_results} pizza options for you! Here are some great choices:",
        "ui_cards": [],
        "restaurant_cards": None,
        "user_id": "test_user",
        "session_id": "test_session",
        "timestamp": "2025-01-05T18:30:00.000000",
        "search_metadata": {
            "total_results": total_results,
            "search_query": "pizza",
            "filters_applied": ["category: Pizza"],
            "user_identity": "student",
            "budget_limit": 0.0
        }
    }
    
    # Convert food items to ui_cards format
    for item in food_items:
        metadata = item.get('metadata', {})
        ui_card = {
            "food_id": item.get('id', ''),
            "dish_name": metadata.get('dish_name', 'Unknown'),
            "description": metadata.get('description', ''),
            "category": metadata.get('category', ''),
            "cuisine_type": metadata.get('cuisine_type', ''),
            "student_price": metadata.get('student_price', 0),
            "staff_price": metadata.get('staff_price', 0),
            "location": metadata.get('location', ''),
            "restaurant_name": metadata.get('restaurant_name', ''),
            "dietary_tags": metadata.get('dietary_tags', []),
            "available": metadata.get('available', True)
        }
        agent_response["ui_cards"].append(ui_card)
    
    print(f"   📋 Response Structure:")
    print(f"      - text_bubble: '{agent_response['text_bubble']}'")
    print(f"      - ui_cards: {len(agent_response['ui_cards'])} items")
    print(f"      - search_metadata: {agent_response['search_metadata']}")
    
    # Step 4: Final Result
    print(f"\n🎯 Final Result:")
    print("   If agent works correctly, user should see:")
    print(f"   💬 '{agent_response['text_bubble']}'")
    print("   🍕 Pizza options:")
    for i, card in enumerate(agent_response['ui_cards'][:3]):
        print(f"      {i+1}. {card['dish_name']} - {card['category']} - £{card['student_price']}")
    
    print(f"\n✅ Agent workflow simulation complete!")
    print(f"📊 Summary: Found {total_results} pizza items successfully")

if __name__ == "__main__":
    simulate_agent_workflow()
