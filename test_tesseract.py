"""
Quick test for Tesseract OCR
"""
import sys
import os

# Ensure src is in path
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
try:
    ocr = OCREngine()
    print("OCR Engine initialized!")
except Exception as e:
    print(f"Failed to initialize OCR: {e}")
    sys.exit(1)

print("\nPerforming OCR...")
text = ocr.get_text_only(img)

print(f"\n{'='*60}")
print("Detected text:")
print(f"{'='*60}")
print(text)
print(f"{'='*60}")

print("\nDetailed results:")
results = ocr.detect_and_recognize(img)
for bbox, txt, conf in results:
    print(f"Text: '{txt}' (Conf: {conf:.2f})")
