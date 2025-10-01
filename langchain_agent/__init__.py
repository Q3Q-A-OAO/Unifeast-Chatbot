"""
UniFeast LangChain Agent Package
================================

A conversational AI agent for UniFeast food recommendations.
Provides intelligent food search, user preference management, and personalized recommendations.
"""

__version__ = "1.0.0"
__author__ = "UniFeast Team"
__description__ = "Conversational AI agent for food recommendations"

# Import main components for easy access
from .agent import MCPToolsTester, search_pinecone
from .memory import MemoryManager
from .config import settings

__all__ = [
    'MCPToolsTester',
    'search_pinecone', 
    'MemoryManager',
    'settings',
    '__version__',
    '__author__',
    '__description__'
]
