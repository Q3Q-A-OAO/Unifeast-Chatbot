#!/usr/bin/env python3
"""
Test the knowledge base directly without LangChain tools
"""
import sys
import os

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from langchain_agent.knowledge_base.simple_knowledge_base import SimpleKnowledgeBase

def test_knowledge_base():
    """Test the knowledge base directly"""
    print("🧪 TESTING LOCAL KNOWLEDGE BASE DIRECTLY")
    print("=" * 50)
    
    # Create knowledge base instance
    kb = SimpleKnowledgeBase()
    
    print(f"📁 Knowledge file: {kb.knowledge_file}")
    print(f"📊 Knowledge sections: {list(kb.knowledge_data.keys())}")
    
    # Test 1: Check pizza in categories
    print("\n1️⃣ Checking Pizza in categories:")
    categories = kb.knowledge_data.get("categories", {})
    pizza_info = categories.get("Pizza", {})
    if pizza_info:
        print(f"Pizza category found: {pizza_info}")
        cuisine = pizza_info.get("cuisine", "Unknown")
        if cuisine == "International":
            print("✅ Pizza cuisine is International (CORRECT)")
        else:
            print(f"❌ Pizza cuisine is {cuisine} (WRONG - should be International)")
    else:
        print("❌ Pizza category not found")
    
    # Test 2: Check International cuisine
    print("\n2️⃣ Checking International cuisine:")
    cuisine_types = kb.knowledge_data.get("cuisine_types", {})
    international_info = cuisine_types.get("International", {})
    if international_info:
        print(f"International cuisine found: {international_info}")
        categories = international_info.get("categories", [])
        if "Pizza" in categories:
            print("✅ Pizza is in International categories (CORRECT)")
        else:
            print("❌ Pizza is NOT in International categories")
        
        restaurants = international_info.get("restaurants", [])
        if "Pizza Pi" in restaurants:
            print("✅ Pizza Pi is in International restaurants (CORRECT)")
        else:
            print("❌ Pizza Pi is NOT in International restaurants")
    else:
        print("❌ International cuisine not found")
    
    # Test 3: Check Italian cuisine
    print("\n3️⃣ Checking Italian cuisine:")
    italian_info = cuisine_types.get("Italian", {})
    if italian_info:
        print(f"Italian cuisine found: {italian_info}")
        categories = italian_info.get("categories", [])
        if "Pizza" in categories:
            print("❌ Pizza is still in Italian categories (WRONG)")
        else:
            print("✅ Pizza is NOT in Italian categories (CORRECT)")
    else:
        print("❌ Italian cuisine not found")
    
    # Test 4: Check Pizza Pi restaurant
    print("\n4️⃣ Checking Pizza Pi restaurant:")
    restaurants = kb.knowledge_data.get("restaurants", {})
    pizza_pi_info = restaurants.get("Pizza Pi", {})
    if pizza_pi_info:
        print(f"Pizza Pi restaurant found: {pizza_pi_info}")
        cuisine_type = pizza_pi_info.get("cuisine_type", "Unknown")
        if cuisine_type == "International":
            print("✅ Pizza Pi cuisine_type is International (CORRECT)")
        else:
            print(f"❌ Pizza Pi cuisine_type is {cuisine_type} (WRONG)")
        
        specialties = pizza_pi_info.get("specialties", [])
        if "Italian" in specialties:
            print("❌ Pizza Pi still has 'Italian' in specialties (WRONG)")
        else:
            print("✅ Pizza Pi does NOT have 'Italian' in specialties (CORRECT)")
    else:
        print("❌ Pizza Pi restaurant not found")
    
    # Test 5: Check search insights
    print("\n5️⃣ Checking pizza search insights:")
    search_insights = kb.knowledge_data.get("search_insights", {})
    pizza_info = search_insights.get("pizza_info", {})
    if pizza_info:
        print(f"Pizza search insight found: {pizza_info}")
        cuisine = pizza_info.get("cuisine", "Unknown")
        if cuisine == "International":
            print("✅ Pizza search insight cuisine is International (CORRECT)")
        else:
            print(f"❌ Pizza search insight cuisine is {cuisine} (WRONG)")
    else:
        print("❌ Pizza search insight not found")

if __name__ == "__main__":
    test_knowledge_base()
