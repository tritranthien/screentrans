"""
OCR Engine module using RapidOCR for fast, accurate offline text recognition
"""

import numpy as np
from typing import List, Tuple, Optional
from rapidocr_onnxruntime import RapidOCR


class OCREngine:
    """
    Wrapper for RapidOCR engine.
    Provides text detection and recognition from images.
    """
    
    def __init__(self):
        """
        Initialize the RapidOCR engine.
        Models will be downloaded automatically on first run.
        """
        try:
            self.engine = RapidOCR()
            print("OCR Engine initialized successfully")
        except Exception as e:
            print(f"Error initializing OCR engine: {e}")
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
            # RapidOCR expects RGB or BGR, returns (dt_boxes, rec_res, scores)
            result, elapse = self.engine(image)
            
            if result is None or len(result) == 0:
                return []
            
            # Format results as list of (bbox, text, confidence)
            formatted_results = []
            for item in result:
                bbox = item[0]  # List of 4 corner points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text = item[1]  # Recognized text
                confidence = item[2]  # Confidence score
                
                formatted_results.append((bbox, text, confidence))
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during OCR: {e}")
            return []
    
    def get_text_only(self, image: np.ndarray) -> str:
        """
        Extract only the text from an image (without bounding boxes).
        
        Args:
            image: numpy array in BGR format
            
        Returns:
            str: All recognized text concatenated with newlines
        """
        results = self.detect_and_recognize(image)
        
        if not results:
            return ""
        
        # Extract just the text from each result
        texts = [text for _, text, _ in results]
        
        # Join with newlines
        return "\n".join(texts)
    
    def get_bounding_boxes(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Get bounding boxes for detected text regions.
        
        Args:
            image: numpy array in BGR format
            
        Returns:
            List of tuples (x, y, width, height) for each detected text region
        """
        results = self.detect_and_recognize(image)
        
        if not results:
            return []
        
        bboxes = []
        for bbox, _, _ in results:
            # Convert corner points to x, y, width, height
            xs = [point[0] for point in bbox]
            ys = [point[1] for point in bbox]
            
            x = min(xs)
            y = min(ys)
            width = max(xs) - x
            height = max(ys) - y
            
            bboxes.append((int(x), int(y), int(width), int(height)))
        
        return bboxes
