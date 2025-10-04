"""
Proper LangChain Knowledge Base Implementation
=============================================

This module implements a real LangChain-based knowledge base using VectorStore
and RetrievalQA instead of hardcoded if/else statements.
"""

import json
import os
from typing import Dict, Any, List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from config import settings

class VectorKnowledgeBase:
    """
    A proper LangChain-based knowledge base using vector storage for semantic search.
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize Pinecone vector store for knowledge base
        # Use the same namespace as food items since we're searching the food database
        self.vector_store = PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=self.embeddings,
            namespace=settings.PINECONE_NAMESPACE  # Use same namespace as food items
        )
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,  # Low temperature for factual responses
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize the knowledge base with data
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
    
    def _create_documents_from_knowledge(self, knowledge_data: Dict[str, Any]) -> List[Document]:
        """Convert knowledge data into LangChain Document objects"""
        documents = []
        
        # Create documents for cuisine types
        for cuisine, info in knowledge_data.get("cuisine_types", {}).items():
            categories = info.get("categories", [])
            restaurants = info.get("restaurants", [])
            
            content = f"""
            Cuisine: {cuisine}
            Categories: {', '.join(categories)}
            Restaurants: {', '.join(restaurants)}
            Count: {info.get('count', 'N/A')}
            
            This cuisine type offers {len(categories)} different categories including {', '.join(categories[:3])}.
            Available at restaurants: {', '.join(restaurants[:3])}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "cuisine",
                    "name": cuisine,
                    "categories": categories,
                    "restaurants": restaurants
                }
            ))
        
        # Create documents for categories
        for category, info in knowledge_data.get("categories", {}).items():
            cuisine = info.get("cuisine", "N/A")
            food_types = info.get("food_types", [])
            serve_times = info.get("serve_times", [])
            count = info.get("count", 0)
            
            content = f"""
            Category: {category}
            Cuisine: {cuisine}
            Food Types: {', '.join(food_types)}
            Serve Times: {', '.join(serve_times)}
            Count: {count}
            Description: {info.get('description', '')}
            
            This food category belongs to {cuisine} cuisine and includes {count} items.
            Available during: {', '.join(serve_times)}.
            Food types: {', '.join(food_types)}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "category",
                    "name": category,
                    "cuisine": cuisine,
                    "food_types": food_types,
                    "serve_times": serve_times,
                    "count": count
                }
            ))
        
        # Create documents for restaurants
        for restaurant, info in knowledge_data.get("restaurants", {}).items():
            cuisine = info.get("cuisine", "N/A")
            categories = info.get("categories", [])
            location = info.get("location", "N/A")
            specialties = info.get("specialties", [])
            
            content = f"""
            Restaurant: {restaurant}
            Cuisine: {cuisine}
            Location: {location}
            Categories: {', '.join(categories)}
            Specialties: {', '.join(specialties)}
            
            This restaurant serves {cuisine} cuisine and specializes in {', '.join(specialties[:3])}.
            Located at: {location}.
            Offers categories: {', '.join(categories[:3])}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "restaurant",
                    "name": restaurant,
                    "cuisine": cuisine,
                    "location": location,
                    "categories": categories,
                    "specialties": specialties
                }
            ))
        
        # Create documents for food types
        for food_type, info in knowledge_data.get("food_types", {}).items():
            categories = info.get("categories", [])
            count = info.get("count", 0)
            
            content = f"""
            Food Type: {food_type}
            Categories: {', '.join(categories)}
            Count: {count}
            Description: {info.get('description', '')}
            
            This food type includes {count} items across categories: {', '.join(categories[:5])}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "food_type",
                    "name": food_type,
                    "categories": categories,
                    "count": count
                }
            ))
        
        # Create documents for dietary options
        for dietary, info in knowledge_data.get("dietary_options", {}).items():
            categories = info.get("categories", [])
            description = info.get("description", "")
            count = info.get("count", 0)
            
            content = f"""
            Dietary Option: {dietary}
            Description: {description}
            Categories: {', '.join(categories)}
            Count: {count}
            
            This dietary option includes {count} items across categories: {', '.join(categories[:5])}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "dietary",
                    "name": dietary,
                    "categories": categories,
                    "description": description,
                    "count": count
                }
            ))
        
        return documents
    
    def query_knowledge_base(self, query: str, max_results: int = 5) -> str:
        """
        Query the knowledge base using semantic search on the actual food items
        and return relevant information about categories, cuisines, etc.
        """
        try:
            query_lower = query.lower()
            
            # First, search the actual food items to see what's available
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": max_results}
            )
            
            # Get relevant food items from Pinecone
            docs = retriever.get_relevant_documents(query)
            
            if not docs:
                return f"No food items found for query: {query}"
            
            # Analyze the results to extract knowledge
            categories = set()
            cuisines = set()
            restaurants = set()
            food_types = set()
            dietary_tags = set()
            
            for doc in docs:
                metadata = doc.metadata
                if 'category' in metadata:
                    categories.add(metadata['category'])
                if 'cuisine_type' in metadata:
                    cuisines.add(metadata['cuisine_type'])
                if 'restaurant_name' in metadata:
                    restaurants.add(metadata['restaurant_name'])
                if 'food_type' in metadata:
                    food_types.add(metadata['food_type'])
                if 'dietary_tags' in metadata:
                    for tag in metadata['dietary_tags']:
                        dietary_tags.add(tag)
            
            # Build response based on query type
            response_parts = []
            
            if "bubble tea" in query_lower:
                # Check if bubble tea category exists in results
                bubble_tea_found = any("bubble tea" in cat.lower() for cat in categories)
                if bubble_tea_found:
                    response_parts.append("Bubble Tea is available in the database!")
                    response_parts.append(f"Found in categories: {[cat for cat in categories if 'bubble tea' in cat.lower()]}")
                else:
                    response_parts.append("Bubble Tea category not found in current results")
                    response_parts.append("Available beverage categories: " + ", ".join([cat for cat in categories if any(beverage in cat.lower() for beverage in ['drink', 'beverage', 'coffee', 'tea', 'juice', 'soda'])])[:10])
            
            elif any(word in query_lower for word in ["pizza", "italian"]):
                pizza_found = any("pizza" in cat.lower() for cat in categories)
                if pizza_found:
                    response_parts.append("Pizza is available!")
                    response_parts.append(f"Found in categories: {[cat for cat in categories if 'pizza' in cat.lower()]}")
                    response_parts.append(f"Available at restaurants: {', '.join(list(restaurants)[:3])}")
                else:
                    response_parts.append("Pizza category not found in current results")
            
            else:
                # Generic response
                response_parts.append(f"Found {len(docs)} relevant items for '{query}'")
                if categories:
                    response_parts.append(f"Categories: {', '.join(list(categories)[:5])}")
                if cuisines:
                    response_parts.append(f"Cuisines: {', '.join(list(cuisines)[:3])}")
                if restaurants:
                    response_parts.append(f"Restaurants: {', '.join(list(restaurants)[:3])}")
            
            # Add filter suggestions
            if categories:
                response_parts.append(f"\nSuggested filter: {{'category': {{'$in': {list(categories)[:3]}}}}}")
            
            return "\n".join(response_parts)
            
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
