"""
Ultra Simple Railway API for UniFeast MCP Chatbot
================================================

This is a minimal FastAPI wrapper that works reliably on Railway.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the langchain_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="UniFeast MCP Chatbot API",
    description="Food recommendation chatbot - simple version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - simplified version"""
    try:
        # For now, return a simple response to test the API
        response_text = f"Hello! I received your message: '{request.message}'. The full chatbot functionality will be available soon!"
        
        return ChatResponse(
            response=response_text,
            user_id=request.user_id or "test_user",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"I'm sorry, I encountered an error: {str(e)}",
            user_id=request.user_id or "test_user",
            timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
