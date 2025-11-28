"""
Floating capture button widget
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QAction, QPen, QLinearGradient


class FloatingCaptureButton(QWidget):
    """A floating button that stays on top for quick capture"""
    
    def __init__(self, capture_callback, ask_callback):
        super().__init__()
        self.capture_callback = capture_callback
        self.ask_callback = ask_callback
        self.dragging = False
        self.hovered = False
        self.pressed = False
        self.pressed_section = None # 'capture' or 'ask'
        
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
        
        # Set initial opacity (25% transparent)
        self.setWindowOpacity(0.25)
        
        # Set window size (Capsule shape)
        self.width = 90
        self.height = 40
        self.setFixedSize(self.width, self.height)
        self.setToolTip("Left: Capture Region\nRight: Capture & Ask\nDrag to move")
        
        # Position at bottom-right corner
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 150, screen.height() - 100)
        
    def paintEvent(self, event):
        """Custom paint for the button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine colors based on state
        if self.hovered:
            bg_color = QColor(255, 255, 255, 230)
            icon_color = QColor("#333333")
            border_color = QColor(200, 200, 200, 200)
        else:
            bg_color = QColor(255, 255, 255, 150)
            icon_color = QColor("#555555")
            border_color = QColor(200, 200, 200, 100)
            
        # Draw capsule background
        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(1, 1, self.width-2, self.height-2, self.height//2, self.height//2)
        
        # Draw separator line
        painter.setPen(QPen(border_color, 1))
        painter.drawLine(self.width//2, 8, self.width//2, self.height-8)
        
        # Draw "Scan/Crop" Icon (Left side)
        # Highlight if pressed
        if self.pressed and self.pressed_section == 'capture':
            painter.setPen(QPen(QColor("#3D5AFE"), 2))
        else:
            painter.setPen(QPen(icon_color, 2))
            
        # Icon dimensions for Capture (smaller now)
        cx = self.width // 4
        cy = self.height // 2
        sz = 8 # half size
        
        # Corners
        painter.drawLine(cx - sz, cy - sz, cx - sz + 4, cy - sz) # Top-Left H
        painter.drawLine(cx - sz, cy - sz, cx - sz, cy - sz + 4) # Top-Left V
        
        painter.drawLine(cx + sz, cy - sz, cx + sz - 4, cy - sz) # Top-Right H
        painter.drawLine(cx + sz, cy - sz, cx + sz, cy - sz + 4) # Top-Right V
        
        painter.drawLine(cx - sz, cy + sz, cx - sz + 4, cy + sz) # Bottom-Left H
        painter.drawLine(cx - sz, cy + sz, cx - sz, cy + sz - 4) # Bottom-Left V
        
        painter.drawLine(cx + sz, cy + sz, cx + sz - 4, cy + sz) # Bottom-Right H
        painter.drawLine(cx + sz, cy + sz, cx + sz, cy + sz - 4) # Bottom-Right V
        
        # Draw "Question" Icon (Right side)
        # Highlight if pressed
        if self.pressed and self.pressed_section == 'ask':
            painter.setPen(QPen(QColor("#651FFF"), 2))
        else:
            painter.setPen(QPen(icon_color, 2))
            
        qx = (self.width * 3) // 4
        qy = self.height // 2
        
        # Draw question mark (simplified)
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(qx - 10, qy - 10, 20, 20, Qt.AlignmentFlag.AlignCenter, "?")
    
    def enterEvent(self, event):
        """Make button fully visible on hover"""
        self.hovered = True
        self.setWindowOpacity(1.0)
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Make button semi-transparent when not hovering"""
        self.hovered = False
        self.setWindowOpacity(0.25)  # More transparent when idle
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Start dragging or show context menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            
            # Determine which section was pressed
            if event.pos().x() < self.width / 2:
                self.pressed_section = 'capture'
            else:
                self.pressed_section = 'ask'
                
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
                self.on_click(event.pos())
            
            self.dragging = False
            self.pressed_section = None
    
    def on_click(self, pos):
        """Handle button click based on position"""
        if pos.x() < self.width / 2:
            # Left side: Capture
            self.capture_callback()
        else:
            # Right side: Ask
            self.ask_callback()
    
    def show_context_menu(self, pos):
        """Show context menu on right-click"""
        menu = QMenu()
        
        hide_action = QAction("🙈 Hide Button", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)
        
        menu.exec(pos)
