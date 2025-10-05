"""
FastAPI wrapper for UniFeast MCP Chatbot
========================================

This FastAPI application wraps the MCP chatbot functionality
to provide a REST API for frontend integration.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Configure structured logging to reduce volume
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set environment variable to reduce Railway log volume
os.environ["PYTHONUNBUFFERED"] = "0"

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'langchain_agent'))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Import your existing modules
from agent.mcp_tester import MCPToolsTester
from agent.pinecone_search import search_pinecone
from config.settings import settings
from knowledge_base.simple_knowledge_base import (
    query_database_knowledge,
    get_available_cuisines,
    get_available_categories,
    get_available_restaurants,
    get_dietary_options
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global chatbot_instance
    
    # Startup
    logger.info("🚀 Starting UniFeast MCP Chatbot API")
    try:
        # Initialize the existing MCPToolsTester agent
        chatbot_instance = MCPToolsTester()
        custom_tools = [
            search_pinecone,
            query_database_knowledge,
            get_available_cuisines,
            get_available_categories,
            get_available_restaurants,
            get_dietary_options
        ]
        
        # Try MCP servers first, fallback to Pinecone only
        try:
            await chatbot_instance.setup_mcp_servers(custom_tools)
            logger.info("✅ Chatbot initialized with full MCP server access")
        except Exception as mcp_error:
            logger.warning(f"⚠️ MCP servers failed: {mcp_error}")
            logger.info("🔄 Using Pinecone search only")
            # Set tools directly for Pinecone-only mode
            chatbot_instance.tools = custom_tools
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        logger.info("🔄 Continuing without chatbot - using basic functionality")
        # Don't raise the exception - allow API to start with limited functionality
        chatbot_instance = None
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down chatbot")
    if chatbot_instance:
        await chatbot_instance.cleanup()

# Create FastAPI app
app = FastAPI(
    title="UniFeast MCP Chatbot API",
    description="Food recommendation chatbot using Amazon Bedrock Inline Agents and MCP servers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserProfile(BaseModel):
    user_id: str
    user_name: str
    email: str
    user_identity: str  # "student" | "staff"
    dietary_preferences: str
    period_plan: str
    budget: float
    milk_allergy: bool
    eggs_allergy: bool
    peanuts_allergy: bool
    tree_nuts_allergy: bool
    shellfish_allergy: bool
    other_allergies: list[str]
    created_at: str
    updated_at: str

class ChatRequest(BaseModel):
    message: str
    cognito_id: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    user_id: Optional[str] = None  # Keep for backward compatibility
    session_id: Optional[str] = None

class FoodCard(BaseModel):
    dish_name: str
    restaurant_name: str
    description: str
    category: str
    food_type: str
    cuisine_type: str
    ingredients: list[str]
    dietary_tags: list[str]
    milk_allergy: bool
    eggs_allergy: bool
    peanuts_allergy: bool
    tree_nuts_allergy: bool
    shellfish_allergy: bool
    other_allergens: list[str]
    student_price: float
    staff_price: float
    serve_time: str
    location: str
    available: bool
    image_url: Optional[str] = None
    score: float

class RestaurantCard(BaseModel):
    restaurant_name: str
    cuisine_type: str
    location: str
    description: Optional[str] = None
    available_food_types: Optional[list[str]] = None
    operating_hours: Optional[str] = None
    price_range: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None

class SearchMetadata(BaseModel):
    total_results: int
    search_query: str
    filters_applied: list[str]
    user_identity: str
    budget_limit: float

class ChatResponse(BaseModel):
    text_bubble: str
    ui_cards: list[FoodCard]
    restaurant_cards: Optional[list[RestaurantCard]] = None
    user_id: str
    session_id: str
    timestamp: str
    search_metadata: SearchMetadata

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "UniFeast MCP Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

async def check_pinecone_health() -> str:
    """Check if Pinecone connection is healthy"""
    try:
        # Check if Pinecone tools are available in the chatbot instance
        if chatbot_instance and hasattr(chatbot_instance, 'tools'):
            pinecone_tools = [tool for tool in chatbot_instance.tools if 'pinecone' in str(tool).lower()]
            if pinecone_tools:
                return "healthy"
        return "unhealthy"
    except Exception as e:
        logger.error(f"Pinecone health check failed: {e}")
        return "unhealthy"

async def check_dynamodb_health() -> str:
    """Check if DynamoDB connection is healthy"""
    try:
        # Check if MCP DynamoDB tools are available
        if chatbot_instance and hasattr(chatbot_instance, 'tools'):
            dynamodb_tools = [tool for tool in chatbot_instance.tools if 'dynamodb' in str(tool).lower()]
            if dynamodb_tools:
                return "healthy"
        return "unhealthy"
    except Exception as e:
        logger.error(f"DynamoDB health check failed: {e}")
        return "unhealthy"

async def check_postgresql_health() -> str:
    """Check if PostgreSQL connection is healthy"""
    try:
        # Check if MCP PostgreSQL tools are available
        if chatbot_instance and hasattr(chatbot_instance, 'tools'):
            postgres_tools = [tool for tool in chatbot_instance.tools if 'postgres' in str(tool).lower()]
            if postgres_tools:
                return "healthy"
        return "unhealthy"
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return "unhealthy"

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with real connection tests"""
    # Check each service individually
    chatbot_status = "healthy" if chatbot_instance else "unhealthy"
    pinecone_status = await check_pinecone_health()
    dynamodb_status = await check_dynamodb_health()
    postgresql_status = await check_postgresql_health()
    
    services = {
        "chatbot": chatbot_status,
        "pinecone": pinecone_status,
        "dynamodb": dynamodb_status,
        "postgresql": postgresql_status
    }
    
    # Overall status is healthy only if all services are healthy
    overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        services=services
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    print(f"🚀 CHAT REQUEST: {request.message}")
    
    # Use provided user_id or cognito_id or default
    user_id = request.user_id or request.cognito_id or settings.DEFAULT_USER_ID
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"👤 User: {user_id}, Session: {session_id}")
    
    # Log user profile information for debugging
    if request.user_profile:
        logger.info(f"User profile received: {request.user_profile.user_identity}, Budget: {request.user_profile.budget}, Dietary: {request.user_profile.dietary_preferences}")
        print(f"👤 User profile: {request.user_profile.user_identity}, Budget: {request.user_profile.budget}")
    else:
        logger.info(f"No user profile provided, using default settings")
        print(f"👤 No user profile provided")
    
    try:
        if not chatbot_instance:
            # Fallback response when chatbot is not available
            fallback_response = {
                "text_bubble": f"I received your message: '{request.message}'. The full chatbot functionality will be available soon!",
                "ui_cards": [],
                "search_metadata": {
                    "total_results": 0,
                    "search_query": request.message,
                    "filters_applied": [],
                    "user_identity": "student",
                    "budget_limit": 0.0
                }
            }
            logger.info(f"Using fallback response for user {user_id}: {request.message}")
        else:
            # Initialize user memory if needed
            if not chatbot_instance.current_user_id:
                chatbot_instance.initialize_user_memory(user_id)
            
            # Process the message using the existing agent
            logger.info(f"Processing message from user {user_id}: {request.message}")
            fallback_response = await process_message(request.message, user_id, session_id, request.user_profile)
        
        # Create structured response
        return ChatResponse(
            text_bubble=fallback_response["text_bubble"],
            ui_cards=fallback_response["ui_cards"],
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            search_metadata=fallback_response["search_metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def process_message(message: str, user_id: str, session_id: str, user_profile: Optional[UserProfile] = None) -> dict:
    """Process a chat message using the existing MCPToolsTester agent"""
    print(f"🤖 PROCESSING MESSAGE: {message}")
    
    try:
        # Enhance message with user profile context if available
        enhanced_message = message
        if user_profile:
            # Add user profile context to the message for the agent
            profile_context = f"""
User Profile Context:
- Identity: {user_profile.user_identity}
- Dietary Preferences: {user_profile.dietary_preferences}
- Budget Limit: £{user_profile.budget}
- Allergies: {'Milk' if user_profile.milk_allergy else ''} {'Eggs' if user_profile.eggs_allergy else ''} {'Peanuts' if user_profile.peanuts_allergy else ''} {'Tree Nuts' if user_profile.tree_nuts_allergy else ''} {'Shellfish' if user_profile.shellfish_allergy else ''} {'Other: ' + ', '.join(user_profile.other_allergies) if user_profile.other_allergies else ''}

User Query: {message}
"""
            enhanced_message = profile_context
            print(f"👤 Enhanced message with profile context")
        
        print(f"🤖 Calling agent with message length: {len(enhanced_message)}")
        # Use the existing agent's get_chat_response method
        response = await chatbot_instance.get_chat_response(enhanced_message, user_id, session_id)
        print(f"✅ Agent response received, length: {len(response)}")
        print(f"📝 Response preview: {response[:300]}...")
        
        # Try to parse as JSON first (new structured format)
        try:
            import json
            parsed_response = json.loads(response)
            return parsed_response
        except json.JSONDecodeError:
            # Fallback to old format - create structured response
            return {
                "text_bubble": response,
                "ui_cards": [],
                "search_metadata": {
                    "total_results": 0,
                    "search_query": message,
                    "filters_applied": [],
                    "user_identity": "student",
                    "budget_limit": 0.0
                }
            }
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {
            "text_bubble": f"I'm sorry, I encountered an error processing your request: {str(e)}",
            "ui_cards": [],
            "search_metadata": {
                "total_results": 0,
                "search_query": message,
                "filters_applied": [],
                "user_identity": "student",
                "budget_limit": 0.0
            }
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
