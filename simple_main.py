"""
Simplified Screen Translator - UI and Screen Capture Only
For testing without OCR/Translation dependencies
"""

import sys
import multiprocessing as mp
from multiprocessing import Queue
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
import mss
import cv2
import numpy as np

# Import UI components
sys.path.insert(0, 'src')
from ui.snipping import SnippingWidget


class SimpleScreenTranslatorApp:
    """
    Simplified application for testing UI and screen capture.
    """
    
    def __init__(self):
        """Initialize the application."""
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Snipping widget
        self.snipping_widget = None
        
        # Screen capture
        self.sct = mss.mss()
        
        # Create system tray icon
        self.create_tray_icon()
        
        print("✓ Screen Translator (Simple Mode) started")
        print("✓ Double-click tray icon to capture screen region")
        print("✓ Right-click tray icon for options")
    
    def create_tray_icon(self):
        """Create system tray icon with menu"""
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Create icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()
        
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        # Create menu
        menu = QMenu()
        
        # Capture action
        capture_action = QAction("📸 Capture Region", self.app)
        capture_action.triggered.connect(self.start_capture)
        menu.addAction(capture_action)
        
        menu.addSeparator()
        
        # About action
        about_action = QAction("ℹ️ About", self.app)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Double-click to capture
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.start_capture()
    
    def start_capture(self):
        """Start the region selection process"""
        print("\n📸 Starting region capture...")
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()
    
    def on_region_selected(self, x, y, width, height):
        """Handle region selection from snipping tool."""
        print(f"✓ Region selected: ({x}, {y}, {width}, {height})")
        
        # Capture the region
        try:
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }
            
            screenshot = self.sct.grab(monitor)
            img = np.array(screenshot)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Save the captured image
            filename = f"capture_{x}_{y}_{width}x{height}.png"
            cv2.imwrite(filename, img_bgr)
            
            print(f"✓ Screenshot saved: {filename}")
            print(f"✓ Image size: {img_bgr.shape}")
            
            # Show success message
            QMessageBox.information(
                None,
                "Capture Successful! 🎉",
                f"Screenshot saved as:\n{filename}\n\n"
                f"Region: {width}x{height}\n"
                f"Position: ({x}, {y})\n\n"
                "Note: OCR and Translation features\n"
                "will be added once dependencies are fixed."
            )
            
        except Exception as e:
            print(f"✗ Error capturing region: {e}")
            QMessageBox.critical(
                None,
                "Capture Failed",
                f"Error: {e}"
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            None,
            "About Screen Translator",
            "Screen Translator (Simple Mode)\n\n"
            "✓ Screen Capture: Working\n"
            "✓ UI: Working\n"
            "⚠ OCR: Pending (dependency issues)\n"
            "⚠ Translation: Pending (dependency issues)\n\n"
            "This is a simplified version for testing.\n"
            "Full features will be available once\n"
            "Python/library compatibility is resolved."
        )
    
    def quit_app(self):
        """Quit the application cleanly"""
        print("\n👋 Shutting down...")
        self.sct.close()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    mp.freeze_support()
    
    print("=" * 60)
    print("Screen Translator - Simple Mode")
    print("=" * 60)
    print("\nThis version includes:")
    print("  ✓ Screen capture")
    print("  ✓ Region selection UI")
    print("  ✓ System tray integration")
    print("\nPending (due to dependency issues):")
    print("  ⚠ OCR (text recognition)")
    print("  ⚠ Translation")
    print("\n" + "=" * 60 + "\n")
    
    app = SimpleScreenTranslatorApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
