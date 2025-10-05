#!/usr/bin/env python3
"""
Test if we can create a simple working tool
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_agent'))

from langchain.tools import tool

@tool("test_tool")
def test_tool(message: str) -> str:
    """A simple test tool."""
    return f"Test tool received: {message}"

# Test the tool directly
if __name__ == "__main__":
    print("Testing tool creation...")
    print(f"Tool: {test_tool}")
    print(f"Tool name: {test_tool.name}")
    print(f"Tool description: {test_tool.description}")
    print("✅ Tool created successfully")
