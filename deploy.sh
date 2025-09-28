#!/bin/bash
# ECHOSKETCH Deployment Script

echo "🚀 Starting ECHOSKETCH Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "⚠️  Creating .env.production from template..."
    cp .env.example .env.production
    echo "📝 Please update .env.production with your API keys before continuing!"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose --env-file .env.production up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "✅ Checking service status..."
docker-compose ps

# Show logs
echo "📋 Service logs:"
docker-compose logs --tail=50

# Show access URLs
echo ""
echo "🎉 ECHOSKETCH Deployed Successfully!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:5000"
echo "MongoDB: mongodb://localhost:27017"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"