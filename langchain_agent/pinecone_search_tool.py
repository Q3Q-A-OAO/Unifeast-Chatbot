"""
Pinecone Search Tool for LangChain Agent
========================================

Custom tool for semantic search and metadata filtering of food items using Pinecone.
Based on the working logic from test_pinecone.py.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from langchain.tools import tool

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get credentials from .env
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'unifeast-food-02')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI for semantic search."""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        raise

def format_food_result(match: Any) -> Dict[str, Any]:
    """Format a Pinecone match into a structured food item with all available metadata."""
    metadata = match.metadata
    
    return {
        # Core identification
        "id": match.id,
        "score": round(match.score, 4),
        "original_id": metadata.get('id', 'N/A'),
        
        # Basic food info
        "dish_name": metadata.get('dish_name', 'N/A'),
        "description": metadata.get('description', 'N/A'),
        "notes": metadata.get('notes', 'N/A'),
        "category": metadata.get('category', 'N/A'),
        "cuisine_type": metadata.get('cuisine_type', 'N/A'),
        "food_type": metadata.get('food_type', 'N/A'),
        
        # Ingredients and dietary info
        "ingredients": metadata.get('ingredients', []),
        "dietary_tags": metadata.get('dietary_tags', []),
        
        # Pricing
        "student_price": metadata.get('student_price', 'N/A'),
        "staff_price": metadata.get('staff_price', 'N/A'),
        
        # Restaurant and location
        "restaurant_name": metadata.get('restaurant_name', 'N/A'),
        "restaurant_id": metadata.get('restaurant_id', 'N/A'),
        "location": metadata.get('location', 'N/A'),
        "opening_hours": metadata.get('opening_hours', 'N/A'),
        
        # Timing and availability
        "serve_time": metadata.get('serve_time', 'N/A'),
        "available": metadata.get('available', False),
        
        # Allergy information (boolean flags)
        "milk_allergy": metadata.get('milk_allergy', False),
        "eggs_allergy": metadata.get('eggs_allergy', False),
        "peanuts_allergy": metadata.get('peanuts_allergy', False),
        "tree_nuts_allergy": metadata.get('tree_nuts_allergy', False),
        "shellfish_allergy": metadata.get('shellfish_allergy', False),
        "other_allergens": metadata.get('other_allergens', []),
        
        # Additional fields
        "accessibility": metadata.get('accessibility', ''),
        "text": metadata.get('text', ''),  # Combined text field for embeddings
        "_ab_stream": metadata.get('_ab_stream', '')  # Data stream source
    }

@tool("search_food")
def search_food(query: str, filter: Optional[Dict[str, Any]] = None, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Search for food items using semantic search and metadata filtering.
    
    Args:
        query: Natural language search query (e.g., "spicy Indian food", "cold drinks")
        filter: Optional metadata filter dict for precise filtering
        top_k: Number of results to return (default: 10, max: 100)
    
    Returns:
        List of food items with comprehensive structured data including name, price, description, 
        allergies, restaurant info, location, timing, and more.
    
    Available filter fields:
        Pricing:
            - student_price: {"$lte": 5.0} or {"$gte": 3.0}
            - staff_price: {"$lte": 8.0}
        
        Cuisine and Categories:
            - cuisine_type: {"$in": ["Indian", "Chinese", "Mexican"]}
            - category: {"$in": ["Burritos", "Beverages", "Snacks"]}
            - food_type: {"$in": ["savory", "sweet"]}
        
        Dietary Preferences:
            - dietary_tags: {"$in": ["vegetarian", "vegan", "spicy", "gluten_free"]}
        
        Allergy Filters (boolean fields):
            - milk_allergy: {"$eq": false} (safe for milk allergy)
            - eggs_allergy: {"$eq": false} (safe for egg allergy)
            - peanuts_allergy: {"$eq": false} (safe for peanut allergy)
            - tree_nuts_allergy: {"$eq": false} (safe for tree nut allergy)
            - shellfish_allergy: {"$eq": false} (safe for shellfish allergy)
            - other_allergens: {"$nin": ["gluten", "soy"]} (exclude specific allergens)
        
        Restaurant and Location:
            - restaurant_name: {"$in": ["La Cantina", "Campus Cafe"]}
            - restaurant_id: {"$eq": "la_cantina"}
            - location: {"$in": ["Level 2 Sherfield Building", "Main Campus"]}
        
        Timing and Availability:
            - serve_time: {"$in": ["breakfast", "lunch", "dinner"]}
            - available: {"$eq": true}
            - opening_hours: {"$regex": "Monday-Friday"}
        
        General:
            - _ab_stream: {"$eq": "unifeast_food"} (filter to food items only)
    
    Example complex filters:
        - Vegetarian Indian food under £6: {"cuisine_type": {"$in": ["Indian"]}, "dietary_tags": {"$in": ["vegetarian"]}, "student_price": {"$lte": 6.0}}
        - Safe for milk and egg allergies: {"milk_allergy": {"$eq": false}, "eggs_allergy": {"$eq": false}}
        - Lunch items at specific location: {"serve_time": {"$eq": "lunch"}, "location": {"$in": ["Level 2 Sherfield Building"]}}
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k <= 0 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")
        
        # Get embedding for semantic search
        logger.info(f"Getting embedding for query: {query}")
        embedding = get_embedding(query)
        
        # Get Pinecone index
        index = pc.Index(name=PINECONE_INDEX_NAME)
        
        # Prepare query parameters
        query_params = {
            "vector": embedding,
            "top_k": top_k,
            "include_metadata": True,
            "namespace": "__default__"  # Using default namespace as per your working test
        }
        
        # Add filter if provided
        if filter:
            query_params["filter"] = filter
            logger.info(f"Applying filter: {filter}")
        
        # Execute search
        logger.info(f"Searching Pinecone with query: {query}")
        results = index.query(**query_params)
        
        # Format results
        formatted_results = []
        for match in results.matches:
            food_item = format_food_result(match)
            formatted_results.append(food_item)
        
        logger.info(f"Found {len(formatted_results)} food items")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "error": f"Search failed: {str(e)}",
            "results": []
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the tool
    print("🧪 Testing Pinecone Search Tool")
    print("=" * 50)
    
    # Test 1: Basic search
    print("\n1. Basic search for 'cold drinks':")
    results = search_food("cold drinks", top_k=3)
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item['dish_name']} - £{item['student_price']}")
    
    # Test 2: Search with price filter
    print("\n2. Search for 'coffee' under £4:")
    results = search_food("coffee", filter={"student_price": {"$lte": 4.0}}, top_k=3)
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item['dish_name']} - £{item['student_price']}")
    
    # Test 3: Search with cuisine filter
    print("\n3. Search for 'food' in Indian cuisine:")
    results = search_food("food", filter={"cuisine_type": {"$in": ["Indian"]}}, top_k=3)
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item['dish_name']} - {item['cuisine_type']}")
    
    print("\n✅ Tool testing completed!") 