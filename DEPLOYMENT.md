# UniFeast MCP Chatbot - Railway Deployment Guide

## Overview

This guide explains how to deploy your MCP chatbot as a FastAPI service on Railway, addressing your concerns about Docker and database management.

## Docker Requirements - ANSWERED ✅

**You do NOT need to run Docker locally for Railway deployment!** Here's why:

1. **Railway handles Docker for you** - If you use the Dockerfile approach, Railway builds and runs the container
2. **Alternative: Direct Python deployment** - Railway can run your Python app directly without Docker
3. **Database services** - Railway provides managed PostgreSQL/Redis services

## Deployment Options

### Option 1: Direct Python Deployment (Recommended)
- Railway detects your Python app and runs it directly
- No Docker required on your local machine
- Faster deployment and easier debugging

### Option 2: Dockerfile Deployment
- Railway builds and runs your Docker container
- You don't need Docker running locally
- More control over the environment

## Step-by-Step Deployment

### 1. Prepare Your Repository

Your project structure is now ready:
```
mcp-chatbot/
├── api/
│   └── main.py              # FastAPI application
├── langchain_agent/         # Your existing chatbot code
├── railway.json             # Railway configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Optional Docker deployment
└── .env                    # Environment variables (don't commit this)
```

### 2. Set Up Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub repository

### 3. Deploy to Railway

#### Method A: From GitHub (Easiest)
1. Push your code to GitHub
2. In Railway dashboard, click "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the configuration

#### Method B: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 4. Configure Environment Variables

In Railway dashboard, add these environment variables:
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-west-2
DYNAMODB_TABLE_NAME=unifeast-users
PINECONE_INDEX_NAME=unifeast-food-index
PINECONE_NAMESPACE=__default__
```

### 5. Add Database Services (Optional)

For persistent memory storage:
1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL" or "Redis"
3. Railway will provide connection strings automatically

## API Endpoints

Once deployed, your API will have these endpoints:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat` - Main chat endpoint
- `POST /search/food` - Direct food search

### Example Usage

```bash
# Health check
curl https://your-app.railway.app/health

# Chat with the bot
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want spicy Indian food"}'

# Direct food search
curl -X POST "https://your-app.railway.app/search/food?query=pasta&top_k=5"
```

## Testing Locally

Before deploying, test your API locally:

```bash
# Start the API server
cd api
python -m uvicorn main:app --reload

# In another terminal, run tests
python test_api.py
```

## Memory Management

Your chatbot's memory will be stored in:
- **Local SQLite files** (if using default memory manager)
- **Railway PostgreSQL** (if you add a database service)
- **Session-based memory** (temporary, per request)

## Cost Considerations

Railway pricing:
- **Hobby plan**: $5/month for basic usage
- **Pro plan**: $20/month for production
- **Database services**: Additional cost per service

## Troubleshooting

### Common Issues

1. **Docker not found**: Use the direct Python deployment method
2. **Memory issues**: Add a PostgreSQL service for persistent storage
3. **API keys**: Ensure all environment variables are set in Railway
4. **MCP server errors**: Check that AWS credentials are correct

### Logs

View logs in Railway dashboard:
1. Go to your service
2. Click on "Deployments"
3. Click on the latest deployment
4. View logs in real-time

## Next Steps

1. **Deploy to Railway** using one of the methods above
2. **Test the API** using the provided test script
3. **Integrate with frontend** using the API endpoints
4. **Monitor usage** in Railway dashboard
5. **Scale as needed** based on usage patterns

## Support

- Railway Documentation: https://docs.railway.com
- FastAPI Documentation: https://fastapi.tiangolo.com
- Your chatbot logs: Available in Railway dashboard

