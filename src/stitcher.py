import cv2
import numpy as np
from typing import Optional, Tuple, List

class ImageStitcher:
    """
    Helper class to stitch vertical screenshots together.
    """
    
    @staticmethod
    def stitch_images(images: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Stitch a list of images vertically.
        
        Args:
            images: List of BGR images (numpy arrays)
            
        Returns:
            Stitched image or None if input is empty
        """
        if not images:
            return None
        
        if len(images) == 1:
            return images[0]
        
        result = images[0]
        
        for i in range(1, len(images)):
            result = ImageStitcher._stitch_two(result, images[i])
            
        return result
    
    @staticmethod
    def _stitch_two(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """
        Stitch two images vertically by finding overlap.
        img1 is above img2.
        """
        # Convert to grayscale for matching
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        h1, w1 = gray1.shape
        h2, w2 = gray2.shape
        
        # We assume the overlap is at the bottom of img1 and top of img2
        # Take the bottom 20% of img1 as template
        search_h = int(h1 * 0.2)
        if search_h < 10: search_h = 10 # Minimum height
        
        template = gray1[h1-search_h:h1, :]
        
        # Search in the top 50% of img2
        search_area_h = int(h2 * 0.5)
        search_area = gray2[0:search_area_h, :]
        
        # Match template
        try:
            res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # Check confidence (threshold 0.8)
            if max_val > 0.8:
                # Found match
                match_y = max_loc[1]
                
                # The overlap amount in img2 is match_y + search_h
                # We want to keep img2 starting from match_y + search_h
                # Wait, let's trace:
                # template is img1[h1-search_h : h1]
                # it matches at search_area[match_y : match_y+search_h]
                # So img2[match_y : match_y+search_h] is the same as img1 bottom.
                # The part of img2 ABOVE match_y is ... wait.
                # If img2 is the result of scrolling DOWN, then the top of img2 should overlap with bottom of img1.
                # So the template (bottom of img1) should be found somewhere in img2.
                # If found at match_y, it means img2[match_y : match_y+search_h] == template.
                # So img2[0 : match_y] is content that was in img1 (above the template)? 
                # No, usually scrolling moves content UP.
                # So bottom of img1 is now at top of img2.
                # So we expect match_y to be close to 0.
                
                # Overlap region in img2 ends at match_y + search_h.
                # So we keep img2 from (match_y + search_h) onwards?
                # No, that would discard the matched part (which is fine, it's in img1)
                # AND anything above it in img2?
                
                # Let's visualize:
                # Img1: [ A ]
                #       [ B ] <- Template
                #
                # Img2: [ B ] <- Match found here (match_y = 0)
                #       [ C ]
                
                # If match_y > 0, it means there is some content X above B in Img2:
                # Img2: [ X ]
                #       [ B ]
                # This implies we scrolled UP? Or captured something we missed?
                # Usually in "scroll down", the content moves up.
                # So the bottom of screen (B) moves to top of screen.
                
                cut_index = match_y + search_h
                
                # Crop img2
                img2_cropped = img2[cut_index:, :]
                
                # Concatenate
                return np.vstack((img1, img2_cropped))
            else:
                # No good match found, just append?
                # Or maybe the scroll was larger than screen height (unlikely)
                # For safety, let's just append with a visual separator or just append
                print(f"Stitching warning: Low match confidence ({max_val:.2f}). Appending directly.")
                return np.vstack((img1, img2))
                
        except Exception as e:
            print(f"Stitching error: {e}")
            return np.vstack((img1, img2))
