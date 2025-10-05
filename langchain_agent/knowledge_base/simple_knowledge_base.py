"""
Simple Knowledge Base Implementation
===================================

A lightweight knowledge base that avoids complex vector stores and ChromaDB
to prevent agent loops. Uses simple string matching and JSON data.

This approach:
- Loads knowledge from JSON file
- Uses simple string matching for queries
- Avoids vector embeddings and ChromaDB
- Provides reliable, fast responses
"""

import os
import json
from typing import List, Optional, Dict, Any
from langchain.tools import tool

class SimpleKnowledgeBase:
    """
    Simple knowledge base that loads data from JSON and uses string matching.
    Avoids complex vector stores that can cause agent loops.
    """
    
    def __init__(self):
        self.knowledge_file = os.path.join(os.path.dirname(__file__), "database_knowledge.json")
        self.knowledge_data = {}
        self._load_knowledge_data()
    
    def _load_knowledge_data(self):
        """Load knowledge data from JSON file."""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r') as f:
                    self.knowledge_data = json.load(f)
                print(f"✅ Loaded knowledge base with {len(self.knowledge_data)} sections")
            else:
                print(f"❌ Knowledge file not found: {self.knowledge_file}")
                self.knowledge_data = {}
        except Exception as e:
            print(f"❌ Error loading knowledge data: {e}")
            self.knowledge_data = {}
    
    def _search_knowledge(self, query: str) -> str:
        """
        Search knowledge base using simple string matching.
        Returns relevant information based on query keywords.
        """
        query_lower = query.lower()
        results = []
        
        # Search cuisine types
        cuisine_types = self.knowledge_data.get("cuisine_types", {})
        for cuisine, info in cuisine_types.items():
            if any(keyword in query_lower for keyword in [cuisine.lower(), "cuisine", "food"]):
                categories = info.get("categories", [])
                restaurants = info.get("restaurants", [])
                count = info.get("count", 0)
                
                result = f"**{cuisine} Cuisine:**\n"
                result += f"- Available categories: {', '.join(categories[:5])}\n"
                result += f"- Restaurants: {', '.join(restaurants[:3])}\n"
                result += f"- Total items: {count}\n"
                results.append(result)
        
        # Search categories
        categories = self.knowledge_data.get("categories", {})
        for category, info in categories.items():
            if any(keyword in query_lower for keyword in [category.lower(), "category", "type"]):
                food_types = info.get("food_types", [])
                restaurants = info.get("restaurants", [])
                count = info.get("count", 0)
                
                result = f"**{category} Category:**\n"
                result += f"- Food types: {', '.join(food_types[:5])}\n"
                result += f"- Restaurants: {', '.join(restaurants[:3])}\n"
                result += f"- Total items: {count}\n"
                results.append(result)
        
        # Search restaurants
        restaurants = self.knowledge_data.get("restaurants", {})
        for restaurant, info in restaurants.items():
            if any(keyword in query_lower for keyword in [restaurant.lower(), "restaurant", "place", "location"]):
                cuisine_type = info.get("cuisine_type", "Unknown")
                location = info.get("location", "Unknown")
                categories = info.get("categories", [])
                
                result = f"**{restaurant}:**\n"
                result += f"- Cuisine: {cuisine_type}\n"
                result += f"- Location: {location}\n"
                result += f"- Categories: {', '.join(categories[:5])}\n"
                results.append(result)
        
        # Search dietary options
        dietary_options = self.knowledge_data.get("dietary_options", {})
        for diet, info in dietary_options.items():
            if any(keyword in query_lower for keyword in [diet.lower(), "dietary", "allergy", "vegetarian", "vegan"]):
                count = info.get("count", 0)
                restaurants = info.get("restaurants", [])
                
                result = f"**{diet} Options:**\n"
                result += f"- Available at {len(restaurants)} restaurants\n"
                result += f"- Total items: {count}\n"
                results.append(result)
        
        # Search food types
        food_types = self.knowledge_data.get("food_types", {})
        for food_type, info in food_types.items():
            if any(keyword in query_lower for keyword in [food_type.lower(), "food", "dish"]):
                count = info.get("count", 0)
                restaurants = info.get("restaurants", [])
                
                result = f"**{food_type}:**\n"
                result += f"- Available at {len(restaurants)} restaurants\n"
                result += f"- Total items: {count}\n"
                results.append(result)
        
        # Search locations
        locations = self.knowledge_data.get("locations", {})
        for location, info in locations.items():
            if any(keyword in query_lower for keyword in [location.lower(), "location", "building", "level"]):
                restaurants = info.get("restaurants", [])
                count = info.get("count", 0)
                
                result = f"**{location}:**\n"
                result += f"- Restaurants: {', '.join(restaurants[:5])}\n"
                result += f"- Total items: {count}\n"
                results.append(result)
        
        # If no specific matches, return general information
        if not results:
            general_info = "**Available Information:**\n"
            general_info += f"- {len(cuisine_types)} cuisine types\n"
            general_info += f"- {len(categories)} food categories\n"
            general_info += f"- {len(restaurants)} restaurants\n"
            general_info += f"- {len(dietary_options)} dietary options\n"
            general_info += f"- {len(food_types)} food types\n"
            results.append(general_info)
        
        return "\n".join(results[:5])  # Limit to 5 results
    
    def query_database_knowledge(self, query: str) -> str:
        """
        Query the database knowledge base for information about food, restaurants, cuisines, etc.
        
        Args:
            query: The search query (e.g., "pizza", "Italian food", "restaurants", "vegetarian options")
            
        Returns:
            Relevant information from the knowledge base
        """
        try:
            print(f"🔍 Querying knowledge base: {query}")
            result = self._search_knowledge(query)
            print(f"✅ Knowledge base result: {result[:100]}...")
            return result
        except Exception as e:
            print(f"❌ Error querying knowledge base: {e}")
            return f"Error querying knowledge base: {str(e)}"
    
    def get_available_cuisines(self) -> str:
        """Get all available cuisine types."""
        try:
            cuisine_types = self.knowledge_data.get("cuisine_types", {})
            if not cuisine_types:
                return "No cuisine types available."
            
            result = "**Available Cuisine Types:**\n"
            for cuisine, info in cuisine_types.items():
                count = info.get("count", 0)
                result += f"- {cuisine} ({count} items)\n"
            
            return result
        except Exception as e:
            return f"Error getting cuisines: {str(e)}"
    
    def get_available_categories(self) -> str:
        """Get all available food categories."""
        try:
            categories = self.knowledge_data.get("categories", {})
            if not categories:
                return "No categories available."
            
            result = "**Available Food Categories:**\n"
            for category, info in categories.items():
                count = info.get("count", 0)
                result += f"- {category} ({count} items)\n"
            
            return result
        except Exception as e:
            return f"Error getting categories: {str(e)}"
    
    def get_available_food_types(self) -> str:
        """Get all available food types."""
        try:
            food_types = self.knowledge_data.get("food_types", {})
            if not food_types:
                return "No food types available."
            
            result = "**Available Food Types:**\n"
            for food_type, info in food_types.items():
                count = info.get("count", 0)
                result += f"- {food_type} ({count} items)\n"
            
            return result
        except Exception as e:
            return f"Error getting food types: {str(e)}"
    
    def get_available_restaurants(self) -> str:
        """Get all available restaurants."""
        try:
            print("🔍 Getting available restaurants...")
            restaurants = self.knowledge_data.get("restaurants", {})
            print(f"✅ Found {len(restaurants)} restaurants in knowledge base")
            
            if not restaurants:
                print("❌ No restaurants found in knowledge base")
                return "No restaurants available."
            
            result = "**Available Restaurants:**\n"
            for restaurant, info in restaurants.items():
                cuisine_type = info.get("cuisine_type", "Unknown")
                location = info.get("location", "Unknown")
                result += f"- {restaurant} ({cuisine_type}) - {location}\n"
            
            print(f"✅ Successfully formatted {len(restaurants)} restaurants")
            return result
        except Exception as e:
            print(f"❌ Error getting restaurants: {e}")
            return f"Error getting restaurants: {str(e)}"
    
    def get_dietary_options(self) -> str:
        """Get all available dietary options."""
        try:
            dietary_options = self.knowledge_data.get("dietary_options", {})
            if not dietary_options:
                return "No dietary options available."
            
            result = "**Available Dietary Options:**\n"
            for diet, info in dietary_options.items():
                count = info.get("count", 0)
                result += f"- {diet} ({count} items)\n"
            
            return result
        except Exception as e:
            return f"Error getting dietary options: {str(e)}"

# Create global instance
knowledge_base = SimpleKnowledgeBase()

# Create standalone tool functions
@tool
def query_database_knowledge(query: str) -> str:
    """Query the database knowledge base for information about food, restaurants, cuisines, etc."""
    return knowledge_base.query_database_knowledge(query)

@tool
def get_available_cuisines() -> str:
    """Get all available cuisine types."""
    return knowledge_base.get_available_cuisines()

@tool
def get_available_categories() -> str:
    """Get all available food categories."""
    return knowledge_base.get_available_categories()

@tool
def get_available_food_types() -> str:
    """Get all available food types."""
    return knowledge_base.get_available_food_types()

@tool
def get_available_restaurants() -> str:
    """Get all available restaurants."""
    return knowledge_base.get_available_restaurants()

@tool
def get_dietary_options() -> str:
    """Get all available dietary options and tags."""
    return knowledge_base.get_dietary_options()

