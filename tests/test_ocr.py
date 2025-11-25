"""
Test script for OCR functionality
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ocr_engine import OCREngine
import cv2
import numpy as np


def create_test_image():
    """Create a simple test image with text"""
    # Create white background
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Hello World', (50, 100), font, 2, (0, 0, 0), 3)
    cv2.putText(img, 'Screen Translator Test', (50, 160), font, 1, (0, 0, 0), 2)
    
    return img


def test_ocr():
    """Test OCR engine"""
    print("=" * 60)
    print("OCR Engine Test")
    print("=" * 60)
    
    try:
        # Initialize OCR engine
        print("\n1. Initializing OCR engine...")
        ocr = OCREngine()
        print("   ✓ OCR engine initialized")
        
        # Create test image
        print("\n2. Creating test image...")
        test_img = create_test_image()
        print("   ✓ Test image created")
        
        # Save test image
        test_img_path = Path(__file__).parent / 'test_image.png'
        cv2.imwrite(str(test_img_path), test_img)
        print(f"   ✓ Test image saved to: {test_img_path}")
        
        # Perform OCR
        print("\n3. Performing OCR...")
        results = ocr.detect_and_recognize(test_img)
        print(f"   ✓ Detected {len(results)} text regions")
        
        # Display results
        print("\n4. OCR Results:")
        for i, (bbox, text, confidence) in enumerate(results, 1):
            print(f"\n   Text {i}:")
            print(f"   - Content: '{text}'")
            print(f"   - Confidence: {confidence:.2%}")
            print(f"   - Bounding box: {bbox}")
        
        # Test get_text_only method
        print("\n5. Testing get_text_only method...")
        full_text = ocr.get_text_only(test_img)
        print(f"   Full text:\n   {full_text}")
        
        # Test get_bounding_boxes method
        print("\n6. Testing get_bounding_boxes method...")
        bboxes = ocr.get_bounding_boxes(test_img)
        print(f"   Bounding boxes (x, y, w, h):")
        for i, bbox in enumerate(bboxes, 1):
            print(f"   {i}. {bbox}")
        
        print("\n" + "=" * 60)
        print("✓ All OCR tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during OCR test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = test_ocr()
    sys.exit(0 if success else 1)
