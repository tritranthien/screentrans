"""
Floating capture button widget
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QAction, QPen, QLinearGradient


class FloatingCaptureButton(QWidget):
    """A floating button that stays on top for quick capture"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.dragging = False
        self.hovered = False
        self.pressed = False
        
        self.offset = QPoint()
        self.drag_start_pos = QPoint()
        self.drag_start_global = QPoint()
        self.widget_start_pos = QPoint()
        self.click_pos = QPoint()
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)  # Enable mouse tracking
        
        # Set initial opacity (15% transparent)
        self.setWindowOpacity(0.25)
        
        # Set window size
        self.setFixedSize(50, 50)
        self.setToolTip("Left-click: Capture\nRight-click: Menu\nDrag to move")
        
        # Position at bottom-right corner
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 100, screen.height() - 100)
        
    def paintEvent(self, event):
        """Custom paint for the button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine colors based on state
        if self.pressed:
            bg_color = QColor(240, 240, 240, 200)
            icon_color = QColor("#000000")
        elif self.hovered:
            bg_color = QColor(255, 255, 255, 220)
            icon_color = QColor("#333333")
        else:
            bg_color = QColor(255, 255, 255, 150)
            icon_color = QColor("#555555")
            
        # Draw circle background
        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor(200, 200, 200, 150), 1))  # Subtle border
        painter.drawEllipse(2, 2, 46, 46)
        
        # Draw "Scan/Crop" Icon
        painter.setPen(QPen(icon_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        # Icon dimensions
        m = 14  # margin
        s = 50  # size
        
        # Top-Left corner
        painter.drawLine(m, m + 7, m, m)
        painter.drawLine(m, m, m + 7, m)
        
        # Top-Right corner
        painter.drawLine(s - m - 7, m, s - m, m)
        painter.drawLine(s - m, m, s - m, m + 7)
        
        # Bottom-Left corner
        painter.drawLine(m, s - m - 7, m, s - m)
        painter.drawLine(m, s - m, m + 7, s - m)
        
        # Bottom-Right corner
        painter.drawLine(s - m - 7, s - m, s - m, s - m)
        painter.drawLine(s - m, s - m, s - m, s - m - 7)
        
        # Center dot/lens
        painter.setBrush(icon_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(23, 23, 4, 4)
    
    def enterEvent(self, event):
        """Make button fully visible on hover"""
        self.hovered = True
        self.setWindowOpacity(1.0)
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Make button semi-transparent when not hovering"""
        self.hovered = False
        self.setWindowOpacity(0.15)  # More transparent when idle
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Start dragging or show context menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            self.update()
            
            # Store initial positions
            self.drag_start_global = event.globalPosition().toPoint()
            self.widget_start_pos = self.pos()
            self.click_pos = event.pos()
            self.dragging = False
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
    
    def mouseMoveEvent(self, event):
        """Handle dragging"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_global = event.globalPosition().toPoint()
            delta = current_global - self.drag_start_global
            
            # Start dragging immediately on any movement
            if delta.manhattanLength() > 0:
                self.dragging = True
                new_pos = self.widget_start_pos + delta
                self.move(new_pos)
    
    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = False
            self.update()
            
            # If we didn't drag, treat it as a click
            if not self.dragging:
                self.on_click()
            
            self.dragging = False
    
    def on_click(self):
        """Handle button click - only trigger if not dragging"""
        self.callback()
    
    def show_context_menu(self, pos):
        """Show context menu on right-click"""
        menu = QMenu()
        
        hide_action = QAction("🙈 Hide Button", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)
        
        menu.exec(pos)
