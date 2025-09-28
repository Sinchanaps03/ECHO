#!/usr/bin/env python3
"""
Debug script to test Gemini API configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_gemini_setup():
    """Debug Gemini API setup"""
    
    print("🔍 Debugging Gemini API Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Found .env file: {env_file}")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    # Check environment variable
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not found")
    
    # Check if google-generativeai can be imported
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
        
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Gemini model initialized successfully")
                
                # Test a simple request
                response = model.generate_content("Test message")
                print(f"✅ Test API call successful: {response.text[:50]}...")
                
            except Exception as e:
                print(f"❌ Gemini API test failed: {e}")
        else:
            print("⚠️  Cannot test API without key")
            
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")

if __name__ == "__main__":
    debug_gemini_setup()