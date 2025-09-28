#!/usr/bin/env python3
"""Simple ECHOSKETCH test server"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the current directory to the path so we can import our services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nlp_service import NLPService

app = Flask(__name__)
CORS(app)

# Initialize NLP service
nlp_service = NLPService()

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'Server working!', 'nlp_ready': True})

@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text_input = data['text']
        print(f"Processing: {text_input}")
        
        # Process with NLP
        visual_concepts = nlp_service.extract_visual_concepts(text_input)
        print(f"Visual concepts: {visual_concepts}")
        
        # Create response with proper formatting
        response_data = {
            'success': True,
            'transcript': text_input,
            'visual_concepts': {
                'objects': visual_concepts.get('visual_elements', {}).get('objects', []),
                'colors': visual_concepts.get('visual_elements', {}).get('colors', []),
                'settings': visual_concepts.get('visual_elements', {}).get('weather', []) + visual_concepts.get('visual_elements', {}).get('time', []),
                'mood': visual_concepts.get('attributes', {}).get('mood', 'neutral'),
                'style': visual_concepts.get('attributes', {}).get('style', 'realistic'),
                'sentiment': visual_concepts.get('attributes', {}).get('sentiment', 'neutral'),
                'raw_analysis': visual_concepts
            },
            'image_data': {
                'image_data': 'data:image/png;base64,placeholder_image_data',
                'success': True,
                'service': 'test'
            }
        }
        
        print(f"Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ECHOSKETCH Test Server...")
    print("✅ NLP Service initialized")
    app.run(host='localhost', port=5000, debug=True)