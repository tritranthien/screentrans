"""
Snipping tool for selecting screen regions
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QScreen
import sys


class SnippingWidget(QWidget):
    """
    Transparent overlay widget for selecting screen regions.
    Similar to Windows Snipping Tool.
    """
    
    # Signal emitted when region is selected (x, y, width, height)
    region_selected = pyqtSignal(int, int, int, int)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Selection state
        self.start_pos = None
        self.end_pos = None
        self.selecting = False
        
        # Make fullscreen
        self.showFullScreen()
        
        # Set cursor
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def paintEvent(self, event):
        """Draw the selection rectangle"""
        painter = QPainter(self)
        
        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # If we have a selection, draw it
        if self.start_pos and self.end_pos:
            # Calculate selection rectangle
            rect = QRect(self.start_pos, self.end_pos).normalized()
            
            # Clear the selected area (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            
            # Draw border around selection
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # Draw corner handles
            handle_size = 8
            painter.setBrush(QBrush(QColor(0, 120, 215)))
            
            # Top-left
            painter.drawRect(rect.x() - handle_size // 2, rect.y() - handle_size // 2, 
                           handle_size, handle_size)
            # Top-right
            painter.drawRect(rect.right() - handle_size // 2, rect.y() - handle_size // 2,
                           handle_size, handle_size)
            # Bottom-left
            painter.drawRect(rect.x() - handle_size // 2, rect.bottom() - handle_size // 2,
                           handle_size, handle_size)
            # Bottom-right
            painter.drawRect(rect.right() - handle_size // 2, rect.bottom() - handle_size // 2,
                           handle_size, handle_size)
    
    def mousePressEvent(self, event):
        """Start selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"DEBUG: Mouse press at {event.pos()}")
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.selecting = True
            self.update()
    
    def mouseMoveEvent(self, event):
        """Update selection"""
        if self.selecting:
            self.end_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Finish selection"""
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            print(f"DEBUG: Mouse release at {event.pos()}")
            self.selecting = False
            self.end_pos = event.pos()
            
            # Calculate final rectangle
            rect = QRect(self.start_pos, self.end_pos).normalized()
            print(f"DEBUG: Selection rect: {rect}, size: {rect.width()}x{rect.height()}")
            
            # Only emit if we have a valid selection (at least 10x10 pixels)
            if rect.width() >= 10 and rect.height() >= 10:
                print("DEBUG: Emitting region_selected")
                self.region_selected.emit(rect.x(), rect.y(), rect.width(), rect.height())
            else:
                print("DEBUG: Selection too small, ignoring")
            
            # Close the snipping widget
            self.close()
    
    def keyPressEvent(self, event):
        """Handle escape key to cancel"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()


def select_region():
    """
    Show the snipping tool and return the selected region.
    This is a blocking function that returns when selection is complete.
    
    Returns:
        tuple: (x, y, width, height) or None if cancelled
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    selected_region = [None]
    
    def on_region_selected(x, y, w, h):
        selected_region[0] = (x, y, w, h)
    
    snipping = SnippingWidget()
    snipping.region_selected.connect(on_region_selected)
    snipping.show()
    
    # Wait for the widget to close
    snipping.exec() if hasattr(snipping, 'exec') else app.exec()
    
    return selected_region[0]
