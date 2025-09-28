#!/usr/bin/env python3
"""
Test the actual API endpoint to see the full response
"""

import requests
import json

def test_api_response():
    """Test the actual API response structure"""
    
    print("🔍 Testing API Response")
    print("=" * 50)
    
    url = "http://localhost:5000/api/text-to-image"
    payload = {"text": "A magical forest with glowing crystal trees"}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Full API Response:")
            print(json.dumps(data, indent=2))
            
            # Check specific fields
            print("\n" + "="*30)
            print("VISUAL CONCEPTS STRUCTURE:")
            visual_concepts = data.get('visual_concepts', {})
            
            print(f"Objects: {visual_concepts.get('objects', [])}")
            print(f"Colors: {visual_concepts.get('colors', [])}")
            print(f"Settings: {visual_concepts.get('settings', [])}")
            print(f"Mood: {visual_concepts.get('mood', 'not found')}")
            print(f"Style: {visual_concepts.get('style', 'not found')}")
            print(f"Sentiment: {visual_concepts.get('sentiment', 'not found')}")
            
            # Check image data
            print(f"\nImage Data Present: {'image_data' in data}")
            if 'image_data' in data and data['image_data']:
                image_info = data['image_data']
                print(f"Image Service: {image_info.get('service', 'unknown')}")
                print(f"Image Success: {image_info.get('success', False)}")
                image_data = image_info.get('image_data', '')
                if image_data:
                    print(f"Image Data Length: {len(image_data)} chars")
                    print(f"Image Data Type: {'base64' if 'base64' in image_data else 'unknown'}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api_response()