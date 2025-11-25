"""
Test script for screen capture functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from capture import ScreenCapture
import cv2


def test_capture():
    """Test screen capture"""
    print("=" * 60)
    print("Screen Capture Test")
    print("=" * 60)
    
    try:
        # Initialize screen capture
        print("\n1. Initializing screen capture...")
        capture = ScreenCapture()
        print("   ✓ Screen capture initialized")
        
        # Get monitor info
        print("\n2. Getting monitor information...")
        monitors = capture.get_monitor_info()
        print(f"   ✓ Found {len(monitors) - 1} monitor(s)")  # -1 because index 0 is all monitors
        
        for i, monitor in enumerate(monitors):
            if i == 0:
                print(f"\n   All monitors combined: {monitor}")
            else:
                print(f"\n   Monitor {i}: {monitor}")
        
        # Capture a small region (top-left corner)
        print("\n3. Capturing screen region (500x300 from top-left)...")
        img = capture.capture_region(0, 0, 500, 300)
        
        if img is not None:
            print(f"   ✓ Captured image shape: {img.shape}")
            print(f"   ✓ Image dtype: {img.dtype}")
            
            # Save the captured image
            output_path = Path(__file__).parent / 'captured_region.png'
            cv2.imwrite(str(output_path), img)
            print(f"   ✓ Saved to: {output_path}")
        else:
            print("   ✗ Failed to capture image")
            return False
        
        # Test full screen capture
        print("\n4. Capturing full screen (monitor 1)...")
        full_img = capture.capture_full_screen(monitor_number=1)
        
        if full_img is not None:
            print(f"   ✓ Captured full screen shape: {full_img.shape}")
            
            # Save the full screen capture
            output_path = Path(__file__).parent / 'captured_fullscreen.png'
            cv2.imwrite(str(output_path), full_img)
            print(f"   ✓ Saved to: {output_path}")
        else:
            print("   ✗ Failed to capture full screen")
            return False
        
        # Cleanup
        print("\n5. Cleaning up...")
        capture.close()
        print("   ✓ Resources released")
        
        print("\n" + "=" * 60)
        print("✓ All screen capture tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during capture test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = test_capture()
    sys.exit(0 if success else 1)
