"""
UniFeast LangChain Agent Entry Point
====================================

Main entry point for the UniFeast conversational agent.
Handles initialization and starts the interactive conversation.
"""

import asyncio
import logging

# Local modules
from memory import MemoryManager
from agent import MCPToolsTester, search_pinecone
from config import settings
# TEMPORARILY DISABLED KNOWLEDGE BASE TOOLS - TESTING WITHOUT ANY KNOWLEDGE BASE
# from knowledge_base.simple_knowledge_base import (
#     query_database_knowledge,
#     get_available_cuisines,
#     get_available_categories,
#     get_available_food_types,
#     get_available_restaurants,
#     get_dietary_options
# )

# Version information
__version__ = "1.0.0"
__author__ = "UniFeast Team"

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)




async def main():
    """Main function to start the conversational agent."""
    tester = None
    
    try:
        logger.info("🚀 STARTING UNIFEAST CONVERSATIONAL AGENT")
        logger.info("=" * 80)
        logger.info(f"📦 Version: {__version__}")
        logger.info(f"👥 Author: {__author__}")
        logger.info("=" * 80)
        
        # Validate required settings
        if not settings.validate_required_settings():
            logger.error("❌ Missing required environment variables. Please check your .env file.")
            return
        
        logger.info("✅ Configuration validated successfully")
        
        # Initialize tester
        tester = MCPToolsTester()
        
        # Setup MCP servers with custom tools - ONLY SEARCH_PINECONE (NO KNOWLEDGE BASE)
        custom_tools = [
            search_pinecone
        ]
        await tester.setup_mcp_servers(custom_tools)
        
        # Start interactive conversation
        await tester.start_conversation()
        
        logger.info("🎉 Conversation completed!")
        
    except KeyboardInterrupt:
        logger.info("👋 Agent stopped by user")
        
    except Exception as e:
        logger.error(f"❌ Agent failed: {e}")
        raise
        
    finally:
        # Cleanup
        if tester:
            await tester.cleanup()
        logger.info("🎯 All connections closed")

if __name__ == "__main__":
    asyncio.run(main()) 