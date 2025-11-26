"""
OCR Engine module using Tesseract for offline text recognition
"""

import numpy as np
from typing import List, Tuple, Optional
import pytesseract
import cv2
import os
import sys

# Set path to tesseract executable
# Try common locations
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(TESSERACT_CMD):
    # Fallback to local app data
    TESSERACT_CMD = os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe')

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    print("Warning: Tesseract executable not found in standard locations.")

class OCREngine:
    """
    Wrapper for Tesseract OCR engine.
    Provides text detection and recognition from images.
    """
    
    def __init__(self, languages=['en']):
        """
        Initialize the Tesseract engine.
        
        Args:
            languages: List of language codes (default: ['en'] for English)
        """
        try:
            print(f"Initializing Tesseract OCR for languages: {languages}")
            
            # Convert language codes to Tesseract format (e.g., 'en' -> 'eng', 'vi' -> 'vie')
            self.lang_map = {
                'en': 'eng',
                'vi': 'vie',
                'es': 'spa',
                'fr': 'fra',
                'de': 'deu',
                'ja': 'jpn',
                'ko': 'kor',
                'zh': 'chi_sim'
            }
            
            self.langs = "+".join([self.lang_map.get(l, l) for l in languages])
            
            # Verify tesseract is available
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract OCR initialized successfully (Version: {version})")
            print(f"Using executable at: {pytesseract.pytesseract.tesseract_cmd}")
            
        except Exception as e:
            print(f"Error initializing OCR engine: {e}")
            print("Please ensure Tesseract is installed correctly.")
            raise
    
    def detect_and_recognize(self, image: np.ndarray) -> List[Tuple[List[List[int]], str, float]]:
        """
        Detect and recognize text in an image.
        
        Args:
            image: numpy array in BGR format (OpenCV format)
            
        Returns:
            List of tuples, each containing:
                - bbox: List of 4 [x, y] coordinates for text box corners
                - text: Recognized text string
                - confidence: Recognition confidence score (0-1)
            Returns empty list if no text detected or on error.
        """
        try:
            # Tesseract expects RGB format
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Get data including bounding boxes and confidence
            # Output is a dict with keys: 'left', 'top', 'width', 'height', 'conf', 'text'
            data = pytesseract.image_to_data(image_rgb, lang=self.langs, output_type=pytesseract.Output.DICT)
            
            formatted_results = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                # Filter out empty text and low confidence results
                # conf is -1 for empty blocks/structure
                conf = float(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > 0 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # Create bbox points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    bbox = [
                        [x, y],          # Top-left
                        [x + w, y],      # Top-right
                        [x + w, y + h],  # Bottom-right
                        [x, y + h]       # Bottom-left
                    ]
                    
                    # Normalize confidence to 0-1 range
                    normalized_conf = conf / 100.0
                    
                    formatted_results.append((bbox, text, normalized_conf))
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during OCR: {e}")
            return []
    
    def get_text_only(self, image: np.ndarray) -> str:
        """
        Extract only the text from an image.
        """
        try:
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
                
            return pytesseract.image_to_string(image_rgb, lang=self.langs).strip()
        except Exception as e:
            print(f"Error getting text: {e}")
            return ""
    
    def get_bounding_boxes(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Get bounding boxes for detected text regions.
        """
        results = self.detect_and_recognize(image)
        if not results:
            return []
            
        bboxes = []
        for bbox, _, _ in results:
            # Extract x, y, w, h from the 4 points
            x = bbox[0][0]
            y = bbox[0][1]
            w = bbox[1][0] - x
            h = bbox[2][1] - y
            bboxes.append((int(x), int(y), int(w), int(h)))
            
        return bboxes

