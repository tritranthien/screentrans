"""
Transparent overlay window for displaying translations in tooltip style
"""

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from typing import List, Dict, Any


class OverlayWindow(QMainWindow):
    """
    Tooltip-style window that displays all translations in a single box.
    """
    
    # Signal to request new translation
    translate_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Window setup - NOT fullscreen, NOT click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Translation data
        self.translations = []
        self.region_offset = (0, 0)
        
        # Tab state: 0 = Full Text (default), 1 = Word by Word
        self.current_tab = 0
        self.tab_rects = []  # Will store clickable areas for tabs
        
        # Font settings
        self.title_font = QFont("Arial", 10, QFont.Weight.Bold)
        self.text_font = QFont("Arial", 12)
        
        # Dragging state
        self.dragging = False
        self.drag_position = QPoint()
        
        # Close button area
        self.close_button_rect = QRect()
        
        # Initially hidden
        self.hide()
        
        print("Overlay window initialized")
    
    def set_translations(self, translations: List[Dict[str, Any]], region: Dict[str, int], full_translation: str = ""):
        """
        Update the overlay with new translations.
        
        Args:
            translations: List of individual word translations (for word-by-word view)
            region: Dictionary with 'x', 'y' for positioning
            full_translation: Full sentence translation (for full text view)
        """
        self.translations = translations
        self.region_offset = (region['x'], region['y'])
        self.full_translation = full_translation
        
        if translations:
            # Position window near the captured region
            dpr = self.devicePixelRatio()
            x = int(region['x'] / dpr)
            y = int(region['y'] / dpr)
            
            # Calculate window size based on content
            width = 500
            height = min(700, 60 + len(translations) * 60)  # Dynamic height
            
            # Make sure window is on screen
            screen = self.screen().geometry()
            if x + width > screen.width():
                x = screen.width() - width - 20
            if y + height > screen.height():
                y = screen.height() - height - 20
            
            self.setGeometry(x, y, width, height)
            self.show()
            self.raise_()
        
        print(f"Displaying {len(translations)} translations")
    
    def clear_translations(self):
        """Clear all translations and hide window"""
        self.translations = []
        self.hide()
        print("Translations cleared")
    
    def paintEvent(self, event):
        """Draw the tooltip-style translation window with tabs"""
        if not self.translations:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Draw main background
        bg_color = QColor(255, 255, 220, 250)  # Light yellow, almost opaque
        painter.fillRect(self.rect(), bg_color)
        
        # Draw border
        border_pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(border_pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
        # Draw title bar
        title_bg = QColor(255, 200, 0)
        painter.fillRect(0, 0, self.width(), 30, title_bg)
        painter.drawLine(0, 30, self.width(), 30)
        
        # Draw title text
        painter.setFont(self.title_font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(10, 20, f"Translations ({len(self.translations)})")
        
        # Draw close button (X)
        close_x = self.width() - 25
        close_y = 5
        self.close_button_rect = QRect(close_x, close_y, 20, 20)
        
        painter.fillRect(self.close_button_rect, QColor(255, 100, 100))
        painter.drawRect(self.close_button_rect)
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(close_x + 5, close_y + 5, close_x + 15, close_y + 15)
        painter.drawLine(close_x + 15, close_y + 5, close_x + 5, close_y + 15)
        
        # Draw tab buttons
        tab_width = 100
        tab_height = 25
        tab_y = 35
        
        self.tab_rects = []
        tab_labels = ["Nguyên câu", "Từng từ"]
        
        for i, label in enumerate(tab_labels):
            tab_x = 10 + i * (tab_width + 5)
            tab_rect = QRect(tab_x, tab_y, tab_width, tab_height)
            self.tab_rects.append(tab_rect)
            
            # Draw tab background
            if i == self.current_tab:
                # Active tab - bright
                painter.fillRect(tab_rect, QColor(255, 255, 100))
                painter.setPen(QPen(QColor(0, 0, 0), 2))
            else:
                # Inactive tab - dimmed
                painter.fillRect(tab_rect, QColor(220, 220, 150))
                painter.setPen(QPen(QColor(100, 100, 100), 1))
            
            painter.drawRect(tab_rect)
            
            # Draw tab label
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(tab_rect, Qt.AlignmentFlag.AlignCenter, label)
        
        # Draw content based on current tab
        content_y = tab_y + tab_height + 15
        
        if self.current_tab == 0:
            # Tab 0: Full Text - combine all translations into one paragraph
            self._draw_full_text_tab(painter, content_y)
        else:
            # Tab 1: Word by Word - show individual translations
            self._draw_word_by_word_tab(painter, content_y)
    
    def _draw_full_text_tab(self, painter, start_y):
        """Draw the full text translation tab"""
        # Combine all original texts
        original_texts = [trans['original'] for trans in self.translations]
        full_original = " ".join(original_texts)
        
        # Use the full translation from pipeline (not combined individual translations)
        full_translated = self.full_translation if hasattr(self, 'full_translation') else full_original
        
        # Draw original text
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor(100, 100, 100))
        
        original_rect = QRect(15, start_y, self.width() - 30, 80)
        painter.drawText(original_rect, Qt.TextFlag.TextWordWrap, f"Gốc: {full_original}")
        
        # Draw separator
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(15, start_y + 85, self.width() - 15, start_y + 85)
        
        # Draw translated text
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QColor(0, 0, 0))
        
        translated_rect = QRect(15, start_y + 95, self.width() - 30, self.height() - start_y - 110)
        painter.drawText(translated_rect, Qt.TextFlag.TextWordWrap, f"Dịch: {full_translated}")
    
    def _draw_word_by_word_tab(self, painter, start_y):
        """Draw the word-by-word translation tab"""
        painter.setFont(self.text_font)
        painter.setPen(QColor(0, 0, 0))
        
        y_offset = start_y
        for i, trans in enumerate(self.translations):
            original = trans['original']
            translated = trans['translated']
            
            # Draw original text (gray, smaller)
            painter.setFont(QFont("Arial", 9))
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(15, y_offset, f"{i+1}. {original}")
            
            # Draw translated text (black, bold, larger)
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRect(15, y_offset + 5, self.width() - 30, 50)
            painter.drawText(text_rect, Qt.TextFlag.TextWordWrap, f"   → {translated}")
            
            y_offset += 60
            
            # Draw separator line
            if i < len(self.translations) - 1:
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                painter.drawLine(15, y_offset - 5, self.width() - 15, y_offset - 5)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging, close button, and tab switching"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on close button
            if self.close_button_rect.contains(event.pos()):
                self.clear_translations()
                return
            
            # Check if clicked on a tab
            for i, tab_rect in enumerate(self.tab_rects):
                if tab_rect.contains(event.pos()):
                    if self.current_tab != i:
                        self.current_tab = i
                        self.update()  # Repaint to show new tab
                    return
            
            # Check if clicked on title bar (for dragging)
            if event.pos().y() < 30:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
    
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
            full_translation = result.get('full_translation', '')
            
            if texts:
                self.overlay.set_translations(texts, region, full_translation)
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
