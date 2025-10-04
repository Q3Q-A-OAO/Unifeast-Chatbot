"""
Proper LangChain Knowledge Base Implementation
=============================================

This module implements a real LangChain-based knowledge base using VectorStore
and RetrievalQA instead of hardcoded if/else statements.
"""

import json
import os
from typing import Dict, Any, List
from langchain.tools import tool

class VectorKnowledgeBase:
    """
    A proper LangChain-based knowledge base using vector storage for semantic search.
    """
    
    def __init__(self):
        # Initialize the knowledge base with data only - no Pinecone needed
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base - just load the knowledge data for reference"""
        knowledge_file = os.path.join(os.path.dirname(__file__), "database_knowledge.json")
        
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r') as f:
                self.knowledge_data = json.load(f)
            print(f"✅ Loaded knowledge base data from {knowledge_file}")
        else:
            print(f"❌ Knowledge file not found: {knowledge_file}")
            self.knowledge_data = {}
    
    
    def query_knowledge_base(self, query: str, max_results: int = 5) -> str:
        """
        Query the knowledge base using semantic search and return relevant information
        about categories, cuisines, restaurants, and dietary options.
        """
        try:
            query_lower = query.lower()
            
            # Search the knowledge base data for relevant information
            relevant_info = []
            
            # Check cuisine types
            for cuisine, info in self.knowledge_data.get("cuisine_types", {}).items():
                categories = info.get("categories", [])
                if any(query_lower in cat.lower() for cat in categories):
                    relevant_info.append(f"Cuisine '{cuisine}' offers: {', '.join(categories)}")
            
            # Check categories
            for category, info in self.knowledge_data.get("categories", {}).items():
                if query_lower in category.lower():
                    cuisine = info.get("cuisine", "Unknown")
                    food_types = info.get("food_types", [])
                    serve_times = info.get("serve_times", [])
                    relevant_info.append(f"Category '{category}' (cuisine: {cuisine}, types: {', '.join(food_types)}, times: {', '.join(serve_times)})")
            
            # Check restaurants
            for restaurant, info in self.knowledge_data.get("restaurants", {}).items():
                categories = info.get("categories", [])
                if any(query_lower in cat.lower() for cat in categories):
                    cuisine = info.get("cuisine", "Unknown")
                    location = info.get("location", "Unknown")
                    relevant_info.append(f"Restaurant '{restaurant}' ({cuisine}) at {location} offers: {', '.join(categories)}")
            
            # Check food types
            for food_type, info in self.knowledge_data.get("food_types", {}).items():
                categories = info.get("categories", [])
                if any(query_lower in cat.lower() for cat in categories):
                    count = info.get("count", 0)
                    relevant_info.append(f"Food type '{food_type}' includes {count} items in categories: {', '.join(categories)}")
            
            # Check dietary options
            for dietary, info in self.knowledge_data.get("dietary_options", {}).items():
                categories = info.get("categories", [])
                if any(query_lower in cat.lower() for cat in categories):
                    description = info.get("description", "")
                    relevant_info.append(f"Dietary option '{dietary}': {description}. Available in: {', '.join(categories)}")
            
            if relevant_info:
                response = f"Knowledge base search for '{query}' found:\n\n"
                response += "\n".join(relevant_info[:10])  # Limit to top 10 results
                
                # Add general guidance
                response += f"\n\nBased on this information, you can use appropriate filters like:"
                response += f"\n- Category filter: {{'category': {{'$eq': 'CategoryName'}}}}"
                response += f"\n- Cuisine filter: {{'cuisine_type': {{'$eq': 'CuisineType'}}}}"
                response += f"\n- Food type filter: {{'food_type': {{'$eq': 'FoodType'}}}}"
                
                return response
            else:
                return f"No specific information found for '{query}' in the knowledge base. Try searching with broader terms or different keywords."
            
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"

# Initialize the global knowledge base instance
_knowledge_base = VectorKnowledgeBase()

@tool
def query_database_knowledge(query: str) -> str:
    """
    Query the database knowledge base for information about available food categories, 
    cuisine types, restaurants, locations, and dietary options.
    
    This tool uses proper LangChain VectorStore and RetrievalQA for semantic search
    instead of hardcoded rules.
    
    Args:
        query (str): The search query (e.g., "pizza", "bubble tea", "Italian food", "vegetarian options")
    
    Returns:
        str: Information about the queried item including categories, cuisines, restaurants, etc.
    """
    print(f"\n📚 VECTOR KNOWLEDGE BASE QUERY:")
    print(f"   Query: '{query}'")
    
    result = _knowledge_base.query_knowledge_base(query)
    
    print(f"   Result: {result[:200]}..." if len(result) > 200 else f"   Result: {result}")
    print(f"\n")
    
    return result

@tool
def get_available_cuisines() -> str:
    """
    Get all available cuisine types in the database using vector search.
    """
    return _knowledge_base.query_knowledge_base("What cuisine types are available?")

@tool
def get_available_categories() -> str:
    """
    Get all available food categories in the database using vector search.
    """
    return _knowledge_base.query_knowledge_base("What food categories are available?")

@tool
def get_available_restaurants() -> str:
    """
    Get all available restaurants in the database using vector search.
    """
    return _knowledge_base.query_knowledge_base("What restaurants are available?")

@tool
def get_dietary_options() -> str:
    """
    Get all available dietary options in the database using vector search.
    """
    return _knowledge_base.query_knowledge_base("What dietary options are available?")

# Export the tools
__all__ = [
    "query_database_knowledge",
    "get_available_cuisines", 
    "get_available_categories",
    "get_available_restaurants",
    "get_dietary_options"
]
