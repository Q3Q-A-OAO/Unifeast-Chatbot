"""
Real LangChain Knowledge Base Implementation
===========================================

Following the Medium article guide:
https://cismography.medium.com/building-a-knowledge-base-for-custom-llms-using-langchain-chroma-and-gpt4all-950906ae496d

This implements a proper knowledge base using:
- LangChain Document loaders
- Text splitters for chunking
- Vector embeddings
- Chroma vector database
- RetrievalQA chain
"""

import os
import json
from typing import List, Optional
from langchain.tools import tool
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from config import settings

class DatabaseKnowledgeBase:
    """
    Real LangChain knowledge base implementation following the Medium article guide.
    Uses document loading, text splitting, embeddings, and vector storage.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, target_chunks: int = 4):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.target_chunks = target_chunks
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize LLM for QA chain
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Chroma settings following the article
        self.chroma_settings = {
            'persist_directory': './knowledge_base_db',
            'anonymized_telemetry': False
        }
        
        # Initialize vector store and QA chain
        self.vector_store = None
        self.qa_chain = None
        
        # Build the knowledge base
        self._build_knowledge_base()
    
    def _load_documents(self) -> List[Document]:
        """
        Load documents from the database knowledge JSON file.
        Convert the structured data into Document objects for processing.
        """
        knowledge_file = os.path.join(os.path.dirname(__file__), "database_knowledge.json")
        
        if not os.path.exists(knowledge_file):
            print(f"❌ Knowledge file not found: {knowledge_file}")
            return []
        
        with open(knowledge_file, 'r') as f:
            knowledge_data = json.load(f)
        
        documents = []
        
        # Convert knowledge data to documents
        for cuisine, info in knowledge_data.get("cuisine_types", {}).items():
            categories = info.get("categories", [])
            restaurants = info.get("restaurants", [])
            count = info.get("count", 0)
            
            content = f"""
            Cuisine Type: {cuisine}
            Available Categories: {', '.join(categories)}
            Restaurants: {', '.join(restaurants)}
            Item Count: {count}
            
            This cuisine type offers {len(categories)} different food categories including {', '.join(categories[:5])}.
            Available at {len(restaurants)} restaurants: {', '.join(restaurants[:3])}.
            """
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "type": "cuisine",
                    "name": cuisine,
                    "categories": categories,
                    "restaurants": restaurants,
                    "count": count
                }
            ))
        
        # Add category documents
        for category, info in knowledge_data.get("categories", {}).items():
            cuisine = info.get("cuisine", "Unknown")
            food_types = info.get("food_types", [])
            serve_times = info.get("serve_times", [])
            count = info.get("count", 0)
            description = info.get("description", "")
            
            content = f"""
            Food Category: {category}
            Cuisine Type: {cuisine}
            Food Types: {', '.join(food_types)}
            Serve Times: {', '.join(serve_times)}
            Item Count: {count}
            Description: {description}
            
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
        
        # Add restaurant documents
        for restaurant, info in knowledge_data.get("restaurants", {}).items():
            cuisine = info.get("cuisine", "Unknown")
            categories = info.get("categories", [])
            location = info.get("location", "Unknown")
            specialties = info.get("specialties", [])
            
            content = f"""
            Restaurant: {restaurant}
            Cuisine Type: {cuisine}
            Location: {location}
            Available Categories: {', '.join(categories)}
            Specialties: {', '.join(specialties)}
            
            This restaurant serves {cuisine} cuisine and specializes in {', '.join(specialties[:3])}.
            Located at: {location}.
            Offers {len(categories)} categories: {', '.join(categories[:5])}.
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
        
        # Add food type documents
        for food_type, info in knowledge_data.get("food_types", {}).items():
            categories = info.get("categories", [])
            count = info.get("count", 0)
            description = info.get("description", "")
            
            content = f"""
            Food Type: {food_type}
            Available Categories: {', '.join(categories)}
            Item Count: {count}
            Description: {description}
            
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
        
        print(f"✅ Loaded {len(documents)} documents from knowledge base")
        return documents
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using RecursiveCharacterTextSplitter.
        Following the Medium article approach.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"✅ Split documents into {len(split_docs)} chunks")
        return split_docs
    
    def _create_embeddings(self, documents: List[Document]):
        """
        Create embeddings and store in Chroma vector database.
        Following the Medium article Chroma setup.
        """
        try:
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.chroma_settings['persist_directory'],
                anonymized_telemetry=self.chroma_settings['anonymized_telemetry']
            )
            
            # Persist the database
            self.vector_store.persist()
            print(f"✅ Created Chroma vector store with {len(documents)} documents")
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            # Fallback to in-memory storage
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            print("✅ Created in-memory vector store as fallback")
    
    def _create_qa_chain(self):
        """
        Create RetrievalQA chain following the Medium article approach.
        """
        if not self.vector_store:
            print("❌ No vector store available for QA chain")
            return
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.target_chunks}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=True
        )
        
        print("✅ Created RetrievalQA chain")
    
    def _build_knowledge_base(self):
        """
        Build the complete knowledge base following the Medium article workflow:
        1. Load documents
        2. Split into chunks
        3. Create embeddings
        4. Store in vector database
        5. Create QA chain
        """
        print("🏗️ Building knowledge base...")
        
        # Step 1: Load documents
        documents = self._load_documents()
        if not documents:
            print("❌ No documents loaded")
            return
        
        # Step 2: Split documents
        split_docs = self._split_documents(documents)
        
        # Step 3: Create embeddings and vector store
        self._create_embeddings(split_docs)
        
        # Step 4: Create QA chain
        self._create_qa_chain()
        
        print("✅ Knowledge base built successfully!")
    
    def query(self, query: str) -> str:
        """
        Query the knowledge base using RetrievalQA chain.
        Following the Medium article approach.
        """
        if not self.qa_chain:
            return "Knowledge base not available. Please rebuild the knowledge base."
        
        try:
            result = self.qa_chain({"query": query})
            answer = result["result"]
            source_docs = result["source_documents"]
            
            # Add source information
            if source_docs:
                sources = []
                for doc in source_docs[:3]:  # Limit to top 3 sources
                    metadata = doc.metadata
                    if metadata.get("type") == "cuisine":
                        sources.append(f"Cuisine: {metadata.get('name')}")
                    elif metadata.get("type") == "category":
                        sources.append(f"Category: {metadata.get('name')} ({metadata.get('cuisine')})")
                    elif metadata.get("type") == "restaurant":
                        sources.append(f"Restaurant: {metadata.get('name')} ({metadata.get('location')})")
                    elif metadata.get("type") == "food_type":
                        sources.append(f"Food Type: {metadata.get('name')}")
                
                if sources:
                    answer += f"\n\nBased on: {', '.join(sources)}"
            
            return answer
            
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"

# Initialize the global knowledge base instance
_knowledge_base = DatabaseKnowledgeBase()

@tool
def query_database_knowledge(query: str) -> str:
    """
    Query the database knowledge base using proper LangChain RetrievalQA chain.
    
    This tool uses real semantic search with embeddings and vector storage,
    following the Medium article methodology.
    
    Args:
        query (str): The search query (e.g., "pizza", "bubble tea", "Italian food")
    
    Returns:
        str: Semantic search results from the knowledge base
    """
    print(f"\n📚 REAL KNOWLEDGE BASE QUERY:")
    print(f"   Query: '{query}'")
    
    result = _knowledge_base.query(query)
    
    print(f"   Result: {result[:200]}..." if len(result) > 200 else f"   Result: {result}")
    print(f"\n")
    
    return result

@tool
def get_available_cuisines() -> str:
    """Get all available cuisine types using semantic search."""
    return _knowledge_base.query("What cuisine types are available?")

@tool
def get_available_categories() -> str:
    """Get all available food categories using semantic search."""
    return _knowledge_base.query("What food categories are available?")

@tool
def get_available_restaurants() -> str:
    """Get all available restaurants using semantic search."""
    return _knowledge_base.query("What restaurants are available?")

@tool
def get_dietary_options() -> str:
    """Get all available dietary options using semantic search."""
    return _knowledge_base.query("What dietary options are available?")

# Export the tools
__all__ = [
    "query_database_knowledge",
    "get_available_cuisines", 
    "get_available_categories",
    "get_available_restaurants",
    "get_dietary_options"
]
