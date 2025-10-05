"""
MCP Tools Tester Module
=======================

Handles MCP server connections and conversational agent setup.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# MCP adapters
from langchain_mcp_adapters.client import MultiServerMCPClient

# LangChain components
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Local modules
from memory import MemoryManager
from config import settings

logger = logging.getLogger(__name__)


class MCPToolsTester:
    """Simple MCP tools tester - no agent, just direct tool testing."""
    
    def __init__(self):
        """Initialize the MCP tools tester."""
        self.mcp_client = None
        self.tools = []
        self.memory_manager = MemoryManager()
        self.current_user_id = None
        self.current_session_id = None
        self.current_memory = None
        
        logger.info("🔧 MCP Tools Tester initialized")
    
    def get_user_id_from_context(self, user_input: str = None) -> str:
        """Extract user ID from context or use default. In the future, this will use Cognito."""
        # TODO: In the future, extract user ID from Cognito authentication
        # For now, use a default test user
        return settings.DEFAULT_USER_ID
    
    def initialize_user_memory(self, user_id: str):
        """Initialize memory for a specific user."""
        self.current_user_id = user_id
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_memory = self.memory_manager.get_memory_for_user(
            user_id, self.current_session_id
        )
        logger.info(f"🧠 Initialized memory for user: {user_id}")
        
        # Load previous conversations if any
        conversations = self.memory_manager.get_user_conversations(user_id)
        if conversations:
            logger.info(f"📚 Found {len(conversations)} previous conversations")
    
    def get_memory_context(self) -> Dict[str, Any]:
        """Get memory context for the agent."""
        if self.current_memory:
            return self.current_memory.load_memory_variables({})
        return {}
    
    async def setup_mcp_servers(self, custom_tools=None):
        """Setup MCP server connections for DynamoDB and PostgreSQL."""
        logger.info("🔧 Setting up MCP server connections...")
        
        try:
            # Create MultiServerMCPClient with stdio transport for installed MCP servers
            self.mcp_client = MultiServerMCPClient({
                "dynamodb": {
                    "transport": "stdio",
                    "command": "python",
                    "args": [
                        "-m", "mcp_server_dynamodb",
                        "--table_name", settings.DYNAMODB_TABLE_NAME,
                        "--region", settings.AWS_REGION
                    ],
                    "env": {
                        "AWS_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
                        "AWS_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
                        "AWS_REGION": settings.AWS_REGION
                    }
                },
                "postgresql": {
                    "transport": "stdio",
                    "command": "python",
                    "args": [
                        "-m", "mcp_server_postgres",
                        "--resource_arn", settings.FOOD_DB_ARN or "",
                        "--secret_arn", settings.FOOD_DB_SECRET or "",
                        "--database", settings.FOOD_DB_NAME,
                        "--region", settings.AWS_REGION,
                        "--readonly", settings.FOOD_DB_READONLY
                    ],
                    "env": {
                        "AWS_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
                        "AWS_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
                        "AWS_REGION": settings.AWS_REGION
                    }
                }
            })
            # Load tools from MCP servers using proper conversion
            mcp_tools = await self.mcp_client.get_tools()
            logger.info(f"✅ Loaded {len(mcp_tools)} tools from MCP servers")
            
            # Add custom tools if provided
            if custom_tools:
                self.tools = mcp_tools + custom_tools
                logger.info(f"✅ Added {len(custom_tools)} custom tools")
            else:
                self.tools = mcp_tools
                
            logger.info(f"✅ Total tools available: {len(self.tools)}")
            
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
    
    async def start_conversation(self, system_prompt_file: str = None):
        """Start interactive conversation with the agent."""
        logger.info("🤖 Starting UniFeast Conversational Agent...")
        
        try:
            # Use the combined tools (MCP + custom) from setup
            tools = self.tools
            logger.info(f"✅ Using {len(tools)} combined tools (MCP + custom)")
            
            # Initialize LLM
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Load the system prompt from file
            prompt_file = system_prompt_file or settings.SYSTEM_PROMPT_FILE
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
            agent = create_openai_functions_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,  # Enable verbose logging for debugging
                max_iterations=3,  # Reduce iterations to prevent loops
                max_execution_time=60,  # Increase time limit to 60 seconds
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                early_stopping_method="force"  # Force stop on iteration limit
            )
            
            # Get user ID for this session
            user_id = self.get_user_id_from_context()
            logger.info(f"👤 User ID: {user_id}")
            
            # Initialize memory for this user
            self.initialize_user_memory(user_id)
            
            # Welcome message
            print("\n" + "="*60)
            print("🤖 UniFeast Conversational Agent")
            print("="*60)
            print("Hello! I'm your UniFeast dining assistant.")
            print("I can help you with:")
            print("• Managing dietary preferences and allergies")
            print("• Finding food recommendations")
            print("• Updating your user profile")
            print("• Answering questions about campus dining")
            print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
            print("="*60)
            
            # Interactive conversation loop
            while True:
                try:
                    # Get user input
                    user_input = input("\nYou: ").strip()
                    
                    # Check for exit commands
                    if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                        print("\n👋 Goodbye! Thanks for using UniFeast Assistant!")
                        break
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Process with agent (including memory context)
                    logger.info(f"📨 Processing: {user_input}")
                    
                    # Get memory context
                    memory_context = self.get_memory_context()
                    
                    # Prepare input with memory
                    agent_input = {
                        "input": user_input,
                        **memory_context
                    }
                    
                    result = await agent_executor.ainvoke(agent_input)
                    
                    # Save conversation to memory
                    if self.current_memory:
                        self.current_memory.save_context(
                            {"input": user_input},
                            {"output": result['output']}
                        )
                    
                    # Display response
                    print(f"\n🤖 Assistant: {result['output']}")
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye! Thanks for using UniFeast Assistant!")
                    break
                except Exception as e:
                    logger.error(f"❌ Error processing input: {e}")
                    print(f"\n❌ Sorry, I encountered an error: {str(e)}")
                    print("Please try again or type 'quit' to exit.")
            
        except Exception as e:
            logger.error(f"❌ Conversation setup failed: {e}")
            raise
    
    async def get_chat_response(self, message: str, user_id: str, session_id: str) -> str:
        """Get a chat response from the MCP chatbot."""
        try:
            # Initialize user memory if needed
            if not self.current_memory or self.current_user_id != user_id:
                self.current_user_id = user_id
                self.initialize_user_memory(user_id)
            
            # Setup MCP servers if not already done
            if not self.mcp_client:
                # SEARCH_PINECONE TOOL ONLY (knowledge base info in system prompt)
                try:
                    from agent.pinecone_search import search_pinecone
                    custom_tools = [search_pinecone]
                except ImportError:
                    custom_tools = []
                await self.setup_mcp_servers(custom_tools)
            
            # Create agent using the same logic as start_conversation
            tools = self.tools
            logger.info(f"✅ Using {len(tools)} tools for chat response")
            
            # Initialize LLM
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Load the system prompt from file
            prompt_file = settings.SYSTEM_PROMPT_FILE
            # Make path absolute to work in Railway container
            if not os.path.isabs(prompt_file):
                # In Railway, the working directory is /app, so the correct path is /app/langchain_agent/agent/prompts/
                prompt_file = os.path.join("/app", "langchain_agent", "agent", "prompts", "system_prompt_with_pinecone.txt")
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
            agent = create_openai_functions_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,  # Enable verbose logging for debugging
                max_iterations=3,  # Reduce iterations to prevent loops
                max_execution_time=60,  # Increase time limit to 60 seconds
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                early_stopping_method="force"  # Force stop on iteration limit
            )
            
            # Get memory context
            memory_context = self.get_memory_context()
            
            # Prepare input with memory
            agent_input = {
                "input": message,
                **memory_context
            }
            
            # Get response from agent
            print(f"🤖 INVOKING AGENT with input: {agent_input}")
            result = await agent_executor.ainvoke(agent_input)
            print(f"🤖 AGENT RESULT: {result}")
            
            # Check for intermediate steps to debug loops
            if 'intermediate_steps' in result:
                print(f"🔄 INTERMEDIATE STEPS COUNT: {len(result['intermediate_steps'])}")
                for i, step in enumerate(result['intermediate_steps']):
                    print(f"🔄 STEP {i}: {step}")
            
            # Save conversation to memory
            if self.current_memory:
                self.current_memory.save_context(
                    {"input": message},
                    {"output": result['output']}
                )
            
            return result['output']
            
        except Exception as e:
            logger.error(f"❌ Error getting chat response: {e}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def cleanup(self):
        """Cleanup MCP client connections."""
        if self.mcp_client:
            try:
                await self.mcp_client.close()
                logger.info("🧹 MCP client connections closed")
            except Exception as e:
                logger.warning(f"⚠️ MCP client cleanup warning: {e}")
