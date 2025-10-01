"""
Simple Railway API for UniFeast MCP Chatbot
===========================================

This is a minimal FastAPI wrapper that uses your existing langchain_agent
with session-based memory (no persistent storage).
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

# Import your existing modules (unchanged)
from agent import MCPToolsTester, search_pinecone
from config import settings

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="UniFeast MCP Chatbot API",
    description="Food recommendation chatbot - session-based memory only",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
chatbot_instance = None

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup"""
    global chatbot_instance
    
    try:
        logger.info("🚀 STARTING UNIFEAST CONVERSATIONAL AGENT")
        logger.info("=" * 80)
        
        # Validate required settings
        if not settings.validate_required_settings():
            logger.error("❌ Missing required environment variables.")
            raise Exception("Missing required environment variables")
        
        logger.info("✅ Configuration validated successfully")
        
        # Initialize tester (your existing code)
        chatbot_instance = MCPToolsTester()
        
        # Setup MCP servers with custom tools (your existing code)
        custom_tools = [search_pinecone]
        await chatbot_instance.setup_mcp_servers(custom_tools)
        
        logger.info("🎉 Chatbot initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "UniFeast MCP Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "memory": "session-based (not persistent)"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if chatbot_instance else "unhealthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - uses session-based memory only"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        # Use provided user_id or default
        user_id = request.user_id or settings.DEFAULT_USER_ID
        
        # Initialize user memory if needed (session-based only)
        if not chatbot_instance.current_user_id:
            chatbot_instance.initialize_user_memory(user_id)
        
        # Process the message using your existing agent logic
        logger.info(f"📨 Processing: {request.message}")
        
        # Get memory context (session-based)
        memory_context = chatbot_instance.get_memory_context()
        
        # Use your existing agent executor
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Load system prompt
        prompt_file = os.path.join(os.path.dirname(__file__), 'langchain_agent', 'agent', 'prompts', 'system_prompt_with_pinecone.txt')
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()
        
        # Create prompt template with memory support
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(llm, chatbot_instance.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=chatbot_instance.tools, verbose=True)
        
        # Prepare input with memory
        agent_input = {
            "input": request.message,
            **memory_context
        }
        
        # Execute the agent
        result = await agent_executor.ainvoke(agent_input)
        
        # Save conversation to memory (session-based only)
        if chatbot_instance.current_memory:
            chatbot_instance.current_memory.save_context(
                {"input": request.message},
                {"output": result['output']}
            )
        
        return ChatResponse(
            response=result['output'],
            user_id=user_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

