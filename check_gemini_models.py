#!/usr/bin/env python3
"""
Check available Gemini models
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_available_models():
    """Check available Gemini models"""
    
    print("🔍 Checking Available Gemini Models")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)
            
            # List available models
            models = genai.list_models()
            for model in models:
                print(f"📍 Model: {model.name}")
                print(f"   Supported methods: {model.supported_generation_methods}")
                print()
                
        else:
            print("❌ GEMINI_API_KEY not found")
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")

if __name__ == "__main__":
    check_available_models()