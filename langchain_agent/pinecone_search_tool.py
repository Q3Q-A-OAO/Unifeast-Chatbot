"""
Pinecone Search Tool for LangChain Agent
========================================

A tool for performing semantic search with metadata filtering on Pinecone food database.
This tool is used by the agent to find food recommendations based on user preferences and search criteria.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from langchain.tools import tool
from pinecone.core import Pinecone
from openai import OpenAI

logger = logging.getLogger(__name__)

def get_openai_client():
    """Get OpenAI client with API key from environment."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using OpenAI."""
    try:
        client = get_openai_client()
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        return []

@tool("search_food_recommendations")
def search_food_recommendations(
    query_text: str,
    filter_dict: Dict[str, Any],
    top_k: int = 10,
    namespace: str = "food"
) -> Dict[str, Any]:
    """
    Search for food recommendations using Pinecone with semantic search and metadata filtering.
    
    Args:
        query_text: The search query (e.g., "spicy Indian food", "vegetarian pasta")
        filter_dict: The filter dictionary from filter_builder_tools.py
        top_k: Number of results to return (default: 10)
        namespace: Pinecone namespace (default: "food")
    
    Returns:
        Dictionary containing search results with food items and metadata
    """
    try:
        logger.info(f"Searching for: {query_text}")
        logger.info(f"Using filter: {filter_dict}")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Get index
        index_name = os.getenv("PINECONE_INDEX_NAME", "unifeast-food-index")
        index = pc.Index(index_name)
        
        # Get embedding for query
        query_embedding = get_embedding(query_text)
        if not query_embedding:
            return {"error": "Failed to generate embedding for query"}
        
        # Perform hybrid search (vector + metadata filtering)
        search_results = index.query(
            vector=query_embedding,
            filter=filter_dict,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )
        
        # Process results
        food_items = []
        for match in search_results.matches:
            food_item = {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            food_items.append(food_item)
        
        result = {
            "query": query_text,
            "filter_used": filter_dict,
            "total_results": len(food_items),
            "food_items": food_items
        }
        
        logger.info(f"Found {len(food_items)} food items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to search food recommendations: {e}")
        return {"error": f"Failed to search food recommendations: {str(e)}"}

def search_food_recommendations_test(
    query_text: str,
    filter_dict: Dict[str, Any],
    top_k: int = 10,
    namespace: str = "food"
) -> Dict[str, Any]:
    """
    Test version of search_food_recommendations without @tool decorator.
    """
    try:
        logger.info(f"Searching for: {query_text}")
        logger.info(f"Using filter: {filter_dict}")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Get index
        index_name = os.getenv("PINECONE_INDEX_NAME", "unifeast-food-index")
        index = pc.Index(index_name)
        
        # Get embedding for query
        query_embedding = get_embedding(query_text)
        if not query_embedding:
            return {"error": "Failed to generate embedding for query"}
        
        # Perform hybrid search (vector + metadata filtering)
        search_results = index.query(
            vector=query_embedding,
            filter=filter_dict,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )
        
        # Process results
        food_items = []
        for match in search_results.matches:
            food_item = {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            food_items.append(food_item)
        
        result = {
            "query": query_text,
            "filter_used": filter_dict,
            "total_results": len(food_items),
            "food_items": food_items
        }
        
        logger.info(f"Found {len(food_items)} food items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to search food recommendations: {e}")
        return {"error": f"Failed to search food recommendations: {str(e)}"}

@tool("search_food_by_cuisine")
def search_food_by_cuisine(
    cuisine_type: str,
    filter_dict: Dict[str, Any],
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Search for food items by cuisine type with user preferences filtering.
    
    Args:
        cuisine_type: The cuisine type (e.g., "Indian", "Chinese", "Italian")
        filter_dict: The filter dictionary from filter_builder_tools.py
        top_k: Number of results to return (default: 10)
    
    Returns:
        Dictionary containing food items of the specified cuisine
    """
    try:
        query_text = f"{cuisine_type} food"
        return search_food_recommendations(query_text, filter_dict, top_k)
        
    except Exception as e:
        logger.error(f"Failed to search food by cuisine: {e}")
        return {"error": f"Failed to search food by cuisine: {str(e)}"}

@tool("search_food_by_price_range")
def search_food_by_price_range(
    max_price: float,
    filter_dict: Dict[str, Any],
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Search for food items within a specific price range.
    
    Args:
        max_price: Maximum price to search for
        filter_dict: The filter dictionary from filter_builder_tools.py
        top_k: Number of results to return (default: 10)
    
    Returns:
        Dictionary containing food items within the price range
    """
    try:
        # Update filter with price constraint
        updated_filter = filter_dict.copy()
        user_identity = filter_dict.get("user_identity", "student")
        
        if user_identity == "student":
            updated_filter["student_price"] = {"$lte": max_price}
        elif user_identity == "staff":
            updated_filter["staff_price"] = {"$lte": max_price}
        
        query_text = f"food under £{max_price}"
        return search_food_recommendations(query_text, updated_filter, top_k)
        
    except Exception as e:
        logger.error(f"Failed to search food by price range: {e}")
        return {"error": f"Failed to search food by price range: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Pinecone Search Tool")
    print("=" * 50)
    
    # Test filter (example from filter_builder_tools.py)
    test_filter = {
        "milk_allergy": {"$eq": False},
        "eggs_allergy": {"$eq": False},
        "peanuts_allergy": {"$eq": False},
        "shellfish_allergy": {"$eq": False},
        "other_allergies": {"$nin": ["banana", "noodles"]},
        "dietary_preferences": {"$in": ["vegetarian"]},
        "student_price": {"$lte": 8.0},
        "cuisine_type": {"$in": ["Indian"]}
    }
    
    # Test 1: Search for spicy Indian food
    print("\n1. Searching for spicy Indian food:")
    result1 = search_food_recommendations("spicy Indian food", test_filter, top_k=5)
    print(f"Results: {result1}")
    
    # Test 2: Search by cuisine
    print("\n2. Searching by cuisine (Chinese):")
    result2 = search_food_by_cuisine("Chinese", test_filter, top_k=5)
    print(f"Results: {result2}")
    
    # Test 3: Search by price range
    print("\n3. Searching by price range (£5):")
    result3 = search_food_by_price_range(5.0, test_filter, top_k=5)
    print(f"Results: {result3}")
    
    print("\n✅ Pinecone search tool testing completed!") 