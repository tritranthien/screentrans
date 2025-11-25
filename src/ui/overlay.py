"""
Transparent overlay window for displaying translations
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from typing import List, Dict, Any
import sys


class OverlayWindow(QMainWindow):
    """
    Frameless, transparent window that displays translations
    over the original text positions.
    """
    
    # Signal to request new translation
    translate_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput  # Click-through
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Make fullscreen
        self.showFullScreen()
        
        # Translation data
        self.translations = []
        self.region_offset = (0, 0)  # Offset to position translations correctly
        
        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.clear_translations)
        self.hide_timer.setSingleShot(True)
        
        # Font settings
        self.font = QFont("Arial", 12, QFont.Weight.Bold)
        
        print("Overlay window initialized")
    
    def set_translations(self, translations: List[Dict[str, Any]], region: Dict[str, int]):
        """
        Update the overlay with new translations.
        
        Args:
            translations: List of translation dictionaries with 'bbox', 'original', 'translated'
            region: Dictionary with 'x', 'y' for positioning
        """
        self.translations = translations
        self.region_offset = (region['x'], region['y'])
        
        # Trigger repaint
        self.update()
        
        # Auto-hide after 10 seconds
        self.hide_timer.start(10000)
        
        print(f"Displaying {len(translations)} translations")
    
    def clear_translations(self):
        """Clear all translations from the overlay"""
        self.translations = []
        self.update()
        print("Translations cleared")
    
    def paintEvent(self, event):
        """Draw translations on the overlay"""
        if not self.translations:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font)
        
        offset_x, offset_y = self.region_offset
        
        for trans in self.translations:
            bbox = trans['bbox']
            translated_text = trans['translated']
            
            # Calculate bounding box position
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            xs = [point[0] for point in bbox]
            ys = [point[1] for point in bbox]
            
            x = min(xs) + offset_x
            y = min(ys) + offset_y
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            
            # Draw semi-transparent background
            bg_color = QColor(0, 0, 0, 180)
            painter.fillRect(int(x), int(y), int(width), int(height), bg_color)
            
            # Draw border
            border_pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(border_pen)
            painter.drawRect(int(x), int(y), int(width), int(height))
            
            # Draw translated text
            text_pen = QPen(QColor(255, 255, 255))
            painter.setPen(text_pen)
            
            # Calculate text position (centered in bbox)
            text_rect = QRect(int(x), int(y), int(width), int(height))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, translated_text)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            self.clear_translations()
        elif event.key() == Qt.Key.Key_Space:
            # Request new translation
            self.translate_requested.emit()


class OverlayController:
    """
    Controller for managing the overlay window and processing results.
    """
    
    def __init__(self, result_queue):
        """
        Initialize the overlay controller.
        
        Args:
            result_queue: Queue to receive results from processing pipeline
        """
        self.result_queue = result_queue
        self.overlay = OverlayWindow()
        
        # Timer to check for results
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_results)
        self.check_timer.start(50)  # Check every 50ms
    
    def check_results(self):
        """Check for new results from the processing pipeline"""
        while not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
                self.handle_result(result)
            except:
                break
    
    def handle_result(self, result: Dict[str, Any]):
        """
        Handle a result from the processing pipeline.
        
        Args:
            result: Result dictionary from pipeline
        """
        result_type = result.get('type')
        
        if result_type == 'init_complete':
            translator_available = result.get('translator_available', False)
            if translator_available:
                print("✓ System ready - Translator available")
            else:
                print("⚠ System ready - Translator not available (will show original text)")
        
        elif result_type == 'init_error':
            print(f"✗ Initialization error: {result.get('error')}")
        
        elif result_type == 'result':
            texts = result.get('texts', [])
            region = result.get('region', {})
            timing = result.get('timing', {})
            
            if texts:
                self.overlay.set_translations(texts, region)
                print(f"Displayed {len(texts)} translations (total: {timing.get('total', 0):.3f}s)")
            else:
                print("No text detected in region")
        
        elif result_type == 'error':
            print(f"✗ Processing error: {result.get('error')}")
    
    def show(self):
        """Show the overlay window"""
        self.overlay.show()
    
    def hide(self):
        """Hide the overlay window"""
        self.overlay.hide()
