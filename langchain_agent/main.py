"""
UniFeast LangChain Agent Test
=============================

Test LangChain agent that uses MCP tools to access user profiles and food data.
Agent should intelligently chain tools to provide personalized food recommendations.
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# MCP adapters only
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

# LangChain components
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MCPToolsTester:
    """Simple MCP tools tester - no agent, just direct tool testing."""
    
    def __init__(self):
        """Initialize the MCP tools tester."""
        self.mcp_client = None
        self.tools = []
        
        logger.info("🔧 MCP Tools Tester initialized")
    
    def get_user_id_from_context(self, user_input: str = None) -> str:
        """Extract user ID from context or use default. In the future, this will use Cognito."""
        # TODO: In the future, extract user ID from Cognito authentication
        # For now, use a default test user
        return "test_user_123"
    
    async def setup_mcp_servers(self):
        """Setup MCP server connections for DynamoDB and PostgreSQL."""
        logger.info("🔧 Setting up MCP server connections...")
        
        try:
            # Create MultiServerMCPClient with stdio transport for Docker containers
            self.mcp_client = MultiServerMCPClient({
                "dynamodb": {
                    "transport": "stdio",
                    "command": "docker",
                    "args": [
                        "run", "-i", "--rm",
                        "-e", "AWS_ACCESS_KEY_ID",
                        "-e", "AWS_SECRET_ACCESS_KEY", 
                        "-e", "AWS_REGION",
                        "awslabs/dynamodb-mcp-server:latest",
                        "--table_name", "unifeast-users",
                        "--region", os.getenv("AWS_REGION", "us-west-2")
                    ],
                    "env": {
                        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                        "AWS_REGION": os.getenv("AWS_REGION", "us-west-2")
                    }
                },
                "postgresql": {
                    "transport": "stdio",
                    "command": "docker",
                    "args": [
                        "run", "-i", "--rm",
                        "-e", "AWS_ACCESS_KEY_ID",
                        "-e", "AWS_SECRET_ACCESS_KEY",
                        "-e", "AWS_REGION",
                        "awslabs/postgres-mcp-server:latest",
                        "--resource_arn", os.getenv("FOOD_DB_ARN"),
                        "--secret_arn", os.getenv("FOOD_DB_SECRET"),
                        "--database", os.getenv("FOOD_DB_NAME", "postgres"),
                        "--region", os.getenv("AWS_REGION", "us-west-2"),
                        "--readonly", os.getenv("FOOD_DB_READONLY", "true")
                    ],
                    "env": {
                        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                        "AWS_REGION": os.getenv("AWS_REGION", "us-west-2")
                    }
                }
            })
            # Load tools from MCP servers using proper conversion
            self.tools = await self.mcp_client.get_tools()
            logger.info(f"✅ Loaded {len(self.tools)} tools from MCP servers")
            # Debug: Show what the tools actually look like
            for tool in self.tools:
                if tool.name == 'get_item':
                    logger.info(f"🔍 DEBUG: {tool.name} tool details:")
                    logger.info(f"   - Description: {tool.description}")
                    logger.info(f"   - Args Schema Type: {type(tool.args_schema)}")
                    logger.info(f"   - Args Schema: {tool.args_schema}")
                    if hasattr(tool.args_schema, 'model_json_schema'):
                        logger.info(f"   - Pydantic Schema: {tool.args_schema.model_json_schema()}")
                    logger.info("")
            # Log available tools with detailed information
            logger.info("🔧 Available Tools:")
            for i, tool in enumerate(self.tools, 1):
                logger.info(f"  {i}. {tool.name}")
                logger.info(f"     Description: {tool.description}")
                logger.info(f"     Args Schema: {tool.args_schema}")
                logger.info("")
        except Exception as e:
            logger.error(f"❌ Failed to setup MCP servers: {e}")
            raise
    
      
    async def test_langchain_agent(self):
        """Test LangChain agent with MCP tools."""
        logger.info("🧪 Testing LangChain agent with MCP tools...")
        
        try:
            # Get tools from MCP client
            tools = await self.mcp_client.get_tools()
            logger.info(f"✅ Loaded {len(tools)} MCP tools from client")
            
            # Debug: Show what the agent tools look like
            for tool in tools:
                if tool.name == 'get_item':
                    logger.info(f"🔍 AGENT DEBUG: {tool.name} tool details:")
                    logger.info(f"   - Description: {tool.description}")
                    logger.info(f"   - Args Schema Type: {type(tool.args_schema)}")
                    logger.info(f"   - Args Schema: {tool.args_schema}")
                    if hasattr(tool.args_schema, 'model_json_schema'):
                        logger.info(f"   - Pydantic Schema: {tool.args_schema.model_json_schema()}")
                    logger.info("")
            
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Load the system prompt from file
            with open('system_prompt.txt', 'r') as f:
                system_prompt = f.read()
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent
            agent = create_openai_functions_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Test queries
            test_queries = [
                "Get my user profile",
                "Update my dietary preferences back to vegetarian", 
                "Find spicy Indian food recommendations for me"
            ]
            
            try:
                for query in test_queries:
                    logger.info(f"🔧 Testing query: {query}")
                    try:
                        result = await agent_executor.ainvoke({"input": query})
                        logger.info(f"✅ Agent response: {result['output']}")
                    except Exception as e:
                        logger.error(f"❌ Query failed: {e}")
                    
                    logger.info("-" * 50)
            except Exception as e:
                logger.error(f"❌ LangChain agent test failed: {e}")
                raise
        except Exception as e:
            logger.error(f"❌ LangChain agent setup failed: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup MCP client connections."""
        if self.mcp_client:
            try:
                await self.mcp_client.close()
                logger.info("🧹 MCP client connections closed")
            except Exception as e:
                logger.warning(f"⚠️ MCP client cleanup warning: {e}")

async def main():
    """Main function to test MCP tools directly."""
    tester = None
    
    try:
        logger.info("🚀 STARTING MCP TOOLS TEST")
        logger.info("=" * 80)
        
        # Initialize tester
        tester = MCPToolsTester()
        
        # Setup MCP servers
        await tester.setup_mcp_servers()
        
        # Test LangChain agent with MCP tools
        await tester.test_langchain_agent()
        
        logger.info("🎉 MCP Tools Test completed!")
        
    except Exception as e:
        logger.error(f"❌ MCP tools test failed: {e}")
        raise
        
    finally:
        # Cleanup
        if tester:
            await tester.cleanup()
        logger.info("🎯 All connections closed")

if __name__ == "__main__":
    asyncio.run(main()) 