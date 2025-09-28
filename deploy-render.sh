#!/bin/bash
# Render deployment script for ECHOSKETCH

echo "🚀 Starting ECHOSKETCH deployment..."

# Install basic requirements first
echo "📦 Installing core dependencies..."
pip install --no-cache-dir -r requirements-render.txt

# Set up environment
echo "🔧 Setting up environment..."
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# Check health of installation
echo "🏥 Running health check..."
python -c "
import sys
try:
    from flask import Flask
    from services.speech_service import SpeechService
    from services.nlp_service import NLPService
    from services.image_service import ImageService
    print('✅ Core services imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo "✅ Deployment preparation complete!"
echo "🌐 Starting ECHOSKETCH server..."

# Start the application
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload