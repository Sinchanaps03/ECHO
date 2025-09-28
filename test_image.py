#!/usr/bin/env python3
"""Test image generation methods directly"""

import sys
sys.path.append('.')
from app_minimal import generate_advanced_svg_image, extract_visual_concepts

def test_image_generation():
    print("🧪 Testing ECHOSKETCH Image Generation")
    
    # Test text
    test_text = "a beautiful peacock with golden feathers in a tropical garden"
    
    print(f"📝 Input Text: {test_text}")
    
    # Extract concepts
    print("🔍 Extracting concepts...")
    concepts = extract_visual_concepts(test_text)
    print(f"✅ Concepts: {concepts}")
    
    # Generate image
    print("🎨 Generating advanced SVG image...")
    try:
        image_data = generate_advanced_svg_image(test_text, concepts)
        print(f"✅ Image generated successfully!")
        print(f"📊 Image data length: {len(image_data)} characters")
        print(f"🔗 Image format: {image_data[:50]}...")
        
        # Save to file for testing
        if image_data.startswith('data:image/svg+xml;base64,'):
            import base64
            svg_data = base64.b64decode(image_data[26:])
            with open('test_generated.svg', 'wb') as f:
                f.write(svg_data)
            print("💾 Saved test image as 'test_generated.svg'")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_generation()
    print(f"\n🏁 Test {'PASSED' if success else 'FAILED'}")