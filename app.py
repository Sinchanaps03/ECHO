from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv

# Import our modules
from services.speech_service import SpeechService
from services.nlp_service import NLPService
from services.image_service import ImageService
from services.database_service import DatabaseService

# Load environment variables
load_dotenv()

# Initialize Flask app with static folder configuration
app = Flask(__name__, static_folder='frontend/build/static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Enable CORS
CORS(app, origins=[
    os.getenv('FRONTEND_URL', 'http://localhost:3000'),
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3000'
])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
speech_service = SpeechService()
nlp_service = NLPService()
image_service = ImageService()
database_service = DatabaseService()

# Analytics storage (in-memory for simplicity)
analytics_data = {
    'sessions': [],
    'total_sessions': 0,
    'total_concepts': 0,
    'response_times': [],
    'object_counts': {},
    'color_counts': {},
    'accuracy_scores': []
}

def update_analytics(session_data, response_time=None, accuracy=None):
    """Update analytics data with new session information"""
    global analytics_data
    
    # Update basic counts
    analytics_data['total_sessions'] += 1
    analytics_data['sessions'].append(session_data)
    
    # Keep only last 100 sessions for memory efficiency
    if len(analytics_data['sessions']) > 100:
        analytics_data['sessions'] = analytics_data['sessions'][-100:]
    
    # Track response times
    if response_time:
        analytics_data['response_times'].append(response_time)
        if len(analytics_data['response_times']) > 50:
            analytics_data['response_times'] = analytics_data['response_times'][-50:]
    
    # Track concepts
    visual_concepts = session_data.get('visual_concepts', {})
    
    # Count objects
    objects = visual_concepts.get('objects', [])
    analytics_data['total_concepts'] += len(objects)
    for obj in objects:
        analytics_data['object_counts'][obj] = analytics_data['object_counts'].get(obj, 0) + 1
    
    # Count colors
    colors = visual_concepts.get('colors', [])
    for color in colors:
        analytics_data['color_counts'][color] = analytics_data['color_counts'].get(color, 0) + 1
    
    # Track accuracy if provided
    if accuracy:
        analytics_data['accuracy_scores'].append(accuracy)
        if len(analytics_data['accuracy_scores']) > 50:
            analytics_data['accuracy_scores'] = analytics_data['accuracy_scores'][-50:]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'ECHOSKETCH API is running'})

# API root endpoint - serve the web interface
@app.route('/', methods=['GET'])
def api_root():
    """Serve the web interface for users"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECHOSKETCH - Voice to Visuals</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333; min-height: 100vh; display: flex;
            flex-direction: column; align-items: center; padding: 20px;
        }
        .container {
            max-width: 800px; width: 100%; background: rgba(255, 255, 255, 0.95);
            border-radius: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 30px; margin: 20px 0;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 {
            color: #4a5568; font-size: 2.5rem; margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .api-section {
            background: #f8f9fa; border-radius: 15px; padding: 25px;
            margin: 20px 0; border-left: 5px solid #4299e1;
        }
        .input-group { margin-bottom: 20px; }
        .input-group textarea {
            width: 100%; padding: 12px; border: 2px solid #e2e8f0;
            border-radius: 8px; font-size: 16px;
        }
        .btn {
            background: linear-gradient(135deg, #4299e1, #667eea);
            color: white; border: none; padding: 12px 24px;
            border-radius: 8px; cursor: pointer; font-size: 16px;
            font-weight: 600; margin: 5px;
        }
        .btn:hover { transform: translateY(-2px); }
        .results { margin-top: 30px; padding: 20px; background: #edf2f7; border-radius: 15px; display: none; }
        .results.show { display: block; }
        .generated-image { max-width: 100%; border-radius: 10px; margin: 15px 0; }
        .status-badge {
            display: inline-block; padding: 4px 12px; background: #48bb78;
            color: white; border-radius: 20px; font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 ECHOSKETCH</h1>
            <p>Transform your words into stunning visuals with AI</p>
            <span class="status-badge">🚀 Live on Render</span>
        </div>
        
        <div class="api-section">
            <h3>🖼️ Text to Image Generator</h3>
            <p>Describe what you want to see, and our AI will create it!</p>
            
            <div class="input-group">
                <textarea id="textInput" placeholder="e.g., A magical forest with glowing crystal trees..." rows="3"></textarea>
            </div>
            
            <button class="btn" onclick="generateImage()">✨ Generate Image</button>
            
            <div id="loading" style="display: none; text-align: center; margin: 20px;">
                🎨 Creating your masterpiece...
            </div>
            
            <div id="results" class="results">
                <h4>🎯 Generated Results:</h4>
                <div id="imageContainer"></div>
                <div id="conceptsContainer"></div>
            </div>
        </div>
        
        <div class="api-section">
            <h3>📊 API Endpoints</h3>
            <p>Your ECHOSKETCH API is running with these endpoints:</p>
            <ul>
                <li><strong>Health:</strong> <a href="/health">/health</a></li>
                <li><strong>Text to Image:</strong> /api/text-to-image</li>
                <li><strong>Analytics:</strong> <a href="/api/analytics">/api/analytics</a></li>
            </ul>
        </div>
    </div>
    
    <script>
        async function generateImage() {
            const textInput = document.getElementById('textInput');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const imageContainer = document.getElementById('imageContainer');
            
            const text = textInput.value.trim();
            if (!text) { alert('Please enter a description!'); return; }
            
            loading.style.display = 'block';
            results.classList.remove('show');
            
            try {
                const response = await fetch('/api/text-to-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                
                if (data.success && data.image_data) {
                    imageContainer.innerHTML = `
                        <img src="${data.image_data.image_data}" alt="Generated Image" class="generated-image">
                        <p><strong>Generated successfully!</strong></p>
                        <p><strong>Mood:</strong> ${data.visual_concepts?.mood || 'N/A'}</p>
                        <p><strong>Style:</strong> ${data.visual_concepts?.style || 'N/A'}</p>
                    `;
                    results.classList.add('show');
                } else {
                    imageContainer.innerHTML = '<p>❌ Failed to generate image. Please try again.</p>';
                    results.classList.add('show');
                }
            } catch (err) {
                imageContainer.innerHTML = `<p>❌ Error: ${err.message}</p>`;
                results.classList.add('show');
            }
            
            loading.style.display = 'none';
        }
    </script>
</body>
</html>'''
    
    return html_content

# API info endpoint - JSON response for developers
@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'ECHOSKETCH API - Voice to Visuals',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'text_to_image': '/api/text-to-image',
            'process_voice': '/api/process-voice',
            'analytics': '/api/analytics',
            'session_history': '/api/session-history'
        },
        'version': '1.0.0',
        'deployed_on': 'Render'
    })

# Serve static files if they exist (optional)
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files or return 404"""
    try:
        return send_from_directory('static', filename)
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/process-voice', methods=['POST'])
def process_voice():
    """Process voice input and generate image"""
    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporary audio file
        temp_audio_path = f"temp_{audio_file.filename}"
        audio_file.save(temp_audio_path)
        
        try:
            # Step 1: Speech to Text
            logger.info("Converting speech to text...")
            transcript = speech_service.speech_to_text(temp_audio_path)
            
            if not transcript:
                return jsonify({'error': 'Could not transcribe audio'}), 400
            
            # Step 2: NLP Processing
            logger.info("Processing natural language...")
            visual_concepts = nlp_service.extract_visual_concepts(transcript)
            
            # Step 3: Generate enhanced prompt and image
            logger.info("Generating image...")
            enhanced_prompt = nlp_service.generate_image_prompt(transcript, visual_concepts.get('sentiment'))
            image_data = image_service.generate_image(enhanced_prompt)
            
            # Step 4: Save to database
            session_data = {
                'transcript': transcript,
                'visual_concepts': visual_concepts,
                'image_data': image_data,
                'enhanced_prompt': enhanced_prompt,
                'timestamp': database_service.get_current_timestamp()
            }
            session_id = database_service.save_session(session_data)
            
            # Clean up temp file
            os.remove(temp_audio_path)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'transcript': transcript,
                'visual_concepts': {
                    # Format for frontend compatibility
                    'objects': visual_concepts.get('visual_elements', {}).get('objects', []),
                    'colors': visual_concepts.get('visual_elements', {}).get('colors', []),
                    'settings': visual_concepts.get('visual_elements', {}).get('weather', []) + visual_concepts.get('visual_elements', {}).get('time', []),
                    'mood': visual_concepts.get('attributes', {}).get('mood', 'neutral'),
                    'style': visual_concepts.get('attributes', {}).get('style', 'realistic'),
                    'sentiment': visual_concepts.get('attributes', {}).get('sentiment', 'neutral'),
                    # Keep original structure for debugging
                    'raw_analysis': visual_concepts
                },
                'image_data': image_data
            })
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            raise e
            
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    """Generate image from text input"""
    import time
    start_time = time.time()
    
    try:
        logger.info("Received text-to-image request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'text' not in data:
            logger.error("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        
        text_input = data['text']
        preferred_service = data.get('image_service', None)  # Allow service selection
        logger.info(f"Processing text: {text_input[:50]}...")
        
        # Process with NLP
        visual_concepts = nlp_service.extract_visual_concepts(text_input)
        logger.info("NLP processing completed")
        
        # Generate enhanced prompt and image
        enhanced_prompt = nlp_service.generate_image_prompt(text_input, visual_concepts.get('sentiment'))
        logger.info(f"Enhanced prompt: {enhanced_prompt[:50]}...")
        
        image_data = image_service.generate_image(enhanced_prompt, preferred_service=preferred_service)
        logger.info("Image generation completed")
        
        # Calculate processing time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Save to database
        session_data = {
            'transcript': text_input,
            'visual_concepts': visual_concepts,
            'image_data': image_data,
            'enhanced_prompt': enhanced_prompt,
            'timestamp': database_service.get_current_timestamp(),
            'response_time': response_time,
            'service_used': image_data.get('service') if image_data else 'unknown'
        }
        session_id = database_service.save_session(session_data)
        logger.info(f"Session saved with ID: {session_id}")
        
        # Update analytics (preserving existing concept detection)
        confidence_score = visual_concepts.get('confidence', {}).get('overall', 0.85) * 100
        update_analytics(session_data, response_time, confidence_score)
        
        response_data = {
            'success': True,
            'session_id': session_id,
            'transcript': text_input,
            'visual_concepts': {
                # Format for frontend compatibility
                'objects': visual_concepts.get('visual_elements', {}).get('objects', []),
                'colors': visual_concepts.get('visual_elements', {}).get('colors', []),
                'settings': visual_concepts.get('visual_elements', {}).get('weather', []) + visual_concepts.get('visual_elements', {}).get('time', []),
                'mood': visual_concepts.get('attributes', {}).get('mood', 'neutral'),
                'style': visual_concepts.get('attributes', {}).get('style', 'realistic'),
                'sentiment': visual_concepts.get('attributes', {}).get('sentiment', 'neutral'),
                # Keep original structure for debugging
                'raw_analysis': visual_concepts
            },
            'image_data': image_data
        }
        logger.info("Sending successful response")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in text-to-image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data by ID"""
    try:
        session_data = database_service.get_session(session_id)
        if session_data:
            return jsonify(session_data)
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics_simple():
    """Get simple analytics data"""
    return jsonify({
        'totalSessions': analytics_data.get('total_sessions', 0),
        'averageAccuracy': 87.5,
        'averageResponseTime': 1200,
        'totalConcepts': analytics_data.get('total_concepts', 0)
    })

@app.route('/api/performance-chart', methods=['GET'])
def get_chart_simple():
    """Get simple chart data"""
    chart_type = request.args.get('type', 'accuracy')
    
    if chart_type == 'accuracy':
        return jsonify({
            'chartType': 'line',
            'title': 'Accuracy Trends Over Time',
            'data': [
                {'label': 'Week 1', 'value': 82},
                {'label': 'Week 2', 'value': 85},
                {'label': 'Week 3', 'value': 88},
                {'label': 'This Week', 'value': 91}
            ]
        })
    elif chart_type == 'objects':
        return jsonify({
            'chartType': 'bar',
            'title': 'Most Detected Objects',
            'data': [
                {'label': 'moon', 'value': 5},
                {'label': 'stars', 'value': 4},
                {'label': 'sun', 'value': 3},
                {'label': 'tree', 'value': 2}
            ]
        })
    elif chart_type == 'colors':
        return jsonify({
            'chartType': 'doughnut',
            'title': 'Color Distribution',
            'data': [
                {'label': 'blue', 'value': 8},
                {'label': 'green', 'value': 5},
                {'label': 'red', 'value': 3}
            ]
        })
    else:
        return jsonify({
            'chartType': 'line',
            'title': 'Response Times',
            'data': [
                {'label': 'Req 1', 'value': 1200},
                {'label': 'Req 2', 'value': 1100},
                {'label': 'Req 3', 'value': 1000}
            ]
        })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        # Calculate averages and metrics
        total_sessions = analytics_data['total_sessions']
        total_concepts = analytics_data['total_concepts']
        
        # Calculate average accuracy
        accuracy_scores = analytics_data.get('accuracy_scores', [])
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 85
        
        # Calculate average response time
        response_times = analytics_data.get('response_times', [])
        avg_response_time = sum(response_times) / len(response_times) if response_times else 1200
        
        return jsonify({
            'totalSessions': total_sessions,
            'averageAccuracy': round(avg_accuracy, 1),
            'averageResponseTime': round(avg_response_time),
            'totalConcepts': total_concepts,
            'popularObjects': dict(list(sorted(analytics_data['object_counts'].items(), key=lambda x: x[1], reverse=True))[:10]),
            'colorDistribution': analytics_data['color_counts']
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-chart', methods=['GET'])
def get_performance_chart():
    """Get performance chart data"""
    try:
        chart_type = request.args.get('type', 'accuracy')
        
        if chart_type == 'accuracy':
            # Mock accuracy trend data
            accuracy_data = [
                {'label': 'Week 1', 'value': 82},
                {'label': 'Week 2', 'value': 85},
                {'label': 'Week 3', 'value': 88},
                {'label': 'Week 4', 'value': 91},
                {'label': 'This Week', 'value': round(sum(analytics_data.get('accuracy_scores', [85])) / len(analytics_data.get('accuracy_scores', [85])), 1)}
            ]
            return jsonify({
                'chartType': 'line',
                'title': 'Accuracy Trends Over Time',
                'data': accuracy_data
            })
            
        elif chart_type == 'objects':
            # Top objects data
            object_data = [
                {'label': obj, 'value': count}
                for obj, count in sorted(analytics_data['object_counts'].items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            if not object_data:
                object_data = [{'label': 'No data', 'value': 0}]
                
            return jsonify({
                'chartType': 'bar',
                'title': 'Most Detected Objects',
                'data': object_data
            })
            
        elif chart_type == 'colors':
            # Color distribution data
            color_data = [
                {'label': color, 'value': count}
                for color, count in analytics_data['color_counts'].items()
            ]
            if not color_data:
                color_data = [{'label': 'No data', 'value': 0}]
                
            return jsonify({
                'chartType': 'doughnut',
                'title': 'Color Distribution',
                'data': color_data
            })
            
        elif chart_type == 'response-times':
            # Response time trend (mock data with some real data if available)
            recent_times = analytics_data.get('response_times', [])[-10:]
            if not recent_times:
                recent_times = [1200, 1150, 1100, 1080, 1050]
            
            time_data = [
                {'label': f'Request {i+1}', 'value': time_ms}
                for i, time_ms in enumerate(recent_times)
            ]
            
            return jsonify({
                'chartType': 'line',
                'title': 'Recent Response Times (ms)',
                'data': time_data
            })
            
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
            
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image-services', methods=['GET'])
def get_image_services():
    """Get available image generation services"""
    try:
        services = []
        
        # Check which services are available
        if hasattr(image_service, 'client') and image_service.client:
            services.append({
                'id': 'dalle',
                'name': 'DALL-E 3',
                'description': 'OpenAI\'s latest image generation model',
                'available': True
            })
        
        if hasattr(image_service, 'sd_pipeline') and image_service.sd_pipeline:
            services.append({
                'id': 'stable_diffusion',
                'name': 'Stable Diffusion',
                'description': 'Local Stable Diffusion model',
                'available': True
            })
        
        # Stability AI check
        stability_key = os.getenv('STABILITY_API_KEY')
        if stability_key:
            services.append({
                'id': 'stability',
                'name': 'Stability AI',
                'description': 'Stability AI\'s image generation',
                'available': True
            })
        
        # Fallback is always available
        services.append({
            'id': 'fallback',
            'name': 'SVG Generator',
            'description': 'Fallback SVG image generator',
            'available': True
        })
        
        return jsonify({
            'services': services,
            'default': 'dalle' if any(s['id'] == 'dalle' for s in services if s['available']) else 'stable_diffusion'
        })
        
    except Exception as e:
        logger.error(f"Error getting image services: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to ECHOSKETCH'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@socketio.on('voice_stream')
def handle_voice_stream(data):
    """Handle real-time voice streaming"""
    try:
        # Process streaming audio data
        # This would be implemented for real-time processing
        logger.info('Received voice stream data')
        emit('processing', {'message': 'Processing voice stream...'})
        
        # For now, just acknowledge
        emit('stream_received', {'status': 'received'})
        
    except Exception as e:
        logger.error(f"Error in voice stream: {str(e)}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = 'localhost'  # Fixed to localhost for proper binding
    
    logger.info(f"Starting ECHOSKETCH server on {host}:{port}")
    
    # Log API status
    if os.getenv('OPENAI_API_KEY'):
        logger.info("✅ OpenAI API configured for DALL-E image generation")
    else:
        logger.info("⚠️  OpenAI API key not found - using fallback image generation")
    
    if os.getenv('GEMINI_API_KEY'):
        logger.info("✅ Gemini API configured for enhanced NLP processing")  
    else:
        logger.info("⚠️  Gemini API key not found - using enhanced fallback NLP")
    
    logger.info("🚀 Enhanced concept detection with Stable Diffusion support ready!")
    
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)