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
        custom_tools = [search_pinecone]
        
        # Use the existing agent's setup method but skip MCP servers for Railway
        # Just set the tools directly
        chatbot_instance.tools = custom_tools
        
        # The agent will initialize itself when get_chat_response is called
        
        logger.info("✅ Chatbot initialized with existing agent and Pinecone search")
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
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    session_id: str
    timestamp: str
    search_results: Optional[Dict[str, Any]] = None

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

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "chatbot": "healthy" if chatbot_instance else "unhealthy",
        "pinecone": "healthy",  # Add actual health check
        "dynamodb": "healthy"   # Add actual health check
    }
    
    return HealthResponse(
        status="healthy" if all(status == "healthy" for status in services.values()) else "unhealthy",
        timestamp=datetime.now().isoformat(),
        services=services
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    # Use provided user_id or default
    user_id = request.user_id or settings.DEFAULT_USER_ID
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        if not chatbot_instance:
            # Fallback response when chatbot is not available
            response = f"I received your message: '{request.message}'. The full chatbot functionality will be available soon!"
            logger.info(f"Using fallback response for user {user_id}: {request.message}")
        else:
            # Initialize user memory if needed
            if not chatbot_instance.current_user_id:
                chatbot_instance.initialize_user_memory(user_id)
            
            # Process the message using the existing agent
            logger.info(f"Processing message from user {user_id}: {request.message}")
            response = await process_message(request.message, user_id, session_id)
        
        return ChatResponse(
            response=response,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def process_message(message: str, user_id: str, session_id: str) -> str:
    """Process a chat message using the existing MCPToolsTester agent"""
    try:
        # Use the existing agent's get_chat_response method
        response = await chatbot_instance.get_chat_response(message, user_id, session_id)
        return response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return f"I'm sorry, I encountered an error processing your request: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
