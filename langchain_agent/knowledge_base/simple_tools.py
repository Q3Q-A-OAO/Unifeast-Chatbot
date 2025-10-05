"""
Simple Knowledge Base Tools
==========================

Standalone tool functions for knowledge base queries.
Avoids class methods and 'self' parameter issues.
"""

import os
import json
from typing import List, Optional, Dict, Any
from langchain.tools import tool

# Global knowledge data
_knowledge_data = {}

def _load_knowledge_data():
    """Load knowledge data from JSON file."""
    global _knowledge_data
    try:
        knowledge_file = os.path.join(os.path.dirname(__file__), "database_knowledge.json")
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r') as f:
                _knowledge_data = json.load(f)
            print(f"✅ Loaded knowledge base with {len(_knowledge_data)} sections")
        else:
            print(f"❌ Knowledge file not found: {knowledge_file}")
            _knowledge_data = {}
    except Exception as e:
        print(f"❌ Error loading knowledge data: {e}")
        _knowledge_data = {}

# Load data on import
_load_knowledge_data()

@tool
def query_database_knowledge(query: str) -> str:
    """Query the database knowledge base for information about food, restaurants, cuisines, etc."""
    try:
        print(f"🔍 Querying knowledge base: {query}")
        
        # Simple keyword matching
        query_lower = query.lower()
        results = []
        
        # Search in cuisine types
        cuisine_types = _knowledge_data.get("cuisine_types", {})
        for cuisine, data in cuisine_types.items():
            if any(keyword in query_lower for keyword in [cuisine.lower(), "cuisine", "food"]):
                results.append(f"Available {cuisine} cuisine: {data.get('count', 0)} restaurants")
        
        # Search in categories
        categories = _knowledge_data.get("categories", {})
        for category, data in categories.items():
            if any(keyword in query_lower for keyword in [category.lower(), "category", "type"]):
                results.append(f"Available {category} category: {data.get('count', 0)} items")
        
        # Search in restaurants
        restaurants = _knowledge_data.get("restaurants", {})
        for restaurant, data in restaurants.items():
            if any(keyword in query_lower for keyword in [restaurant.lower(), "restaurant", "place"]):
                results.append(f"Restaurant: {restaurant} - {data.get('cuisine_type', 'Unknown cuisine')}")
        
        if not results:
            return f"No specific information found for '{query}'. Available: {len(cuisine_types)} cuisines, {len(categories)} categories, {len(restaurants)} restaurants."
        
        return "\n".join(results[:3])  # Limit to 3 results
        
    except Exception as e:
        print(f"❌ Error querying knowledge base: {e}")
        return f"Error querying knowledge base: {str(e)}"

@tool
def get_available_cuisines() -> str:
    """Get all available cuisine types."""
    try:
        cuisine_types = _knowledge_data.get("cuisine_types", {})
        if not cuisine_types:
            return "No cuisine types available."
        
        result = "Available cuisines:\n"
        for cuisine, data in cuisine_types.items():
            count = data.get('count', 0)
            result += f"- {cuisine}: {count} restaurants\n"
        
        return result
        
    except Exception as e:
        return f"Error getting cuisines: {str(e)}"

@tool
def get_available_categories() -> str:
    """Get all available food categories."""
    try:
        categories = _knowledge_data.get("categories", {})
        if not categories:
            return "No categories available."
        
        result = "Available categories:\n"
        for category, data in categories.items():
            count = data.get('count', 0)
            result += f"- {category}: {count} items\n"
        
        return result
        
    except Exception as e:
        return f"Error getting categories: {str(e)}"

@tool
def get_available_restaurants() -> str:
    """Get all available restaurants."""
    try:
        print("🔍 Getting available restaurants...")
        restaurants = _knowledge_data.get("restaurants", {})
        print(f"✅ Found {len(restaurants)} restaurants in knowledge base")
        
        if not restaurants:
            return "No restaurants available."
        
        result = "Available restaurants:\n"
        for restaurant, data in restaurants.items():
            cuisine = data.get('cuisine_type', 'Unknown')
            result += f"- {restaurant}: {cuisine} cuisine\n"
        
        return result
        
    except Exception as e:
        print(f"❌ Error getting restaurants: {e}")
        return f"Error getting restaurants: {str(e)}"

@tool
def get_dietary_options() -> str:
    """Get all available dietary options and tags."""
    try:
        dietary_options = _knowledge_data.get("dietary_options", {})
        if not dietary_options:
            return "No dietary options available."
        
        result = "Available dietary options:\n"
        for option, data in dietary_options.items():
            result += f"- {option}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting dietary options: {str(e)}"
