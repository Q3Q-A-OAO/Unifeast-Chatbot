# UniFeast MCP Chatbot

Food recommendation chatbot using Amazon Bedrock Inline Agents and MCP servers.

## Prerequisites

- AWS account with Bedrock access
- AWS CLI installed and configured
- Python 3.11+
- Docker installed and running
- Claude 3.5 Sonnet model access enabled

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start PostgreSQL database**
```bash
docker-compose up -d postgresql
```

3. **Set up AWS credentials**
```bash
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
```

4. **Test database connection**
```bash
# Verify PostgreSQL is running
docker-compose ps
```

## Project Structure

```
mcp-chatbot/
├── src/
│   ├── mcp_servers/     # 4 MCP servers (users, food, crowd, summary)
│   └── inline_agent_sdk.py  # Main SDK
├── config/
│   └── postgresql/      # Database initialization
└── docker-compose.yml   # PostgreSQL only
```

## Next Steps

- Create MCP servers (Phase 2)
- Create InlineAgent SDK (Phase 2)
- Test integration (Phase 3) # Force redeploy - Sun Oct  5 05:39:49 BST 2025
