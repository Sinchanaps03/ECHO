#!/usr/bin/env python3
"""
Test DALL-E integration with your API key
"""

import os
from dotenv import load_dotenv
from services.image_service import ImageService
import json

# Load environment variables
load_dotenv()

def test_dalle_integration():
    """Test DALL-E image generation"""
    
    print("🎨 Testing DALL-E Integration")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✅ OpenAI API Key found: {openai_key[:10]}...")
    else:
        print("❌ OpenAI API Key not found")
        print("💡 Add OPENAI_API_KEY to your .env file")
        return
    
    # Initialize image service
    image_service = ImageService()
    
    # Test prompts
    test_prompts = [
        "A magical forest with glowing crystal trees and purple flowers",
        "An elegant fantasy castle floating in the clouds at sunset",
        "A cute robot painting a masterpiece in an art studio"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎯 Test {i}: {prompt}")
        print("-" * 40)
        
        try:
            result = image_service.generate_dalle_image(prompt)
            
            if result and result.get('success'):
                print("✅ DALL-E generation successful!")
                print(f"Service: {result.get('service')}")
                print(f"Model: {result.get('model')}")
                image_data = result.get('image_data', '')
                if image_data:
                    print(f"Image data length: {len(image_data)} characters")
                    print(f"Data prefix: {image_data[:50]}...")
            else:
                print("❌ DALL-E generation failed")
                if result:
                    print(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception during generation: {e}")
    
    print("\n" + "=" * 50)
    print("🎨 DALL-E integration test completed!")

if __name__ == "__main__":
    test_dalle_integration()