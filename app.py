from flask import Flask, request, jsonify
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

# Initialize Flask app
app = Flask(__name__)
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'ECHOSKETCH API is running'})

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
                'visual_concepts': visual_concepts,
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
    try:
        logger.info("Received text-to-image request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'text' not in data:
            logger.error("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        
        text_input = data['text']
        logger.info(f"Processing text: {text_input[:50]}...")
        
        # Process with NLP
        visual_concepts = nlp_service.extract_visual_concepts(text_input)
        logger.info("NLP processing completed")
        
        # Generate enhanced prompt and image
        enhanced_prompt = nlp_service.generate_image_prompt(text_input, visual_concepts.get('sentiment'))
        logger.info(f"Enhanced prompt: {enhanced_prompt[:50]}...")
        
        image_data = image_service.generate_image(enhanced_prompt)
        logger.info("Image generation completed")
        
        # Save to database
        session_data = {
            'transcript': text_input,
            'visual_concepts': visual_concepts,
            'image_data': image_data,
            'enhanced_prompt': enhanced_prompt,
            'timestamp': database_service.get_current_timestamp()
        }
        session_id = database_service.save_session(session_data)
        logger.info(f"Session saved with ID: {session_id}")
        
        response_data = {
            'success': True,
            'session_id': session_id,
            'transcript': text_input,
            'visual_concepts': visual_concepts,
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
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting ECHOSKETCH server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=True)