#!/usr/bin/env python3
"""
Debug the exact response structure from our API
"""

import os
from dotenv import load_dotenv
from services.nlp_service import NLPService
import json

# Load environment variables
load_dotenv()

def test_response_structure():
    """Test what the actual response structure looks like"""
    
    print("🔍 Testing Response Structure")
    print("=" * 50)
    
    nlp_service = NLPService()
    
    test_text = "A magical forest with glowing crystal trees and purple flowers"
    
    print(f"Input: {test_text}")
    print("-" * 30)
    
    # Test the method that process_voice_to_visual calls
    concepts = nlp_service.extract_visual_concepts(test_text)
    print("Raw extract_visual_concepts result:")
    print(json.dumps(concepts, indent=2))
    print("-" * 30)
    
    # Test the full processing method
    full_result = nlp_service.process_voice_to_visual(test_text)
    print("Full process_voice_to_visual result:")
    print(json.dumps(full_result, indent=2))
    print("-" * 30)

if __name__ == "__main__":
    test_response_structure()