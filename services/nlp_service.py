import logging
import re
from collections import Counter

class NLPService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("NLP service initialized with basic text processing")
            
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

    def extract_visual_concepts(self, text):
        """Extract visual concepts from transcribed text"""
        try:
            text_lower = text.lower().strip()
            
            # Basic text cleaning
            cleaned_text = re.sub(r'[^\w\s]', '', text_lower)
            words = cleaned_text.split()
            
            # Visual element categories
            visual_keywords = {
                'colors': ['red', 'blue', 'green', 'yellow', 'black', 'white', 'orange', 'purple', 'pink', 'brown', 'gray', 'silver', 'gold'],
                'objects': ['house', 'tree', 'car', 'person', 'animal', 'bird', 'flower', 'mountain', 'ocean', 'beach', 'building', 'bridge'],
                'actions': ['running', 'walking', 'flying', 'swimming', 'dancing', 'sitting', 'standing', 'jumping', 'climbing'],
                'weather': ['sunny', 'cloudy', 'rainy', 'stormy', 'snowy', 'foggy', 'windy'],
                'time': ['morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk', 'sunrise', 'sunset'],
                'style': ['realistic', 'cartoon', 'sketch', 'painting', 'watercolor', 'oil painting', 'digital art', 'anime']
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
            
            # Extract other keywords
            all_keywords = self.extract_keywords(text)
            
            return {
                'visual_elements': visual_elements,
                'keywords': all_keywords,
                'sentiment': self.analyze_sentiment(text),
                'main_concept': text.strip()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting visual concepts: {e}")
            return {
                'visual_elements': {'colors': [], 'objects': [], 'actions': [], 'weather': [], 'time': [], 'style': []},
                'keywords': [],
                'sentiment': {'label': 'NEUTRAL', 'confidence': 0.5},
                'main_concept': text
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