from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QAction
from typing import List, Dict, Any


class ParagraphCard(QWidget):
    """Custom card widget that shows copy button on hover"""
    
    def __init__(self, text, formatted_text, copy_callback, parent=None):
        super().__init__(parent)
        self.text = text
        self.copy_callback = copy_callback
        
        self.setStyleSheet("""
            ParagraphCard {
                background: rgba(255, 255, 255, 150);
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with copy button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedSize(50, 20)
        self.copy_btn.setStyleSheet("font-size: 9px; padding: 2px; background: #4CAF50; color: white; border-radius: 3px;")
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        self.copy_btn.hide()  # Hidden by default
        header_layout.addWidget(self.copy_btn)
        
        layout.addWidget(header)
        
        # Paragraph text
        para_label = QLabel()
        para_label.setFont(QFont("Arial", 10))
        para_label.setStyleSheet("background: transparent; color: #000;")
        para_label.setWordWrap(True)
        para_label.setTextFormat(Qt.TextFormat.RichText)
        para_label.setText(f"<div style='line-height: 1.3;'>{formatted_text}</div>")
        para_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(para_label)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def enterEvent(self, event):
        """Show copy button when mouse enters"""
        self.copy_btn.show()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide copy button when mouse leaves"""
        self.copy_btn.hide()
        super().leaveEvent(event)
    
    def on_copy_clicked(self):
        """Handle copy button click"""
        self.copy_callback(self.text, self.copy_btn)

class OverlayWindow(QMainWindow):
    """
    Tooltip-style window that displays translations.
    Uses widgets for content to support scrolling and text selection.
    """
    
    # Signal to request new translation
    translate_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.central_widget.setStyleSheet("""
            #centralWidget {
                background-color: rgba(255, 255, 220, 250);
                border: 2px solid black;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: transparent;
                border: none;
                color: black;
            }
            QPushButton#tabButton {
                background-color: rgba(220, 220, 150, 255);
                border: 1px solid gray;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton#tabButton:checked {
                background-color: rgba(255, 255, 100, 255);
                border: 2px solid black;
            }
            QPushButton#closeButton {
                background-color: #ff6464;
                border: 1px solid #cc0000;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            QPushButton#closeButton:hover {
                background-color: #ff0000;
            }
        """)
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        # Title bar area (custom)
        self.title_layout = QHBoxLayout()
        
        self.title_label = QLabel("Translations")
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_layout.addWidget(self.title_label)
        
        self.title_layout.addStretch()
        
        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.clear_translations)
        self.title_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(self.title_layout)
        
        # Title bar controls (minimize, maximize, close)
        controls_layout = QHBoxLayout()
        
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("closeButton")
        self.minimize_btn.setFixedSize(24, 24)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("closeButton")
        self.maximize_btn.setFixedSize(24, 24)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.maximize_btn)
        controls_layout.addWidget(self.close_btn)
        
        self.title_layout.addLayout(controls_layout)
        
        # Content area (no tabs, just the main view)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # Section: Original
        self.original_header = QWidget()
        oh_layout = QHBoxLayout(self.original_header)
        oh_layout.setContentsMargins(0, 0, 0, 0)
        oh_label = QLabel("Gốc:")
        oh_label.setStyleSheet("color: #555; font-weight: bold; font-size: 10pt;")
        self.copy_original_btn = QPushButton("Copy")
        self.copy_original_btn.setFixedSize(50, 20)
        self.copy_original_btn.setStyleSheet("font-size: 9px; padding: 2px;")
        self.copy_original_btn.clicked.connect(lambda: self.copy_text(self.full_original_text, self.copy_original_btn))
        oh_layout.addWidget(oh_label)
        oh_layout.addStretch()
        oh_layout.addWidget(self.copy_original_btn)
        content_layout.addWidget(self.original_header)
        
        self.original_edit = QTextEdit()
        self.original_edit.setReadOnly(True)
        self.original_edit.setMaximumHeight(70)
        self.original_edit.setFont(QFont("Arial", 9))
        self.original_edit.setStyleSheet("color: #555; background: rgba(255,255,255,100); border: 1px solid #ccc;")
        content_layout.addWidget(self.original_edit)
        
        # Section: Translated (single text area)
        self.translated_container = QWidget()
        self.translated_layout = QVBoxLayout(self.translated_container)
        self.translated_layout.setContentsMargins(0, 10, 0, 0)
        self.translated_layout.setSpacing(5)
        
        # Header for translated section with Copy All button
        translated_main_header = QWidget()
        tmh_layout = QHBoxLayout(translated_main_header)
        tmh_layout.setContentsMargins(0, 0, 0, 0)
        tmh_label = QLabel("Dịch:")
        tmh_label.setStyleSheet("color: #000; font-weight: bold; font-size: 10pt;")
        tmh_layout.addWidget(tmh_label)
        tmh_layout.addStretch()
        
        self.copy_all_btn = QPushButton("Copy All")
        self.copy_all_btn.setFixedSize(60, 20)
        self.copy_all_btn.setStyleSheet("font-size: 9px; padding: 2px; background: #4CAF50; color: white; border-radius: 3px;")
        self.copy_all_btn.clicked.connect(lambda: self.copy_text(self.full_translated_text, self.copy_all_btn))
        tmh_layout.addWidget(self.copy_all_btn)
        
        self.translated_layout.addWidget(translated_main_header)
        
        # Single text edit for all translated content
        self.translated_edit = QTextEdit()
        self.translated_edit.setReadOnly(True)
        self.translated_edit.setFont(QFont("Arial", 10))
        self.translated_edit.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 150);
                border: 1px solid #ddd;
                border-radius: 5px;
                color: #000;
                padding: 8px;
            }
        """)
        self.translated_layout.addWidget(self.translated_edit)
        
        content_layout.addWidget(self.translated_container)
        
        # Add content to main layout
        self.layout.addWidget(content_widget)
        
        # Dragging state
        self.dragging = False
        self.drag_position = QPoint()
        
        # Maximize state
        self.is_maximized = False
        self.normal_geometry = None
        
        # Data
        self.translations = []
        self.full_original_text = ""
        self.full_translated_text = ""
        
        # Initially hidden
        self.hide()
        print("Overlay window initialized")

    def toggle_maximize(self):
        """Toggle between maximized and normal size"""
        if self.is_maximized:
            # Restore to normal
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_maximized = False
            self.maximize_btn.setText("□")
        else:
            # Save current geometry and maximize
            self.normal_geometry = self.geometry()
            screen = self.screen().geometry()
            self.setGeometry(screen)
            self.is_maximized = True
            self.maximize_btn.setText("❐")
        
    def copy_text(self, text, button=None):
        """Copy text to clipboard with visual feedback"""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        
        # Visual feedback
        if button:
            original_text = button.text()
            original_style = button.styleSheet()
            
            button.setText("✓ Copied!")
            button.setStyleSheet("font-size: 9px; padding: 2px; background: #4CAF50; color: white; border-radius: 3px;")
            
            # Reset after 1.5 seconds
            QTimer.singleShot(1500, lambda: self._reset_copy_button(button, original_text, original_style))
        
        print("Text copied to clipboard")
    
    def _reset_copy_button(self, button, original_text, original_style):
        """Reset copy button to original state"""
        if button:
            button.setText(original_text)
            button.setStyleSheet(original_style)

    def set_translations(self, translations: List[Dict[str, Any]], region: Dict[str, int], full_translation: str = ""):
        """Update translations and show window"""
        self.translations = translations
        
        # Update Full Text Page
        original_texts = [trans['original'] for trans in translations]
        self.full_original_text = " ".join(original_texts)
        self.full_translated_text = full_translation
        
        self.original_edit.setPlainText(self.full_original_text)
        
        # Format translation for HTML display
        import re
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in full_translation.split('\n') if p.strip()]
        
        # Format each paragraph (handle bold markdown)
        formatted_paragraphs = []
        for para in paragraphs:
            formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', para)
            formatted_paragraphs.append(f"<p style='margin-bottom: 12px; line-height: 1.4;'>{formatted}</p>")
        
        # Combine all paragraphs
        html_content = "\n".join(formatted_paragraphs)
        
        self.translated_edit.setHtml(html_content)
        
        # Position and Resize
        if translations:
            dpr = self.devicePixelRatio()
            x = int(region['x'] / dpr)
            y = int(region['y'] / dpr)
            
            width = 500
            height = 400  # Fixed height, scrollable content
            
            screen = self.screen().geometry()
            if x + width > screen.width():
                x = screen.width() - width - 20
            if y + height > screen.height():
                y = screen.height() - height - 20
            
            self.setGeometry(x, y, width, height)
            self.title_label.setText(f"Translations ({len(translations)})")
            self.show()
            self.raise_()

    def show_loading(self, x, y, width, height):
        """Show loading state"""
        self.original_edit.setPlainText("Processing...")
        self.translated_edit.setHtml("<div style='text-align: center; color: #666; margin-top: 20px;'><h3>⟳ Translating...</h3></div>")
        
        # Position near the region
        dpr = self.devicePixelRatio()
        win_x = int(x / dpr)
        win_y = int(y / dpr)
        
        win_width = 400
        win_height = 200
        
        screen = self.screen().geometry()
        if win_x + win_width > screen.width():
            win_x = screen.width() - win_width - 20
        if win_y + win_height > screen.height():
            win_y = screen.height() - win_height - 20
            
        self.setGeometry(win_x, win_y, win_width, win_height)
        self.title_label.setText("Translating...")
        self.show()
        self.raise_()

    def clear_translations(self):
        """Clear and hide"""
        self.hide()
    
    # Remove custom paintEvent since we use widgets now
    
    def mousePressEvent(self, event):
        """Handle dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only drag if clicked on background/title, not on buttons/text
            child = self.childAt(event.pos())
            if child is self.central_widget or child is self.title_label:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False


class LoadingWidget(QWidget):
    """Small floating widget to show loading state"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("⏳")
        self.label.setFont(QFont("Segoe UI Emoji", 20))
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(40, 40)
        
        layout.addWidget(self.label)
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.angle = 0
        
    def animate(self):
        self.angle = (self.angle + 30) % 360
        # Simple text animation since we can't easily rotate the label widget itself without QGraphicsView
        chars = ["⏳", "⌛"]
        self.label.setText(chars[(self.angle // 30) % 2])

    def show_at(self, x, y):
        self.move(x, y)
        self.show()
        self.timer.start(500)
        
    def stop(self):
        self.hide()
        self.timer.stop()


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
        self.loading_widget = LoadingWidget()
        
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
        # Hide loading indicator when we get any result
        self.loading_widget.stop()
        
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
                # Show overlay briefly to say no text found
                self.overlay.translated_edit.setHtml("<div style='text-align: center; color: #666;'>No text found</div>")
                # Position it roughly where the loading was
                self.overlay.setGeometry(self.loading_widget.x(), self.loading_widget.y(), 300, 100)
                self.overlay.show()
        
        elif result_type == 'error':
            print(f"✗ Processing error: {result.get('error')}")
            self.overlay.translated_edit.setHtml(f"<div style='color: red;'>Error: {result.get('error')}</div>")
            self.overlay.show()
    
    def show(self):
        """Show the overlay window"""
        self.overlay.show()
    
    def show_loading(self, x, y, width, height):
        """Show loading indicator"""
        # Calculate center of region
        dpr = self.overlay.devicePixelRatio()
        center_x = int((x + width/2) / dpr)
        center_y = int((y + height/2) / dpr)
        
        # Show loading widget centered on region
        self.loading_widget.show_at(center_x - 20, center_y - 20)
        
        # Hide the main overlay if it's open
        self.overlay.hide()
    
    def hide(self):
        """Hide the overlay window"""
        self.overlay.hide()
        self.loading_widget.stop()
