#!/usr/bin/env python3
"""Debug script for NLP service"""

from services.nlp_service import NLPService
import json

# Initialize NLP service
nlp = NLPService()

# Test cases
test_cases = [
    "With palm trees.",
    "A blue sky with stars and a moon.",
    "A beautiful peacock with colorful feathers"
]

print("=== NLP Service Debug ===")
for text in test_cases:
    print(f"\nTesting: '{text}'")
    result = nlp.extract_visual_concepts(text)
    print("Result:", json.dumps(result, indent=2))
    
    print("\nFormatted for frontend:")
    print("Objects:", result.get('visual_elements', {}).get('objects', []))
    print("Colors:", result.get('visual_elements', {}).get('colors', []))
    print("Mood:", result.get('attributes', {}).get('mood', 'neutral'))
    print("Style:", result.get('attributes', {}).get('style', 'realistic'))
    print("Sentiment:", result.get('attributes', {}).get('sentiment', 'neutral'))