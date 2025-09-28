from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
from datetime import datetime
import base64
import random
import re
import math
from io import BytesIO

# Initialize Flask app and logger
app = Flask(__name__, static_folder='frontend/build/static', static_url_path='/static')
app.config['SECRET_KEY'] = 'echosketch-secret-key'

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import advanced NLP libraries
import os
import logging
import json
from datetime import datetime
import base64
import random
import re
from io import BytesIO

# Try to import advanced NLP libraries
NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
    # Force download required NLTK data at startup
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
except Exception as e:
    NLTK_AVAILABLE = False
    logging.warning(f"NLTK unavailable or failed to download: {e}")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:3001', 
    'http://localhost:5000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5000'
])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Analytics and performance tracking
analytics_data = {
    'total_requests': 0,
    'successful_generations': 0,
    'concept_accuracy': [],
    'response_times': [],
    'error_count': 0,
    'popular_objects': {},
    'popular_colors': {},
    'daily_usage': {}
}

def update_analytics(concepts, response_time, success=True):
    """Update analytics data for performance tracking"""
    analytics_data['total_requests'] += 1
    
    if success:
        analytics_data['successful_generations'] += 1
        
        # Track concept accuracy
        total_concepts = len(concepts.get('objects', [])) + len(concepts.get('colors', [])) + len(concepts.get('settings', []))
        confidence = concepts.get('confidence', {}).get('overall', 0.0)
        analytics_data['concept_accuracy'].append(confidence)
        
        # Track popular objects and colors
        for obj in concepts.get('objects', []):
            analytics_data['popular_objects'][obj] = analytics_data['popular_objects'].get(obj, 0) + 1
        for color in concepts.get('colors', []):
            analytics_data['popular_colors'][color] = analytics_data['popular_colors'].get(color, 0) + 1
    else:
        analytics_data['error_count'] += 1
    
    analytics_data['response_times'].append(response_time)
    
    # Keep only last 100 entries to manage memory
    if len(analytics_data['concept_accuracy']) > 100:
        analytics_data['concept_accuracy'] = analytics_data['concept_accuracy'][-100:]
    if len(analytics_data['response_times']) > 100:
        analytics_data['response_times'] = analytics_data['response_times'][-100:]

def get_performance_metrics():
    """Calculate current performance metrics"""
    if not analytics_data['concept_accuracy']:
        return {
            'accuracy': 0,
            'avg_response_time': 0,
            'success_rate': 0,
            'total_requests': 0
        }
    
    accuracy = sum(analytics_data['concept_accuracy']) / len(analytics_data['concept_accuracy']) * 100
    avg_response_time = sum(analytics_data['response_times']) / len(analytics_data['response_times'])
    success_rate = (analytics_data['successful_generations'] / analytics_data['total_requests']) * 100 if analytics_data['total_requests'] > 0 else 0
    
    return {
        'accuracy': round(accuracy, 2),
        'avg_response_time': round(avg_response_time, 3),
        'success_rate': round(success_rate, 2),
        'total_requests': analytics_data['total_requests'],
        'error_rate': round((analytics_data['error_count'] / analytics_data['total_requests']) * 100, 2) if analytics_data['total_requests'] > 0 else 0
    }

# Simple in-memory storage for sessions
sessions = {}

def extract_visual_concepts(text):
    """Extract visual concepts from text using NLP"""
    # Always robust fallback
    concepts = {
        'objects': [],
        'colors': [],
        'settings': [],
        'mood': 'neutral',
        'sentiment': 'positive',
        'style': 'realistic'
    }
    text_lower = text.lower()
    # Enhanced word lists with synonyms and related terms for better accuracy
    color_words = [
        'red', 'crimson', 'scarlet', 'cherry', 'ruby', 'maroon', 'burgundy',
        'blue', 'azure', 'navy', 'cobalt', 'sapphire', 'turquoise', 'teal',
        'green', 'emerald', 'jade', 'olive', 'lime', 'mint', 'forest',
        'yellow', 'gold', 'amber', 'lemon', 'canary', 'mustard', 'honey',
        'purple', 'violet', 'lavender', 'plum', 'magenta', 'indigo', 'lilac',
        'orange', 'coral', 'peach', 'tangerine', 'apricot', 'bronze',
        'pink', 'rose', 'salmon', 'blush', 'fuchsia', 'hot pink',
        'black', 'ebony', 'charcoal', 'midnight', 'onyx', 'jet',
        'white', 'ivory', 'pearl', 'snow', 'cream', 'alabaster',
        'brown', 'chocolate', 'coffee', 'mahogany', 'tan', 'beige',
        'gray', 'grey', 'silver', 'slate', 'ash', 'steel',
        'golden', 'silver', 'bright', 'dark', 'light', 'deep',
        'colorful', 'vibrant', 'brilliant', 'radiant', 'luminous'
    ]
    
    # Expanded nature objects with better categorization
    nature_objects = [
        # Animals
        'peacock', 'bird', 'birds', 'eagle', 'dove', 'swan', 'parrot',
        'butterfly', 'dragonfly', 'bee', 'ladybug', 'firefly',
        'deer', 'rabbit', 'squirrel', 'fox', 'wolf', 'bear',
        'fish', 'dolphin', 'whale', 'shark', 'seahorse',
        # Plants & Trees
        'tree', 'trees', 'oak', 'pine', 'maple', 'willow', 'cherry',
        'palm', 'bamboo', 'cedar', 'birch', 'redwood',
        'flower', 'flowers', 'rose', 'tulip', 'lily', 'daisy', 'sunflower',
        'orchid', 'iris', 'daffodil', 'poppy', 'jasmine',
        'grass', 'fern', 'moss', 'ivy', 'vine', 'bush', 'shrub',
        # Natural Elements
        'mountain', 'mountains', 'hill', 'valley', 'canyon', 'cliff',
        'ocean', 'sea', 'lake', 'river', 'stream', 'waterfall', 'pond',
        'beach', 'shore', 'coast', 'island', 'reef',
        'forest', 'jungle', 'meadow', 'field', 'prairie', 'desert',
        'cave', 'rock', 'stone', 'crystal', 'gem',
        # Celestial
        'sun', 'moon', 'star', 'stars', 'planet', 'comet', 'galaxy',
        'cloud', 'clouds', 'rainbow', 'lightning', 'aurora',
        # Weather
        'rain', 'snow', 'storm', 'wind', 'mist', 'fog', 'frost'
    ]
    settings = ['sunset', 'sunrise', 'night', 'day', 'indoor', 'outdoor', 'garden', 'park', 'city', 'countryside', 'tropical', 'desert', 'winter', 'summer', 'spring', 'autumn']
    mood_words = {
        'happy': 'cheerful',
        'peaceful': 'calm', 
        'serene': 'tranquil',
        'beautiful': 'pleasant',
        'sunny': 'bright',
        'calm': 'peaceful',
        'dramatic': 'intense',
        'magical': 'mystical'
    }
    style_words = ['realistic', 'cartoon', 'sketch', 'painting', 'watercolor', 'oil painting', 'digital art', 'photographic']
    # Enhanced NLP processing with confidence scoring
    confidence_scores = {'objects': 0.0, 'colors': 0.0, 'settings': 0.0, 'overall': 0.0}
    
    # Try NLTK with enhanced accuracy
    if NLTK_AVAILABLE:
        try:
            tokens = word_tokenize(text_lower)
            pos_tags = pos_tag(tokens)
            # Enhanced object detection with POS tagging
            for word, pos in pos_tags:
                if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Nouns
                    if word in nature_objects:
                        concepts['objects'].append(word)
                        confidence_scores['objects'] += 1.0
                    # Fuzzy matching for partial words
                    elif len(word) > 3:
                        for obj in nature_objects:
                            if word in obj or obj in word:
                                concepts['objects'].append(obj)
                                confidence_scores['objects'] += 0.8
                                break
                elif pos in ['JJ', 'JJR', 'JJS']:  # Adjectives - often describe colors/moods
                    if word in color_words:
                        concepts['colors'].append(word)
                        confidence_scores['colors'] += 1.0
        except Exception as e:
            logging.warning(f"Enhanced NLTK failed, using fallback: {e}")
            # Fallback with pattern matching
            for obj in nature_objects:
                if obj in text_lower:
                    concepts['objects'].append(obj)
    else:
        # Enhanced fallback with substring matching
        for obj in nature_objects:
            if obj in text_lower:
                concepts['objects'].append(obj)
                confidence_scores['objects'] += 0.9
    
    # Enhanced color detection with context
    for color in color_words:
        if color in text_lower:
            concepts['colors'].append(color)
            confidence_scores['colors'] += 1.0
    
    # Enhanced setting detection
    for setting in settings:
        if setting in text_lower:
            concepts['settings'].append(setting)
            confidence_scores['settings'] += 1.0
    
    # Calculate overall confidence
    total_detections = len(concepts['objects']) + len(concepts['colors']) + len(concepts['settings'])
    if total_detections > 0:
        confidence_scores['overall'] = min(1.0, (confidence_scores['objects'] + 
                                                 confidence_scores['colors'] + 
                                                 confidence_scores['settings']) / total_detections)
    
    # Add confidence scores to concepts
    concepts['confidence'] = confidence_scores
    for mood_word, mood_value in mood_words.items():
        if mood_word in text_lower:
            concepts['mood'] = mood_value
            break
    for style in style_words:
        if style in text_lower:
            concepts['style'] = style
            break
    positive_words = ['beautiful', 'lovely', 'amazing', 'wonderful', 'bright', 'colorful', 'peaceful', 'happy', 'sunny']
    if any(word in text_lower for word in positive_words):
        concepts['sentiment'] = 'positive'
    elif any(word in text_lower for word in ['dark', 'gloomy', 'sad', 'scary']):
        concepts['sentiment'] = 'negative'
    else:
        concepts['sentiment'] = 'neutral'
    for key in concepts:
        if isinstance(concepts[key], list):
            concepts[key] = list(set(concepts[key]))
    return concepts

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'ECHOSKETCH API is running'})

# Serve React App (catch-all route)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve the React application"""
    build_path = os.path.join('frontend', 'build')
    
    # Skip API routes - let them be handled by their specific routes
    if path.startswith('api/'):
        return "Not found", 404
    
    if path != "" and os.path.exists(os.path.join(build_path, path)):
        return send_from_directory(build_path, path)
    else:
        return send_file(os.path.join(build_path, 'index.html'))

def generate_advanced_svg_image(text, concepts):
    """Generate advanced SVG image with sophisticated graphics"""
    width, height = 512, 512
    
    # Color palette based on concepts
    color_map = {
        'red': ['#FF6B6B', '#FF5252', '#F44336'],
        'blue': ['#4ECDC4', '#2196F3', '#03A9F4'], 
        'green': ['#96CEB4', '#4CAF50', '#8BC34A'],
        'yellow': ['#FFEAA7', '#FFEB3B', '#FFC107'],
        'purple': ['#DDA0DD', '#9C27B0', '#673AB7'],
        'orange': ['#F39C12', '#FF9800', '#FF5722'],
        'pink': ['#FF69B4', '#E91E63', '#F06292'],
        'golden': ['#FFD700', '#FFC107', '#FFAB00']
    }
    
    primary_colors = color_map.get(concepts['colors'][0] if concepts['colors'] else 'blue', color_map['blue'])
    
    svg_elements = []
    
    # Background gradient
    svg_elements.append(f'''
    <defs>
        <radialGradient id="bg" cx="50%" cy="50%" r="70%">
            <stop offset="0%" style="stop-color:{primary_colors[0]};stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:{primary_colors[1]};stop-opacity:0.3" />
        </radialGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#bg)"/>''')
    
    # Add objects based on concepts
    if 'sun' in concepts['objects']:
        sun_color = '#FFD700' if 'golden' in concepts['colors'] else '#FFA500'
        svg_elements.append(f'''
        <g transform="translate(400, 80)">
            <circle cx="0" cy="0" r="40" fill="{sun_color}" filter="url(#glow)"/>
            <g stroke="{sun_color}" stroke-width="3">
                <line x1="-60" y1="0" x2="-50" y2="0"/>
                <line x1="60" y1="0" x2="50" y2="0"/>
                <line x1="0" y1="-60" x2="0" y2="-50"/>
                <line x1="0" y1="60" x2="0" y2="50"/>
                <line x1="-42" y1="-42" x2="-35" y2="-35"/>
                <line x1="42" y1="42" x2="35" y2="35"/>
                <line x1="42" y1="-42" x2="35" y2="-35"/>
                <line x1="-42" y1="42" x2="-35" y2="35"/>
            </g>
        </g>''')
    
    if 'moon' in concepts['objects']:
        moon_color = '#E8E8E8' if 'bright' not in concepts['colors'] else '#FFFACD'
        svg_elements.append(f'''
        <g transform="translate(100, 100)">
            <circle cx="0" cy="0" r="35" fill="{moon_color}" filter="url(#glow)"/>
            <circle cx="-10" cy="-8" r="3" fill="#D3D3D3"/>
            <circle cx="8" cy="5" r="4" fill="#D3D3D3"/>
            <circle cx="-5" cy="12" r="2" fill="#D3D3D3"/>
        </g>''')
    
    if 'stars' in concepts['objects']:
        star_color = '#FFFF00' if 'yellow' in concepts['colors'] else '#FFFFFF'
        for i in range(15):
            x = random.randint(50, width-50)
            y = random.randint(50, height-200)
            size = random.randint(2, 6)
            svg_elements.append(f'''
            <g transform="translate({x}, {y})">
                <polygon points="0,-{size} {size*0.3},-{size*0.3} {size},0 {size*0.3},{size*0.3} 0,{size} -{size*0.3},{size*0.3} -{size},0 -{size*0.3},-{size*0.3}" 
                         fill="{star_color}" filter="url(#glow)"/>
            </g>''')
    
    if any(tree in concepts['objects'] for tree in ['tree', 'trees', 'palm']):
        tree_color = '#8B4513'
        leaf_color = primary_colors[0] if 'green' in concepts['colors'] else '#228B22'
        svg_elements.append(f'''
        <g transform="translate(200, 400)">
            <rect x="-10" y="0" width="20" height="80" fill="{tree_color}"/>
            <ellipse cx="0" cy="-20" rx="40" ry="30" fill="{leaf_color}" filter="url(#glow)"/>
            <ellipse cx="-15" cy="-10" rx="25" ry="20" fill="#32CD32" opacity="0.8"/>
            <ellipse cx="15" cy="-15" rx="20" ry="25" fill="#90EE90" opacity="0.7"/>
        </g>''')
    
    if 'peacock' in concepts['objects']:
        peacock_colors = ['#4169E1', '#00CED1', '#9370DB', '#FF1493']
        svg_elements.append(f'''
        <g transform="translate(300, 250)">
            <!-- Peacock body -->
            <ellipse cx="0" cy="0" rx="50" ry="30" fill="{peacock_colors[0]}" filter="url(#glow)"/>
            <!-- Peacock head -->
            <ellipse cx="-40" cy="-20" rx="15" ry="12" fill="{peacock_colors[1]}"/>
            <circle cx="-45" cy="-25" r="3" fill="#FFD700"/>
            <!-- Tail feathers -->
            <g stroke-width="3" opacity="0.9">
                <ellipse cx="20" cy="-30" rx="8" ry="25" fill="{peacock_colors[2]}" transform="rotate(-20)"/>
                <ellipse cx="30" cy="-10" rx="8" ry="28" fill="{peacock_colors[3]}" transform="rotate(0)"/>
                <ellipse cx="25" cy="15" rx="8" ry="25" fill="{peacock_colors[0]}" transform="rotate(20)"/>
                <ellipse cx="15" cy="30" rx="8" ry="22" fill="{peacock_colors[1]}" transform="rotate(40)"/>
            </g>
            <!-- Feather eyes -->
            <circle cx="25" cy="-35" r="4" fill="#FFD700"/>
            <circle cx="35" cy="-15" r="4" fill="#FFD700"/>
            <circle cx="30" cy="20" r="4" fill="#FFD700"/>
        </g>''')
    
    if 'beach' in concepts['objects'] or 'ocean' in concepts['objects']:
        water_color = primary_colors[0] if 'blue' in concepts['colors'] else '#4682B4'
        sand_color = '#F4A460' if 'yellow' not in concepts['colors'] else '#FFD700'
        svg_elements.append(f'''
        <g>
            <!-- Beach sand -->
            <rect x="0" y="{height-100}" width="{width}" height="100" fill="{sand_color}"/>
            <!-- Ocean waves -->
            <path d="M0,{height-100} Q{width//4},{height-120} {width//2},{height-100} T{width},{height-100}" 
                  fill="none" stroke="{water_color}" stroke-width="8" opacity="0.8"/>
            <path d="M0,{height-90} Q{width//3},{height-110} {width//1.5},{height-90} T{width},{height-90}" 
                  fill="none" stroke="{water_color}" stroke-width="6" opacity="0.6"/>
        </g>''')
    
    # Add title and concept info
    svg_elements.append(f'''
    <text x="20" y="30" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white" filter="url(#glow)">
        ECHOSKETCH Generated
    </text>
    <text x="20" y="{height-20}" font-family="Arial, sans-serif" font-size="12" fill="white" opacity="0.8">
        Style: {concepts['style']} | Mood: {concepts['mood']} | Objects: {', '.join(concepts['objects'][:3])}
    </text>''')
    
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        {''.join(svg_elements)}
    </svg>'''
    
    encoded_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded_svg}"

def generate_enhanced_image(text, concepts):
    """Generate enhanced image with multiple generation methods"""
    try:
        # Method 1: Try advanced SVG generation first
        if True:  # Always try SVG first as it's most reliable
            logger.info("Generating advanced SVG image")
            return generate_advanced_svg_image(text, concepts)
        
        # Method 2: Enhanced PIL if available
        if PIL_AVAILABLE:
            logger.info("Generating enhanced PIL image")
            return generate_pil_image(text, concepts)
        else:
            # Method 3: Fallback to simple SVG
            return generate_placeholder_image()
            
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
        return generate_placeholder_image()

def generate_pil_image(text, concepts):
    """Generate enhanced PIL image"""
    width, height = 512, 512
    
    # Choose colors based on detected concepts
    color_palette = {
        'red': [(255, 107, 107), (255, 82, 82), (255, 118, 118)],
        'blue': [(78, 205, 196), (45, 183, 209), (116, 185, 255)], 
        'green': [(150, 206, 180), (129, 236, 236), (85, 239, 196)],
        'yellow': [(255, 234, 167), (255, 211, 105), (253, 203, 110)],
        'purple': [(221, 160, 221), (162, 155, 254), (181, 131, 141)],
        'orange': [(243, 156, 18), (230, 126, 34), (255, 165, 2)],
        'pink': [(255, 105, 180), (255, 192, 203), (255, 20, 147)],
        'golden': [(255, 215, 0), (255, 223, 0), (255, 193, 7)],
        'bright': [(255, 225, 53), (255, 241, 118), (247, 220, 111)],
        'colorful': [(255, 107, 107), (78, 205, 196), (150, 206, 180)]
    }
    
    if concepts['colors']:
        primary_color = concepts['colors'][0]
        colors = color_palette.get(primary_color, [(78, 205, 196), (45, 183, 209), (116, 185, 255)])
    else:
        colors = random.choice(list(color_palette.values()))
    
    # Create image with PIL
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create sophisticated gradient background
    base_color = colors[0]
    accent_color = colors[1] if len(colors) > 1 else colors[0]
    
    for y in range(height):
        # Create smooth gradient between base and accent colors
        ratio = y / height
        r = int(base_color[0] * (1 - ratio) + accent_color[0] * ratio)
        g = int(base_color[1] * (1 - ratio) + accent_color[1] * ratio)
        b = int(base_color[2] * (1 - ratio) + accent_color[2] * ratio)
        
        # Add some brightness variation for depth
        brightness = 1.0 - (ratio * 0.2)
        r = int(r * brightness)
        g = int(g * brightness) 
        b = int(b * brightness)
        
        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add sophisticated visual elements based on detected concepts
    if 'sun' in concepts['objects'] or 'sunny' in text.lower():
        # Draw detailed sun with rays
        sun_color = (255, 215, 0) if 'golden' in concepts['colors'] else (255, 223, 0)
        draw.ellipse([380, 30, 480, 130], fill=sun_color, outline=(255, 165, 0), width=3)
        # Sun rays
        for i in range(8):
            angle = i * 45
            x1 = 430 + 60 * math.cos(math.radians(angle))
            y1 = 80 + 60 * math.sin(math.radians(angle))
            x2 = 430 + 80 * math.cos(math.radians(angle))
            y2 = 80 + 80 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=sun_color, width=3)
    
    if any(tree in concepts['objects'] for tree in ['tree', 'trees', 'palm', 'forest']):
        # Draw detailed trees
        tree_x = 150
        # Trunk
        draw.rectangle([tree_x, 350, tree_x + 20, 480], fill=(139, 69, 19))
        # Foliage - multiple layers for depth
        foliage_color = (34, 139, 34) if 'green' in concepts['colors'] else (46, 125, 50)
        draw.ellipse([tree_x - 40, 280, tree_x + 60, 380], fill=foliage_color)
        draw.ellipse([tree_x - 30, 300, tree_x + 50, 400], fill=(60, 179, 113))
        draw.ellipse([tree_x - 20, 320, tree_x + 40, 420], fill=(46, 139, 87))
    
    if 'peacock' in concepts['objects']:
        # Draw detailed peacock
        peacock_colors = [(65, 105, 225), (0, 206, 209), (147, 112, 219), (255, 20, 147)]
        # Body
        draw.ellipse([230, 200, 330, 300], fill=peacock_colors[0], outline=(0, 0, 139), width=2)
        # Head and neck
        draw.ellipse([280, 160, 320, 200], fill=peacock_colors[1])
        draw.ellipse([290, 150, 310, 170], fill=(255, 215, 0))  # crown
        # Elaborate tail feathers in a fan pattern
        center_x, center_y = 280, 250
        for i in range(7):
            angle = -60 + i * 20  # Fan spread
            length = 80 + random.randint(-10, 10)
            end_x = center_x + length * math.cos(math.radians(angle))
            end_y = center_y + length * math.sin(math.radians(angle))
            # Feather shaft
            draw.line([(center_x, center_y), (end_x, end_y)], fill=peacock_colors[i % len(peacock_colors)], width=3)
            # Feather eye
            draw.ellipse([end_x - 8, end_y - 8, end_x + 8, end_y + 8], fill=peacock_colors[(i + 1) % len(peacock_colors)])
            draw.ellipse([end_x - 4, end_y - 4, end_x + 4, end_y + 4], fill=(255, 215, 0))
    
    if any(flower in concepts['objects'] for flower in ['flower', 'flowers', 'garden']):
        # Draw colorful flowers
        flower_colors = [(255, 20, 147), (255, 105, 180), (186, 85, 211), (255, 182, 193)]
        for i in range(3):
            fx = 100 + i * 150
            fy = 400 + random.randint(-30, 30)
            flower_color = random.choice(flower_colors)
            # Petals
            for j in range(6):
                angle = j * 60
                px = fx + 15 * math.cos(math.radians(angle))
                py = fy + 15 * math.sin(math.radians(angle))
                draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=flower_color)
            # Center
            draw.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 215, 0))
    
    # Add text overlay
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add title text
    title = "ECHOSKETCH Generated"
    draw.text((20, 20), title, fill='white', font=font)
    
    # Add concept tags
    concept_text = f"Style: {concepts['style']} | Mood: {concepts['mood']}"
    draw.text((20, height-40), concept_text, fill='white', font=font)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    encoded_img = base64.b64encode(img_data).decode('utf-8')
    
    return f"data:image/png;base64,{encoded_img}"

def generate_placeholder_image():
    """Generate a colorful placeholder image"""
    try:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        selected_color = random.choice(colors)
        
        # Simple placeholder image as base64 SVG
        svg_content = f'''<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:{selected_color};stop-opacity:1" />
<stop offset="100%" style="stop-color:#ffffff;stop-opacity:0.8" />
</linearGradient>
</defs>
<rect width="512" height="512" fill="url(#gradient)"/>
<text x="256" y="240" fill="white" font-family="Arial, sans-serif" font-size="24" text-anchor="middle">ECHOSKETCH</text>
<text x="256" y="280" fill="white" font-family="Arial, sans-serif" font-size="18" text-anchor="middle">Generated Image</text>
</svg>'''
        
        encoded_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded_svg}"
        
    except Exception as e:
        logger.error(f"Error generating placeholder: {e}")
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzRFQ0RDNCIvPjx0ZXh0IHg9IjUwIiB5PSI1NSIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkltYWdlPC90ZXh0Pjwvc3ZnPg=="

@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    """Generate image from text input"""
    start_time = datetime.now()
    try:
        logger.info("Received text-to-image request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'text' not in data:
            logger.error("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        
        text_input = data['text']
        logger.info(f"Processing text: {text_input}")
        
        # Extract visual concepts using existing NLP (keeping it unchanged)
        visual_concepts = extract_visual_concepts(text_input)
        logger.info(f"Extracted concepts: {visual_concepts}")
        
        # Generate enhanced image using existing method
        image_data = generate_enhanced_image(text_input, visual_concepts)
        
        # Create enhanced prompt
        objects_str = ', '.join(visual_concepts['objects'][:3]) if visual_concepts['objects'] else 'scene'
        colors_str = ', '.join(visual_concepts['colors'][:2]) if visual_concepts['colors'] else 'colorful'
        enhanced_prompt = f"A {visual_concepts['style']} {visual_concepts['mood']} image featuring {objects_str} with {colors_str} colors"
        
        # Create session
        session_id = f"session_{len(sessions) + 1}_{int(datetime.now().timestamp())}"
        session_data = {
            'id': session_id,
            'transcript': text_input,
            'visual_concepts': visual_concepts,
            'image_data': image_data,
            'enhanced_prompt': enhanced_prompt,
            'timestamp': datetime.now().isoformat(),
            'processing_time': (datetime.now() - start_time).total_seconds()
        }
        
        # Save to in-memory storage
        sessions[session_id] = session_data
        logger.info(f"Session saved with ID: {session_id}")
        
        # Update analytics with performance tracking
        response_time = (datetime.now() - start_time).total_seconds()
        update_analytics(visual_concepts, response_time, success=True)
        
        response_data = {
            'success': True,
            'session_id': session_id,
            'transcript': text_input,
            'visual_concepts': visual_concepts,
            'image_data': image_data,
            'enhanced_prompt': enhanced_prompt,
            'processing_time': response_time
        }
        
        logger.info("Sending successful response")
        return jsonify(response_data)
        
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds()
        update_analytics({}, response_time, success=False)
        logger.error(f"Error in text-to-image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get performance analytics and metrics"""
    try:
        metrics = get_performance_metrics()
        
        # Get popular concepts for graphs
        popular_objects = dict(sorted(analytics_data['popular_objects'].items(), key=lambda x: x[1], reverse=True)[:10])
        popular_colors = dict(sorted(analytics_data['popular_colors'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Recent accuracy trend (last 20 requests)
        recent_accuracy = analytics_data['concept_accuracy'][-20:] if len(analytics_data['concept_accuracy']) >= 20 else analytics_data['concept_accuracy']
        
        # Recent response times (last 20 requests)
        recent_response_times = analytics_data['response_times'][-20:] if len(analytics_data['response_times']) >= 20 else analytics_data['response_times']
        
        analytics_response = {
            'performance_metrics': metrics,
            'popular_objects': popular_objects,
            'popular_colors': popular_colors,
            'accuracy_trend': recent_accuracy,
            'response_time_trend': recent_response_times,
            'total_sessions': len(sessions)
        }
        
        return jsonify(analytics_response)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-chart', methods=['GET'])
def get_performance_chart():
    """Generate performance chart data"""
    try:
        chart_type = request.args.get('type', 'accuracy')
        
        if chart_type == 'accuracy':
            data = analytics_data['concept_accuracy'][-50:]  # Last 50 requests
            labels = [f"Req {i+1}" for i in range(len(data))]
            chart_data = {
                'type': 'line',
                'title': 'Concept Detection Accuracy Over Time',
                'labels': labels,
                'datasets': [{
                    'label': 'Accuracy (%)',
                    'data': [acc * 100 for acc in data],
                    'borderColor': '#4ECDC4',
                    'backgroundColor': 'rgba(78, 205, 196, 0.1)'
                }]
            }
        elif chart_type == 'response_time':
            data = analytics_data['response_times'][-50:]  # Last 50 requests
            labels = [f"Req {i+1}" for i in range(len(data))]
            chart_data = {
                'type': 'line',
                'title': 'Response Time Trend',
                'labels': labels,
                'datasets': [{
                    'label': 'Response Time (s)',
                    'data': data,
                    'borderColor': '#FF6B6B',
                    'backgroundColor': 'rgba(255, 107, 107, 0.1)'
                }]
            }
        elif chart_type == 'popular_objects':
            popular = dict(sorted(analytics_data['popular_objects'].items(), key=lambda x: x[1], reverse=True)[:10])
            chart_data = {
                'type': 'bar',
                'title': 'Most Detected Objects',
                'labels': list(popular.keys()),
                'datasets': [{
                    'label': 'Detection Count',
                    'data': list(popular.values()),
                    'backgroundColor': ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#85C1E9', '#F8C471']
                }]
            }
        elif chart_type == 'popular_colors':
            popular = dict(sorted(analytics_data['popular_colors'].items(), key=lambda x: x[1], reverse=True)[:10])
            chart_data = {
                'type': 'doughnut',
                'title': 'Most Detected Colors',
                'labels': list(popular.keys()),
                'datasets': [{
                    'label': 'Detection Count',
                    'data': list(popular.values()),
                    'backgroundColor': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFD700', '#FF69B4', '#98D8C8', '#F7DC6F']
                }]
            }
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
            
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions_list = list(sessions.values())
        sessions_list.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(sessions_list[:limit])
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data by ID"""
    try:
        if session_id in sessions:
            return jsonify(sessions[session_id])
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_sessions():
    """Search sessions"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        # Simple search in session transcripts
        matching_sessions = []
        for session in sessions.values():
            if query.lower() in session['transcript'].lower():
                matching_sessions.append(session)
        
        matching_sessions.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(matching_sessions[:limit])
    except Exception as e:
        logger.error(f"Error searching sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    try:
        stats = {
            'total_sessions': len(sessions),
            'total_images': len(sessions),
            'recent_activity': len([s for s in sessions.values() if datetime.now().timestamp() - datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).timestamp() < 3600])
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-voice', methods=['POST'])
def process_voice():
    """Process voice input"""
    try:
        logger.info("Received process-voice request")
        
        # Handle both form data and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle audio file upload
            if 'audio' in request.files:
                audio_file = request.files['audio']
                logger.info(f"Received audio file: {audio_file.filename}")
                # For now, return a mock transcription
                return jsonify({
                    'success': True,
                    'transcript': 'Mock transcription from audio file',
                    'session_id': f"voice_session_{int(datetime.now().timestamp())}"
                })
        
        # Handle JSON data
        data = request.get_json()
        if data and 'text' in data:
            # Process as text-to-image
            return text_to_image()
        
        return jsonify({'error': 'No valid input provided'}), 400
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')  # Changed to localhost only
    
    logger.info(f"Starting ECHOSKETCH minimal server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False)