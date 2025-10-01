#!/bin/bash

echo "🚀 Starting UniFeast development environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./scripts/setup.sh first."
    exit 1
fi

# Start all services
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check MCP Server
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ MCP Server is running"
else
    echo "❌ MCP Server is not responding"
fi

# Check PostgreSQL
if docker-compose exec -T postgresql pg_isready -U unifeast_user -d unifeast_db &> /dev/null; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is not responding"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not responding"
fi

echo ""
echo "🎉 All services are running!"
echo ""
echo "📋 Service URLs:"
echo "   - MCP Server: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - pgAdmin: http://localhost:5050"
echo "   - DynamoDB Admin: http://localhost:8002"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop services: ./scripts/stop.sh"