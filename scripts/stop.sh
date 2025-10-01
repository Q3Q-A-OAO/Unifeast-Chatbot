#!/bin/bash

echo "🔄 Resetting UniFeast development environment..."

# Stop services
docker-compose down

# Remove all data
echo "🗑️  Removing all data..."
rm -rf data/postgresql/*
rm -rf data/redis/*
rm -rf data/dynamodb/*
rm -rf data/pgadmin/*
rm -rf logs/*

# Remove containers and images
echo "🧹 Cleaning up containers and images..."
docker-compose down --volumes --remove-orphans
docker system prune -f

echo "✅ Environment reset complete"
echo "📝 Run ./scripts/setup.sh to set up again"
```

## 📋 Team Member Setup Instructions

### **For New Team Members:**

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd unifeast-mcp
   ```

2. **Run setup script:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure environment:**
   ```bash
   # Edit .env file with your API keys
   nano .env
   ```

4. **Start development environment:**
   ```bash
   ./scripts/start.sh
   ```

5. **Access services:**
   - MCP Server: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - pgAdmin: http://localhost:5050
   - DynamoDB Admin: http://localhost:8002

### **For Existing Team Members:**

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update environment:**
   ```bash
   ./scripts/stop.sh
   ./scripts/start.sh
   ```

## 🔧 Development Workflow

### **Daily Development:**
```bash
# Start environment
./scripts/start.sh

# Make changes to code in src/
# Code auto-reloads thanks to uvicorn --reload

# View logs
docker-compose logs -f mcp-server

# Stop environment
./scripts/stop.sh
```

### **Database Management:**
```bash
# Access PostgreSQL via pgAdmin
# URL: http://localhost:5050
# Email: admin@unifeast.com
# Password: admin123

# Or via command line
docker-compose exec postgresql psql -U unifeast_user -d unifeast_db
```

### **Testing:**
```bash
# Run tests
docker-compose exec mcp-server pytest

# Run with coverage
docker-compose exec mcp-server pytest --cov=src
```

## 📊 Monitoring & Debugging

### **Service Status:**
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f mcp-server
```

### **Database Connections:**
```bash
# PostgreSQL
docker-compose exec postgresql psql -U unifeast_user -d unifeast_db

# Redis
docker-compose exec redis redis-cli

# DynamoDB
docker-compose exec dynamodb-local aws dynamodb list-tables --endpoint-url http://localhost:8000