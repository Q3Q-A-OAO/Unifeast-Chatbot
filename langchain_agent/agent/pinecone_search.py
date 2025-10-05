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


@tool
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
        logger.info(f"Searching Pinecone for: {query_text}")
        logger.info(f"Using filter: {filter_dict}")
        
        # Initialize Pinecone client
        logger.info("Initializing Pinecone client...")
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        logger.info("Pinecone client initialized")
        
        # Get index
        logger.info(f"Getting Pinecone index: {settings.PINECONE_INDEX_NAME}")
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        logger.info("Pinecone index retrieved")
        
        # Get embedding for query
        logger.info("Getting OpenAI embedding...")
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=query_text,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        query_embedding = response.data[0].embedding
        logger.info("OpenAI embedding retrieved")
        
        # Perform search (with or without filter)
        logger.info("Performing Pinecone search...")
        if filter_dict:
            logger.info(f"Searching with filter: {filter_dict}")
            search_results = index.query(
                vector=query_embedding,
                filter=filter_dict,
                top_k=top_k,
                namespace=settings.PINECONE_NAMESPACE,
                include_metadata=True
            )
        else:
            logger.info("Searching without filter")
            search_results = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=settings.PINECONE_NAMESPACE,
                include_metadata=True
            )
        logger.info("Pinecone search completed")
        
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
        logger.error(f"Failed to search Pinecone: {e}")
        return {"error": f"Failed to search Pinecone: {str(e)}"}
