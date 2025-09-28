# ECHOSKETCH Deployment Script for Windows
# Run this in PowerShell

Write-Host "🚀 Starting ECHOSKETCH Deployment..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env.production exists
if (-not (Test-Path ".env.production")) {
    Write-Host "⚠️  Creating .env.production from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env.production"
    Write-Host "📝 Please update .env.production with your API keys before continuing!" -ForegroundColor Yellow
    exit 1
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
docker-compose down

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Blue
docker-compose --env-file .env.production up -d --build

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Check service status
Write-Host "✅ Checking service status..." -ForegroundColor Green
docker-compose ps

# Show logs
Write-Host "📋 Service logs:" -ForegroundColor Blue
docker-compose logs --tail=50

# Show access URLs
Write-Host ""
Write-Host "🎉 ECHOSKETCH Deployed Successfully!" -ForegroundColor Green
Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "MongoDB: mongodb://localhost:27017" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 To view logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "🛑 To stop: docker-compose down" -ForegroundColor Yellow
Write-Host "🔄 To restart: docker-compose restart" -ForegroundColor Yellow