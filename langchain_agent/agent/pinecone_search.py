"""
Pinecone Search Module
=====================

Handles semantic search functionality for food items using Pinecone vector database.
"""

import logging
from typing import Dict, Any

# Pinecone and OpenAI for search
from pinecone import Pinecone
from openai import OpenAI

# LangChain tools
from langchain.tools import tool

# Local configuration
from config import settings

logger = logging.getLogger(__name__)


@tool("search_pinecone")
def search_pinecone(
    query_text: str,
    filter_dict: Dict[str, Any] = None,
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Search for food items in Pinecone using semantic search and optional metadata filtering.
    
    Args:
        query_text: The search query (e.g., "spicy Indian food", "cold drinks", "vegetarian pasta")
        filter_dict: Optional filter dictionary for metadata filtering (e.g., price, allergies, dietary preferences)
        top_k: Number of results to return (default: 10)
    
    Returns:
        Dictionary containing search results with food items and metadata
    """
    try:
        # Enhanced debugging
        print(f"\n🔍 PINECONE SEARCH DEBUG:")
        print(f"   Query Text: '{query_text}'")
        print(f"   Filter Dict: {filter_dict}")
        print(f"   Top K: {top_k}")
        print(f"   Index: {settings.PINECONE_INDEX_NAME}")
        print(f"   Namespace: {settings.PINECONE_NAMESPACE}")
        
        logger.info(f"Searching Pinecone for: {query_text}")
        logger.info(f"Using filter: {filter_dict}")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Get index
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Get embedding for query
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=query_text,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        query_embedding = response.data[0].embedding
        
        # Perform search (with or without filter)
        if filter_dict:
            search_results = index.query(
                vector=query_embedding,
                filter=filter_dict,
                top_k=top_k,
                namespace=settings.PINECONE_NAMESPACE,
                include_metadata=True
            )
        else:
            search_results = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=settings.PINECONE_NAMESPACE,
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
        
        # Enhanced debugging for results
        print(f"\n📊 PINECONE SEARCH RESULTS:")
        print(f"   Total Results: {len(food_items)}")
        if food_items:
            print(f"   Top 3 Results:")
            for i, item in enumerate(food_items[:3]):
                print(f"     {i+1}. {item['metadata'].get('dish_name', 'Unknown')} - Score: {item['score']:.4f}")
                print(f"        Category: {item['metadata'].get('category', 'N/A')}")
                print(f"        Restaurant: {item['metadata'].get('restaurant_name', 'N/A')}")
        else:
            print(f"   No results found!")
        print(f"\n")
        
        logger.info(f"Found {len(food_items)} food items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to search Pinecone: {e}")
        return {"error": f"Failed to search Pinecone: {str(e)}"}
