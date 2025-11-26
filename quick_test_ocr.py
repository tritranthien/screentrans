"""
Quick test for RapidOCR with existing capture image
"""
import sys
sys.path.insert(0, 'src')

from ocr_engine import OCREngine
import cv2

print("Loading image...")
img = cv2.imread('capture_306_701_373x72.png')

if img is None:
    print("Error: Could not load image")
    sys.exit(1)

print(f"Image loaded: {img.shape}")

print("\nInitializing OCR...")
ocr = OCREngine()

print("\nPerforming OCR...")
text = ocr.get_text_only(img)

print(f"\n{'='*60}")
print("Detected text:")
print(f"{'='*60}")
print(text)
print(f"{'='*60}")
