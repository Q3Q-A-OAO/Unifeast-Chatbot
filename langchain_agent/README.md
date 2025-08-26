# UniFeast LangChain Agent with Session Memory

A LangChain agent that connects to DynamoDB and PostgreSQL MCP servers with conversational memory for persistent user interactions.

## Features

- **Session Memory**: Maintains conversation history across interactions
- **MCP Server Integration**: Connects to DynamoDB and PostgreSQL via MCP servers
- **User Profile Management**: Store and retrieve user preferences from DynamoDB
- **Food Recommendations**: Search food items from PostgreSQL database
- **OpenAI Integration**: Uses GPT-4-turbo for natural language processing

## Prerequisites

1. **Python 3.11+**
2. **Docker** (for MCP servers)
3. **AWS Credentials** (for DynamoDB and PostgreSQL access)
4. **OpenAI API Key** (for LLM functionality)

## Setup

### 1. Docker Setup (Recommended)

The easiest way to run everything is using Docker:

```bash
# Make sure you're in the langchain_agent directory
cd langchain_agent

# Copy environment template and fill in your API keys
cp env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor

# Start all services (MCP servers + agent)
docker-compose up

# In another terminal, run the agent
docker-compose exec langchain-agent python main.py
```

### 2. Manual Setup (Alternative)

```bash
# Activate the conda environment
conda activate langchain_env

# Verify installation
python test_setup.py
```

### 3. Environment Variables

Copy `env.example` to `.env` and fill in your API keys:

```env
# AWS Credentials (Required for DynamoDB and PostgreSQL MCP servers)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-west-2

# Pinecone Configuration (Required for food search)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=unifeast-food-index
PINECONE_NAMESPACE=__default__

# OpenAI Configuration (Required for LLM)
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL Aurora Configuration (Required for food database)
FOOD_DB_ARN=arn:aws:rds:us-west-2:123456789012:cluster:unifeast-food-db
FOOD_DB_SECRET=arn:aws:secretsmanager:us-west-2:123456789012:secret:unifeast-food-db-secret
FOOD_DB_NAME=postgres
FOOD_DB_READONLY=true
```

### 4. MCP Servers

The agent automatically connects to:
- **DynamoDB MCP Server**: For user profile management
- **PostgreSQL MCP Server**: For food data queries

Both servers run via Docker containers and are managed by docker-compose.

## Usage

### Run the Agent

```bash
python langchain_agent.py
```

### Interactive Testing

```python
import asyncio
from langchain_agent import UniFeastLangChainAgent

async def test_agent():
    agent = UniFeastLangChainAgent()
    await agent.setup_mcp_servers()
    agent.setup_langchain_components()
    
    response = await agent.process_user_input("Hello! I'm new here. Can you help me find food?")
    print(response)
    
    await agent.cleanup()

asyncio.run(test_agent())
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  LangChain Agent │───▶│  OpenAI GPT-4   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Session Memory   │
                       │ (Conversation    │
                       │  BufferMemory)   │
                       └──────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DynamoDB      │◀───│  MCP Adapters    │───▶│   PostgreSQL    │
│ (User Profiles) │    │                  │    │  (Food Data)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. UniFeastLangChainAgent
- Main agent class with session memory
- MCP server integration
- User input processing

### 2. ConversationBufferMemory
- Maintains conversation history
- Configurable token limits
- Persistent across interactions

### 3. MultiServerMCPClient
- Connects to multiple MCP servers
- Automatic tool conversion
- Docker-based server management

### 4. Available Tools

**DynamoDB Tools:**
- `get_item` - Retrieve user preferences
- `put_item` - Update user preferences
- `query` - Search user data
- `scan` - List all users

**PostgreSQL Tools:**
- `run_query` - Execute SQL queries
- Food item searches
- Restaurant data queries

## Example Conversations

```
User: "Hello! I'm new here. Can you help me find food?"
Agent: "Welcome to Imperial College London! I'd be happy to help you find food. 
       Let me get to know your preferences first. Do you have any dietary 
       restrictions or allergies I should know about?"

User: "I have a nut allergy and I'm vegetarian."
Agent: "Thank you for letting me know! I'll update your profile with your 
       nut allergy and vegetarian preferences. Let me search for suitable 
       food options for you..."

User: "What's my current profile?"
Agent: "Based on our conversation, your current profile shows:
       - Dietary restriction: Vegetarian
       - Allergies: Nuts
       - Budget: Not set yet
       Would you like to update any of these preferences?"
```

## Troubleshooting

### Common Issues

1. **Docker Issues**
   - Ensure Docker Desktop is running
   - Check `docker-compose up` output for errors
   - Verify all required images are pulled: `docker images`

2. **MCP Server Connection Failed**
   - Ensure Docker is running
   - Check AWS credentials in `.env` file
   - Verify MCP server images are available: `docker images | grep awslabs`

3. **OpenAI API Errors**
   - Verify API key is set correctly in `.env`
   - Check API key permissions
   - Ensure sufficient credits

4. **Environment Variables Missing**
   - Copy `env.example` to `.env`: `cp env.example .env`
   - Fill in all required API keys
   - Verify `.env` file exists and is properly formatted

### Debug Mode

Enable detailed logging by modifying the logging level in `langchain_agent.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- `langchain==0.3.27`
- `langchain-mcp-adapters==0.1.9`
- `langchain-openai==0.3.28`
- `python-dotenv==1.1.1`
- `openai==1.98.0`
- `mcp>=1.9.2`

## License

This project is part of the UniFeast system for Imperial College London. 