"""
Screen capture module using mss for fast, cross-platform screen capture
"""

import numpy as np
import mss
from typing import Tuple, Optional
import cv2


class ScreenCapture:
    """
    Handles screen capture operations using mss library.
    Returns images as numpy arrays compatible with OpenCV and OCR engines.
    """
    
    def __init__(self):
        """Initialize the screen capture engine"""
        self.sct = mss.mss()
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        Capture a specific region of the screen.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of the region
            height: Height of the region
            
        Returns:
            numpy.ndarray: BGR image array (OpenCV format) or None if capture fails
        """
        try:
            # Define the region to capture
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }
            
            # Capture the screen region
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array (BGRA format from mss)
            img = np.array(screenshot)
            
            # Convert BGRA to BGR (remove alpha channel for OCR)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img_bgr
            
        except Exception as e:
            print(f"Error capturing screen region: {e}")
            return None
    
    def capture_full_screen(self, monitor_number: int = 1) -> Optional[np.ndarray]:
        """
        Capture the entire screen.
        
        Args:
            monitor_number: Monitor index (1-based, 1 is primary monitor)
            
        Returns:
            numpy.ndarray: BGR image array or None if capture fails
        """
        try:
            # Get monitor info
            monitor = self.sct.monitors[monitor_number]
            
            # Capture the screen
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array and BGR format
            img = np.array(screenshot)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img_bgr
            
        except Exception as e:
            print(f"Error capturing full screen: {e}")
            return None
    
    def get_monitor_info(self) -> list:
        """
        Get information about all available monitors.
        
        Returns:
            list: List of monitor dictionaries with position and size info
        """
        return self.sct.monitors
    
    def close(self):
        """Clean up resources"""
        if self.sct:
            self.sct.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
