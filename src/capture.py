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
    
    def capture_scrolling_region(self, x: int, y: int, width: int, height: int, max_pages: int = 20) -> Optional[np.ndarray]:
        """
        Capture a region with scrolling.
        
        Args:
            x, y, width, height: Region coordinates
            max_pages: Maximum number of pages to scroll (default: 20)
            
        Returns:
            Stitched image
        """
        try:
            import pyautogui
            import time
            from stitcher import ImageStitcher
            
            # Disable fail-safe to prevent corner detection issues
            pyautogui.FAILSAFE = False
            
            print(f"Starting scrolling capture (max {max_pages} pages)...")
            
            # Click to focus the window under the cursor (center of region)
            # Use middle click to avoid triggering links, or just left click if safe
            # For now, let's try just clicking at the top-left corner of the region + offset
            # to minimize risk of clicking something interactive
            try:
                # Click at a safe position (not too close to edges)
                click_x = x + min(50, width // 4)
                click_y = y + min(50, height // 4)
                pyautogui.click(click_x, click_y)
                time.sleep(0.5)
            except Exception as e:
                print(f"Could not focus window: {e}")
            
            captured_images = []
            identical_count = 0  # Track consecutive identical images
            
            # Capture first page
            first_page = self.capture_region(x, y, width, height)
            if first_page is None:
                return None
            captured_images.append(first_page)
            
            for i in range(max_pages - 1):
                # Scroll down
                pyautogui.press('pagedown')
                time.sleep(0.8) # Wait for scroll animation
                
                # Capture next page
                next_page = self.capture_region(x, y, width, height)
                if next_page is None:
                    break
                
                # Check if we reached the bottom using MSE (Mean Squared Error)
                # This is more robust than exact equality
                mse = np.mean((next_page.astype(float) - captured_images[-1].astype(float)) ** 2)
                
                if mse < 10.0:  # Very similar images (threshold can be adjusted)
                    identical_count += 1
                    print(f"Page {i+2}: Similar to previous (MSE: {mse:.2f}), count: {identical_count}")
                    
                    # Stop if we get 2 consecutive identical images
                    if identical_count >= 2:
                        print("Reached end of page (2 consecutive identical images).")
                        break
                else:
                    identical_count = 0  # Reset counter
                    print(f"Page {i+2}: New content detected (MSE: {mse:.2f})")
                
                captured_images.append(next_page)
            
            print(f"Captured {len(captured_images)} pages. Stitching...")
            
            # Stitch images
            result = ImageStitcher.stitch_images(captured_images)
            return result
            
        except ImportError:
            print("pyautogui or stitcher not found. Please install requirements.")
            return self.capture_region(x, y, width, height)
        except Exception as e:
            print(f"Error in scrolling capture: {e}")
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
