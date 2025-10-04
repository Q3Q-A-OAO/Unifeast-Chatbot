"""
Database Knowledge Base Tool for LangChain Agent

This module provides a custom tool that allows the agent to query
database knowledge for better search filtering and recommendations.
"""

import json
import os
from typing import Dict, Any, List, Optional
from langchain.tools import tool


class DatabaseKnowledgeBase:
    """Knowledge base for database information"""
    
    def __init__(self, knowledge_file: str = None):
        """Initialize the knowledge base"""
        if knowledge_file is None:
            # Default to the knowledge file in the same directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_file = os.path.join(current_dir, "database_knowledge.json")
        
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from JSON file"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge file not found: {self.knowledge_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing knowledge file: {e}")
            return {}
    
    def get_cuisine_info(self, cuisine: str = None) -> Dict[str, Any]:
        """Get information about cuisine types"""
        if cuisine:
            return self.knowledge.get("cuisine_types", {}).get(cuisine, {})
        return self.knowledge.get("cuisine_types", {})
    
    def get_category_info(self, category: str = None) -> Dict[str, Any]:
        """Get information about food categories"""
        if category:
            return self.knowledge.get("categories", {}).get(category, {})
        return self.knowledge.get("categories", {})
    
    def get_restaurant_info(self, restaurant: str = None) -> Dict[str, Any]:
        """Get information about restaurants"""
        if restaurant:
            return self.knowledge.get("restaurants", {}).get(restaurant, {})
        return self.knowledge.get("restaurants", {})
    
    def get_dietary_info(self, dietary: str = None) -> Dict[str, Any]:
        """Get information about dietary options"""
        if dietary:
            return self.knowledge.get("dietary_options", {}).get(dietary, {})
        return self.knowledge.get("dietary_options", {})
    
    def get_food_type_info(self, food_type: str = None) -> Dict[str, Any]:
        """Get information about food types"""
        if food_type:
            return self.knowledge.get("food_types", {}).get(food_type, {})
        return self.knowledge.get("food_types", {})
    
    def get_location_info(self, location: str = None) -> Dict[str, Any]:
        """Get information about locations"""
        if location:
            return self.knowledge.get("locations", {}).get(location, {})
        return self.knowledge.get("locations", {})
    
    def search_food_info(self, query: str) -> str:
        """Search for food-related information based on query"""
        query_lower = query.lower()
        
        # Check for specific food items
        if "pizza" in query_lower:
            pizza_info = self.knowledge.get("search_insights", {}).get("pizza_info", {})
            if pizza_info:
                return f"Pizza Information: Category: {pizza_info.get('category')}, Cuisine: {pizza_info.get('cuisine')}, Restaurant: {pizza_info.get('restaurant')}, Location: {pizza_info.get('location')}, Count: {pizza_info.get('count')}, Food Type: {pizza_info.get('food_type')}, Serve Time: {pizza_info.get('serve_time')}"
        
        # Check for cuisine types
        for cuisine, info in self.knowledge.get("cuisine_types", {}).items():
            if cuisine.lower() in query_lower:
                categories = info.get("categories", [])
                restaurants = info.get("restaurants", [])
                return f"{cuisine} Cuisine: Categories: {', '.join(categories[:5])}, Restaurants: {', '.join(restaurants[:3])}, Count: {info.get('count', 'N/A')}"
        
        # Check for categories
        for category, info in self.knowledge.get("categories", {}).items():
            if category.lower() in query_lower:
                cuisine = info.get("cuisine", "N/A")
                restaurants = info.get("restaurants", [])
                food_types = info.get("food_types", [])
                return f"{category} Category: Cuisine: {cuisine}, Restaurants: {', '.join(restaurants[:3])}, Food Types: {', '.join(food_types)}, Count: {info.get('count', 'N/A')}"
        
        # Check for restaurants
        for restaurant, info in self.knowledge.get("restaurants", {}).items():
            if restaurant.lower() in query_lower:
                cuisine = info.get("cuisine", "N/A")
                location = info.get("location", "N/A")
                specialties = info.get("specialties", [])
                return f"{restaurant} Restaurant: Cuisine: {cuisine}, Location: {location}, Specialties: {', '.join(specialties[:3])}"
        
        # Check for dietary options
        for dietary, info in self.knowledge.get("dietary_options", {}).items():
            if dietary.lower() in query_lower:
                categories = info.get("categories", [])
                description = info.get("description", "N/A")
                return f"{dietary} Dietary Option: Description: {description}, Categories: {', '.join(categories[:5])}, Count: {info.get('count', 'N/A')}"
        
        # Check for common searches
        common_searches = self.knowledge.get("search_insights", {}).get("common_searches", {})
        for search_term, info in common_searches.items():
            if search_term.lower() in query_lower:
                return f"{search_term.title()} Search: {info}"
        
        return "No specific information found for this query. Available categories include: Pizza, Pasta, Burgers, Sushi, Beverages, Snacks, and more. Available cuisines include: Italian, American, British, Café, Chinese, Indian, International, Japanese, Mexican."
    
    def get_filter_suggestions(self, query: str) -> Dict[str, Any]:
        """Get filter suggestions based on query"""
        query_lower = query.lower()
        suggestions = {
            "category_filters": [],
            "cuisine_filters": [],
            "restaurant_filters": [],
            "dietary_filters": [],
            "food_type_filters": []
        }
        
        # Pizza suggestions
        if "pizza" in query_lower:
            suggestions["category_filters"].append("Pizza")
            suggestions["cuisine_filters"].append("Italian")
            suggestions["restaurant_filters"].append("La Cantina")
            suggestions["food_type_filters"].append("hot_dish")
        
        # Italian food suggestions
        if "italian" in query_lower:
            suggestions["cuisine_filters"].append("Italian")
            suggestions["category_filters"].extend(["Pizza", "Pasta"])
            suggestions["restaurant_filters"].append("La Cantina")
        
        # Coffee suggestions
        if "coffee" in query_lower or "drink" in query_lower:
            suggestions["category_filters"].extend(["Hot Coffee", "Cold Coffee", "Specialty Coffee"])
            suggestions["food_type_filters"].append("beverage")
        
        # Breakfast suggestions
        if "breakfast" in query_lower or "morning" in query_lower:
            suggestions["category_filters"].extend(["Breakfast", "Hot Breakfast", "Breakfast Components"])
            suggestions["food_type_filters"].append("hot_dish")
        
        # Lunch suggestions
        if "lunch" in query_lower:
            suggestions["category_filters"].extend(["Main Dishes", "Pizza", "Pasta", "Sandwiches", "Burgers"])
            suggestions["food_type_filters"].append("hot_dish")
        
        # Vegetarian suggestions
        if "vegetarian" in query_lower:
            suggestions["dietary_filters"].append("vegetarian")
            suggestions["category_filters"].extend(["Pizza", "Pasta", "Salads"])
        
        # Vegan suggestions
        if "vegan" in query_lower:
            suggestions["dietary_filters"].append("vegan")
            suggestions["category_filters"].extend(["Salads", "Fresh Fruit"])
        
        return suggestions


# Global knowledge base instance
_knowledge_base = DatabaseKnowledgeBase()


@tool
def query_database_knowledge(query: str) -> str:
    """
    Query the database knowledge base for information about available food categories, 
    cuisine types, restaurants, locations, and dietary options.
    
    Use this tool when you need to understand what's available in the database before
    performing searches. This helps with better filtering and more accurate results.
    
    Args:
        query (str): The search query (e.g., "pizza", "Italian food", "coffee", "vegetarian options")
    
    Returns:
        str: Information about the queried item including categories, cuisines, restaurants, etc.
    """
    print(f"\n📚 KNOWLEDGE BASE QUERY DEBUG:")
    print(f"   Query: '{query}'")
    result = _knowledge_base.search_food_info(query)
    print(f"   Result: {result[:200]}..." if len(result) > 200 else f"   Result: {result}")
    print(f"\n")
    return result




@tool
def get_available_cuisines() -> str:
    """
    Get all available cuisine types in the database.
    
    Returns:
        str: List of all available cuisine types with their information
    """
    cuisines = _knowledge_base.get_cuisine_info()
    result = []
    for cuisine, info in cuisines.items():
        categories = info.get("categories", [])
        restaurants = info.get("restaurants", [])
        result.append(f"{cuisine}: Categories: {', '.join(categories[:3])}, Restaurants: {', '.join(restaurants[:2])}")
    
    return f"Available Cuisines:\n" + "\n".join(result)


@tool
def get_available_categories() -> str:
    """
    Get all available food categories in the database.
    
    Returns:
        str: List of all available categories with their information
    """
    categories = _knowledge_base.get_category_info()
    result = []
    for category, info in categories.items():
        cuisine = info.get("cuisine", "N/A")
        count = info.get("count", "N/A")
        result.append(f"{category} (Count: {count}, Cuisine: {cuisine})")
    
    return f"Available Categories:\n" + "\n".join(result[:20])  # Limit to first 20


@tool
def get_available_restaurants() -> str:
    """
    Get all available restaurants in the database.
    
    Returns:
        str: List of all available restaurants with their information
    """
    restaurants = _knowledge_base.get_restaurant_info()
    result = []
    for restaurant, info in restaurants.items():
        cuisine = info.get("cuisine", "N/A")
        location = info.get("location", "N/A")
        specialties = info.get("specialties", [])
        result.append(f"{restaurant}: Cuisine: {cuisine}, Location: {location}, Specialties: {', '.join(specialties[:2])}")
    
    return f"Available Restaurants:\n" + "\n".join(result)


@tool
def get_dietary_options() -> str:
    """
    Get all available dietary options in the database.
    
    Returns:
        str: List of all available dietary options with their information
    """
    dietary_options = _knowledge_base.get_dietary_info()
    result = []
    for dietary, info in dietary_options.items():
        description = info.get("description", "N/A")
        categories = info.get("categories", [])
        result.append(f"{dietary}: {description}, Categories: {', '.join(categories[:3])}")
    
    return f"Available Dietary Options:\n" + "\n".join(result)


# Export the tools for use in the agent
__all__ = [
    "query_database_knowledge",
    "get_available_cuisines",
    "get_available_categories",
    "get_available_restaurants",
    "get_dietary_options"
]
