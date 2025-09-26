import base64
import io
import logging
import os
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

class ImageService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI API
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.logger.info("OpenAI API initialized")
        else:
            self.client = None
            self.logger.warning("OpenAI API key not found")
        
        self.logger.info("Image service initialized")
    
    def generate_dalle_image(self, prompt, size="1024x1024"):
        """Generate image using DALL-E"""
        try:
            if not self.client:
                self.logger.warning("OpenAI API key not configured")
                return None
            
            self.logger.info(f"Generating DALL-E image for prompt: {prompt}")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            self.logger.info(f"DALL-E image generated successfully: {image_url}")
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(image_response.content).decode()
            
            return {
                'success': True,
                'image_data': f"data:image/png;base64,{image_data}",
                'url': image_url,
                'service': 'dalle'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating DALL-E image: {e}")
            return None
    
    def generate_stability_ai_image(self, prompt, size="512x512"):
        """Generate image using Stability AI API"""
        try:
            stability_api_key = os.getenv('STABILITY_API_KEY')
            if not stability_api_key:
                self.logger.warning("Stability AI API key not configured")
                return None
            
            url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {stability_api_key}",
            }
            
            data = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": int(size.split('x')[1]),
                "width": int(size.split('x')[0]),
                "samples": 1,
                "steps": 30,
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            
            if response_data.get('artifacts'):
                image_data = response_data['artifacts'][0]['base64']
                return {
                    'success': True,
                    'image_data': f"data:image/png;base64,{image_data}",
                    'service': 'stability_ai'
                }
            
        except Exception as e:
            self.logger.error(f"Error generating Stability AI image: {e}")
            return None
    
    def create_placeholder_image(self, prompt, size="512x512"):
        """Create a placeholder image with the prompt text"""
        try:
            width, height = map(int, size.split('x'))
            
            # Create a new image with a random background color
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
            bg_color = random.choice(colors)
            
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default if not available
            try:
                font_size = max(16, min(width, height) // 20)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Add text to the image
            text = f"Generated from:\\n{prompt[:100]}..."
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Add a semi-transparent background for text readability
            padding = 20
            draw.rectangle([x - padding, y - padding, x + text_width + padding, y + text_height + padding], 
                          fill=(255, 255, 255, 128))
            
            # Draw the text
            draw.multiline_text((x, y), text, fill='black', font=font, align='center')
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'image_data': f"data:image/png;base64,{image_data}",
                'service': 'placeholder'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating placeholder image: {e}")
            # Return a simple fallback
            return {
                'success': True,
                'image_data': "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgZmlsbD0iIzQ1QjdEMSIvPjx0ZXh0IHg9IjI1NiIgeT0iMjU2IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iMC4zZW0iPkVDSE9TS0VUQ0g8L3RleHQ+PC9zdmc+",
                'service': 'fallback'
            }
    
    def generate_image(self, prompt, size="512x512", preferred_service=None):
        """Generate an image using the best available service"""
        try:
            self.logger.info(f"Generating image for prompt: {prompt[:50]}...")
            
            # Try services in order of preference
            services = []
            
            if preferred_service == 'dalle' or not preferred_service:
                services.append(self.generate_dalle_image)
            if preferred_service == 'stability' or not preferred_service:
                services.append(self.generate_stability_ai_image)
            
            # Always add placeholder as fallback
            services.append(self.create_placeholder_image)
            
            for service_func in services:
                try:
                    result = service_func(prompt, size)
                    if result and result.get('success'):
                        self.logger.info(f"Image generated successfully using {result.get('service', 'unknown')}")
                        return result
                except Exception as e:
                    self.logger.warning(f"Service {service_func.__name__} failed: {e}")
                    continue
            
            # This shouldn't happen, but just in case
            self.logger.error("All image generation services failed")
            return {
                'success': False,
                'error': 'All image generation services failed',
                'image_data': None
            }
            
        except Exception as e:
            self.logger.error(f"Error in generate_image: {e}")
            return {
                'success': False,
                'error': str(e),
                'image_data': None
            }
    
    def enhance_prompt_for_generation(self, prompt, sentiment_analysis=None):
        """Enhance the prompt for better image generation"""
        try:
            enhanced_prompt = prompt
            
            # Add artistic style based on sentiment
            if sentiment_analysis:
                sentiment = sentiment_analysis.get('label', 'NEUTRAL')
                if sentiment == 'POSITIVE':
                    enhanced_prompt += ", vibrant colors, bright lighting, uplifting atmosphere"
                elif sentiment == 'NEGATIVE':
                    enhanced_prompt += ", muted colors, dramatic lighting, moody atmosphere"
                else:
                    enhanced_prompt += ", balanced colors, natural lighting"
            
            # Add general quality improvements
            enhanced_prompt += ", high quality, detailed, professional, artistic"
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Error enhancing prompt: {e}")
            return prompt
    
    def process_image_generation_request(self, prompt_data):
        """Process a complete image generation request"""
        try:
            prompt = prompt_data.get('prompt', '')
            size = prompt_data.get('size', '512x512')
            preferred_service = prompt_data.get('service')
            sentiment = prompt_data.get('sentiment_analysis')
            
            if not prompt:
                return {
                    'success': False,
                    'error': 'No prompt provided',
                    'image_data': None
                }
            
            # Enhance the prompt
            enhanced_prompt = self.enhance_prompt_for_generation(prompt, sentiment)
            
            # Generate the image
            result = self.generate_image(enhanced_prompt, size, preferred_service)
            
            # Add additional metadata
            if result.get('success'):
                result['original_prompt'] = prompt
                result['enhanced_prompt'] = enhanced_prompt
                result['generation_params'] = {
                    'size': size,
                    'service': preferred_service
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing image generation request: {e}")
            return {
                'success': False,
                'error': str(e),
                'image_data': None
            }