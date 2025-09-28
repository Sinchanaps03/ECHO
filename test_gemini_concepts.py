#!/usr/bin/env python3
"""
Test script to demonstrate enhanced concept detection with Gemini API
"""

from services.nlp_service import NLPService
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_concept_detection():
    """Test the enhanced concept detection with various fantasy prompts"""
    
    nlp_service = NLPService()
    
    # Test prompts similar to the fantasy image example
    test_prompts = [
        "A magical forest with glowing crystal trees",
        "An elegant elven warrior princess with silver armor",
        "A mystical dragon soaring over ancient ruins",
        "An enchanted castle floating among purple clouds",
        "A wise wizard with glowing staff in a moonlit grove"
    ]
    
    print("🔮 Testing Enhanced Concept Detection with Gemini API")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎯 Test {i}: {prompt}")
        print("-" * 50)
        
        try:
            # Process the text to extract enhanced concepts
            concepts = nlp_service.process_voice_to_visual(prompt)
            
            print(f"📝 Objects: {', '.join(concepts.get('objects', []))}")
            print(f"🎨 Colors: {', '.join(concepts.get('colors', []))}")
            print(f"🌟 Attributes: {', '.join(concepts.get('attributes', []))}")
            print(f"😊 Mood: {concepts.get('mood', 'not detected')}")
            print(f"🎭 Style: {concepts.get('style', 'not detected')}")
            
            # Show enhanced prompt
            if 'enhanced_prompt' in concepts:
                print(f"✨ Enhanced: {concepts['enhanced_prompt'][:100]}...")
                
        except Exception as e:
            print(f"❌ Error processing '{prompt}': {e}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced concept detection test completed!")

if __name__ == "__main__":
    test_concept_detection()