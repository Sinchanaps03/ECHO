import logging
import re
from collections import Counter
import os

# Try to import Google Generative AI (Gemini)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except (ImportError, Exception):
    GEMINI_AVAILABLE = False
    genai = None

class NLPService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini API if available
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.logger.info("Gemini API initialized successfully")
                self.use_gemini = True
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini: {e}")
                self.gemini_model = None
                self.use_gemini = False
        else:
            self.gemini_model = None
            self.use_gemini = False
            if not GEMINI_AVAILABLE:
                self.logger.info("Gemini not available, using fallback NLP processing")
            else:
                self.logger.warning("Gemini API key not configured")
        
        self.logger.info("NLP service initialized with enhanced text processing")
            
    def analyze_sentiment(self, text):
        """Analyze sentiment of the given text using simple keyword matching"""
        try:
            # Simple sentiment analysis using keyword matching
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'beautiful', 'happy', 'joy', 'love', 'fantastic', 'awesome', 'brilliant', 'perfect', 'stunning']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'angry', 'hate', 'pain', 'ugly', 'disgusting', 'annoying', 'frustrating', 'disappointing']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                confidence = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
                return {'label': 'POSITIVE', 'confidence': confidence}
            elif negative_count > positive_count:
                confidence = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
                return {'label': 'NEGATIVE', 'confidence': confidence}
            else:
                return {'label': 'NEUTRAL', 'confidence': 0.5}
                
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'confidence': 0.5}
    
    def extract_keywords(self, text):
        """Extract keywords from text using simple text processing"""
        try:
            # Remove punctuation and convert to lowercase
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            words = clean_text.split()
            
            # Filter out common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
                'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
                'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'very', 'just', 'now',
                'then', 'than', 'only', 'also', 'back', 'other', 'many', 'some', 'time', 'way', 'well',
                'make', 'get', 'go', 'see', 'come', 'take', 'know', 'think', 'say', 'tell', 'look', 'want'
            }
            
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count frequency and return top keywords
            word_freq = Counter(keywords)
            return [word for word, count in word_freq.most_common(10)]
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
    
    def generate_image_prompt(self, text, sentiment=None):
        """Generate an enhanced image prompt based on text and sentiment"""
        try:
            if sentiment is None:
                sentiment = self.analyze_sentiment(text)
            
            keywords = self.extract_keywords(text)
            
            # Base prompt from the text
            base_prompt = text
            
            # Enhance based on sentiment
            if sentiment['label'] == 'POSITIVE':
                style_modifiers = "vibrant colors, bright lighting, uplifting atmosphere, beautiful, cheerful"
            elif sentiment['label'] == 'NEGATIVE':
                style_modifiers = "muted colors, dramatic lighting, moody atmosphere, artistic, somber"
            else:
                style_modifiers = "balanced colors, natural lighting, peaceful atmosphere, serene"
            
            # Add artistic style based on content
            if any(word in text.lower() for word in ['nature', 'forest', 'tree', 'flower', 'mountain', 'ocean', 'sky']):
                artistic_style = "landscape photography, natural beauty, high resolution"
            elif any(word in text.lower() for word in ['person', 'people', 'face', 'portrait', 'human']):
                artistic_style = "portrait photography, professional, detailed"
            elif any(word in text.lower() for word in ['abstract', 'art', 'creative', 'design', 'pattern']):
                artistic_style = "abstract art, creative design, artistic expression"
            else:
                artistic_style = "digital art, high quality, detailed, professional"
            
            # Combine everything
            if keywords:
                keyword_string = ", ".join(keywords[:5])  # Top 5 keywords
                enhanced_prompt = f"{base_prompt}, featuring {keyword_string}, {style_modifiers}, {artistic_style}"
            else:
                enhanced_prompt = f"{base_prompt}, {style_modifiers}, {artistic_style}"
            
            # Clean up the prompt
            enhanced_prompt = re.sub(r',\s*,', ',', enhanced_prompt)  # Remove double commas
            enhanced_prompt = re.sub(r'\s+', ' ', enhanced_prompt)    # Remove extra spaces
            
            return enhanced_prompt.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating image prompt: {e}")
            return text
    
    def summarize_text(self, text, max_length=150):
        """Summarize the given text using simple extractive method"""
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if len(sentences) <= 2:
                return text
            
            # Simple extractive summarization - pick most important sentences
            # Score sentences by keyword frequency
            keywords = self.extract_keywords(text)
            sentence_scores = []
            
            for sentence in sentences:
                score = 0
                sentence_lower = sentence.lower()
                for keyword in keywords[:10]:  # Top 10 keywords
                    if keyword in sentence_lower:
                        score += 1
                sentence_scores.append((sentence, score))
            
            # Sort by score and take top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select sentences to fit within max_length
            summary_sentences = []
            current_length = 0
            
            for sentence, score in sentence_scores:
                if current_length + len(sentence) < max_length:
                    summary_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            if summary_sentences:
                return '. '.join(summary_sentences) + '.'
            else:
                # If no sentences fit, return first sentence
                return sentences[0] + '.'
                
        except Exception as e:
            self.logger.error(f"Error summarizing text: {e}")
            return text

    def extract_visual_concepts_with_gemini(self, text):
        """Extract visual concepts using Gemini AI for enhanced accuracy"""
        if not self.use_gemini or not self.gemini_model:
            return self.extract_visual_concepts(text)
        
        try:
            prompt = f"""
            Analyze this text for visual elements: "{text}"
            
            Extract and categorize visual concepts into JSON format:
            {{
                "visual_elements": {{
                    "objects": ["list of objects, things, items mentioned"],
                    "colors": ["list of colors mentioned"],
                    "weather": ["list of weather conditions"],
                    "time": ["list of time-related elements"],
                    "actions": ["list of actions or movements"],
                    "style": ["list of style descriptors"]
                }},
                "attributes": {{
                    "mood": "cheerful/pleasant/neutral/somber/melancholic",
                    "style": "realistic/artistic/beautiful/minimalist/other",
                    "sentiment": "positive/negative/neutral"
                }},
                "keywords": ["key descriptive words"],
                "main_concept": "brief summary of the main visual concept"
            }}
            
            Be thorough in detecting objects, colors, and style elements. Return only valid JSON.
            """
            
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Try to extract JSON from the response
            import json
            try:
                # Find JSON in the response (handle markdown code blocks)
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    gemini_result = json.loads(json_str)
                    
                    # Enhance with sentiment analysis
                    sentiment_analysis = self.analyze_sentiment(text)
                    
                    # Merge results with fallback data structure
                    enhanced_result = {
                        'visual_elements': gemini_result.get('visual_elements', {}),
                        'keywords': gemini_result.get('keywords', []),
                        'sentiment': sentiment_analysis,
                        'main_concept': gemini_result.get('main_concept', text.strip()),
                        'attributes': gemini_result.get('attributes', {
                            'mood': 'neutral',
                            'style': 'realistic', 
                            'sentiment': sentiment_analysis['label'].lower()
                        })
                    }
                    
                    self.logger.info(f"Gemini analysis successful for: {text[:50]}...")
                    return enhanced_result
                    
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Failed to parse Gemini JSON response: {e}")
        
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
        
        # Fallback to original method
        return self.extract_visual_concepts(text)

    def extract_visual_concepts(self, text):
        """Extract visual concepts from transcribed text"""
        # Check if we should use Gemini first
        if self.use_gemini:
            return self.extract_visual_concepts_with_gemini(text)
        
        try:
            text_lower = text.lower().strip()
            
            # Basic text cleaning
            cleaned_text = re.sub(r'[^\w\s]', '', text_lower)
            words = cleaned_text.split()
            
            # Enhanced visual element categories
            visual_keywords = {
                'colors': ['red', 'blue', 'green', 'yellow', 'black', 'white', 'orange', 'purple', 'pink', 'brown', 'gray', 'grey', 'silver', 'gold', 'turquoise', 'cyan', 'magenta', 'violet', 'indigo', 'crimson', 'scarlet', 'azure'],
                'objects': ['house', 'tree', 'trees', 'car', 'person', 'people', 'animal', 'bird', 'birds', 'flower', 'flowers', 'mountain', 'mountains', 'ocean', 'beach', 'building', 'buildings', 'bridge', 'sun', 'moon', 'star', 'stars', 'cloud', 'clouds', 'palm', 'peacock', 'garden', 'tropical', 'feathers', 'sky', 'water', 'lake', 'river', 'forest', 'field', 'road', 'path', 'rock', 'rocks', 'stone', 'stones'],
                'actions': ['running', 'walking', 'flying', 'swimming', 'dancing', 'sitting', 'standing', 'jumping', 'climbing', 'playing', 'working', 'relaxing', 'sleeping'],
                'weather': ['sunny', 'cloudy', 'rainy', 'stormy', 'snowy', 'foggy', 'windy', 'clear', 'bright', 'dark', 'overcast'],
                'time': ['morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk', 'sunrise', 'sunset', 'midnight', 'noon'],
                'style': ['realistic', 'cartoon', 'sketch', 'painting', 'watercolor', 'oil painting', 'digital art', 'anime', 'abstract', 'photorealistic', 'artistic', 'beautiful', 'colorful']
            }
            
            # Extract visual elements
            visual_elements = {
                'colors': [],
                'objects': [],
                'actions': [],
                'weather': [],
                'time': [],
                'style': []
            }
            
            # Find matches in each category
            for category, keyword_list in visual_keywords.items():
                for keyword in keyword_list:
                    if keyword in text_lower:
                        visual_elements[category].append(keyword)
            
            # Remove duplicates and sort
            for category in visual_elements:
                visual_elements[category] = sorted(list(set(visual_elements[category])))
            
            # Extract other keywords
            all_keywords = self.extract_keywords(text)
            
            # Analyze sentiment for attributes
            sentiment_analysis = self.analyze_sentiment(text)
            
            # Determine mood based on content and sentiment
            mood = "neutral"
            if sentiment_analysis['label'] == 'POSITIVE':
                mood = "cheerful" if sentiment_analysis['confidence'] > 0.7 else "pleasant"
            elif sentiment_analysis['label'] == 'NEGATIVE':
                mood = "melancholic" if sentiment_analysis['confidence'] > 0.7 else "somber"
            
            # Determine style based on content
            detected_style = "realistic"
            if visual_elements['style']:
                detected_style = visual_elements['style'][0]  # Use first detected style
            elif any(word in text_lower for word in ['beautiful', 'colorful', 'vibrant']):
                detected_style = "artistic"
            elif any(word in text_lower for word in ['simple', 'clean', 'minimal']):
                detected_style = "minimalist"
            
            # Determine sentiment description
            sentiment_desc = sentiment_analysis['label'].lower()
            
            return {
                'visual_elements': visual_elements,
                'keywords': all_keywords,
                'sentiment': sentiment_analysis,
                'main_concept': text.strip(),
                'attributes': {
                    'mood': mood,
                    'style': detected_style,
                    'sentiment': sentiment_desc
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting visual concepts: {e}")
            return {
                'visual_elements': {'colors': [], 'objects': [], 'actions': [], 'weather': [], 'time': [], 'style': []},
                'keywords': [],
                'sentiment': {'label': 'NEUTRAL', 'confidence': 0.5},
                'main_concept': text,
                'attributes': {
                    'mood': 'neutral',
                    'style': 'realistic',
                    'sentiment': 'neutral'
                }
            }

    def process_voice_to_visual(self, transcribed_text):
        """Process voice input and extract visual concepts for image generation"""
        try:
            if not transcribed_text or not transcribed_text.strip():
                return {
                    'success': False,
                    'error': 'No text provided',
                    'visual_prompt': '',
                    'analysis': {}
                }
            
            # Extract visual concepts
            analysis = self.extract_visual_concepts(transcribed_text)
            
            # Generate enhanced image prompt
            enhanced_prompt = self.generate_image_prompt(transcribed_text, analysis['sentiment'])
            
            return {
                'success': True,
                'visual_prompt': enhanced_prompt,
                'original_text': transcribed_text,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error in voice to visual processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'visual_prompt': transcribed_text,
                'analysis': {}
            }