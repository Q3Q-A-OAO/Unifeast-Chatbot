cho "🚀 Setting up UniFeast development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "Download from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/postgresql data/redis data/dynamodb data/pgadmin logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and settings"
fi

# Set up PostgreSQL initialization
echo "🗄️  Setting up PostgreSQL..."
mkdir -p config/postgresql
cat > config/postgresql/init.sql << 'EOF'
-- Create database and user
CREATE DATABASE unifeast_db;
CREATE USER unifeast_user WITH PASSWORD 'unifeast_password';
GRANT ALL PRIVILEGES ON DATABASE unifeast_db TO unifeast_user;

-- Connect to the database
\c unifeast_db;

-- Create tables
CREATE TABLE IF NOT EXISTS unifeast_users (
    user_id VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    user_identity VARCHAR(50) CHECK (user_identity IN ('student', 'staff', 'visitor')),
    dietary_preferences VARCHAR(100),
    period_plan VARCHAR(100),
    milk_allergy BOOLEAN DEFAULT FALSE,
    eggs_allergy BOOLEAN DEFAULT FALSE,
    peanuts_allergy BOOLEAN DEFAULT FALSE,
    tree_nuts_allergy BOOLEAN DEFAULT FALSE,
    shellfish_allergy BOOLEAN DEFAULT FALSE,
    other_allergies TEXT[],
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS unifeast_food (
    id SERIAL PRIMARY KEY,
    restaurant_id VARCHAR(255) NOT NULL,
    record_type VARCHAR(100),
    dish_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    food_type VARCHAR(100),
    cuisine_type VARCHAR(100),
    ingredients TEXT[],
    dietary_tags TEXT[],
    milk_allergy BOOLEAN DEFAULT FALSE,
    eggs_allergy BOOLEAN DEFAULT FALSE,
    peanuts_allergy BOOLEAN DEFAULT FALSE,
    tree_nuts_allergy BOOLEAN DEFAULT FALSE,
    shellfish_allergy BOOLEAN DEFAULT FALSE,
    other_allergens TEXT[],
    student_price DECIMAL(10,2),
    staff_price DECIMAL(10,2),
    serve_time VARCHAR(100),
    location VARCHAR(255),
    restaurant_name VARCHAR(255),
    opening_hours VARCHAR(255),
    accessibility VARCHAR(255),
    notes TEXT,
    available BOOLEAN DEFAULT TRUE,
    embedding_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON unifeast_users(email);
CREATE INDEX IF NOT EXISTS idx_users_identity ON unifeast_users(user_identity);
CREATE INDEX IF NOT EXISTS idx_users_name ON unifeast_users(user_name);
CREATE INDEX IF NOT EXISTS idx_food_restaurant ON unifeast_food(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_food_location ON unifeast_food(location);
CREATE INDEX IF NOT EXISTS idx_food_cuisine ON unifeast_food(cuisine_type);
CREATE INDEX IF NOT EXISTS idx_food_price ON unifeast_food(student_price);
CREATE INDEX IF NOT EXISTS idx_food_available ON unifeast_food(available);
CREATE INDEX IF NOT EXISTS idx_food_dietary_tags ON unifeast_food USING GIN(dietary_tags);
CREATE INDEX IF NOT EXISTS idx_food_ingredients ON unifeast_food USING GIN(ingredients);
CREATE INDEX IF NOT EXISTS idx_food_serve_time ON unifeast_food(serve_time);
CREATE INDEX IF NOT EXISTS idx_food_embedding_id ON unifeast_food(embedding_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO unifeast_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO unifeast_user;
EOF

# Set up Redis configuration
echo "🔴 Setting up Redis..."
mkdir -p config/redis
cat > config/redis/redis.conf << 'EOF'
# Redis configuration for development
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF

# Make scripts executable
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: ./scripts/start.sh"
echo "3. Access services:"
echo "   - MCP Server: http://localhost:8000"
echo "   - pgAdmin: http://localhost:5050 (admin@unifeast.com / admin123)"
echo "   - DynamoDB Admin: http://localhost:8002"
echo ""
echo "📚 Documentation: http://localhost:8000/docs"