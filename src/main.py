"""
Main entry point for Screen Translator application
"""

import sys
import os
import multiprocessing as mp
from multiprocessing import Queue
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, QDialog)
from PyQt6.QtGui import QIcon, QAction, QCursor, QPixmap, QPainter, QLinearGradient, QFont, QColor
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt

# Enable High DPI scaling
if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

# Set environment variable for Windows DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Fix imports for PyInstaller
if getattr(sys, 'frozen', False):
    # If running as compiled exe
    base_path = sys._MEIPASS
    # Add src directory to path so imports work
    sys.path.insert(0, os.path.join(base_path, 'src'))
else:
    # If running as script
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_path)

from pipeline import ProcessingPipeline
from ui.overlay import OverlayController
from ui.prompt_dialog import PromptDialog
from ui.snipping import SnippingWidget

class ScreenTranslatorApp:
    """
    Main application class that coordinates all components.
    """
    
    def __init__(self, source_lang="en", target_lang="vi"):
        """
        Initialize the application.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.is_scrolling_capture = False
        self.is_prompt_capture = False
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create communication queues
        self.command_queue = Queue()
        self.result_queue = Queue()
        
        # Start processing pipeline in separate process
        self.pipeline = ProcessingPipeline(
            self.command_queue,
            self.result_queue,
            source_lang=source_lang,
            target_lang=target_lang
        )
        self.pipeline.start()
        
        # Create overlay controller
        self.overlay_controller = OverlayController(self.result_queue)
        
        # Snipping widget
        self.snipping_widget = None
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Create floating capture button
        from ui.capture_button import FloatingCaptureButton
        self.capture_button = FloatingCaptureButton(self.start_capture, self.start_prompt_capture)
        self.capture_button.show()
        
        print("Screen Translator started")
        print("Click the floating button or use tray menu to capture")
        print("Right-click the tray icon for options")
    
    def create_tray_icon(self):
        """Create system tray icon with menu"""
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Create custom icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        gradient = QLinearGradient(0, 0, 64, 64)
        gradient.setColorAt(0, QColor("#3D5AFE"))
        gradient.setColorAt(1, QColor("#651FFF"))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
        
        # Draw "文" (Language symbol)
        painter.setPen(QColor("white"))
        font = QFont("Arial", 32, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "文")
        
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create menu
        menu = QMenu()
        
        # Capture region action
        capture_action = QAction("📸 Capture Region", self.app)
        capture_action.triggered.connect(self.start_capture)
        menu.addAction(capture_action)
        
        # Capture & Ask action
        ask_action = QAction("❓ Capture & Ask", self.app)
        ask_action.triggered.connect(self.start_prompt_capture)
        menu.addAction(ask_action)
        
        fullscreen_action = QAction("🖥️ Capture Full Screen", self.app)
        fullscreen_action.triggered.connect(self.capture_full_screen)
        menu.addAction(fullscreen_action)
        
        # Scrolling capture action
        scroll_action = QAction("📜 Scrolling Capture", self.app)
        scroll_action.triggered.connect(self.start_scrolling_capture)
        menu.addAction(scroll_action)
        
        menu.addSeparator()
        
        # Toggle capture button visibility
        self.toggle_button_action = QAction("👁 Show/Hide Capture Button", self.app)
        self.toggle_button_action.triggered.connect(self.toggle_capture_button)
        menu.addAction(self.toggle_button_action)
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self.app)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        # Clear translations action
        clear_action = QAction("🗑️ Clear Translations", self.app)
        clear_action.triggered.connect(self.overlay_controller.overlay.clear_translations)
        menu.addAction(clear_action)
        
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
        print("Starting region capture...")
        self.is_scrolling_capture = False
        self.is_prompt_capture = False
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()
    
    def start_prompt_capture(self):
        """Start capture with prompt dialog"""
        print("Starting capture & ask...")
        self.is_scrolling_capture = False
        self.is_prompt_capture = True
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()

    def start_scrolling_capture(self):
        """Start the scrolling region selection process"""
        print("Starting scrolling capture...")
        self.is_scrolling_capture = True
        self.is_prompt_capture = False
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()
    
    def capture_full_screen(self):
        """Capture the entire screen and process it"""
        print("Capturing full screen...")
        self.is_scrolling_capture = False
        self.is_prompt_capture = False
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Get screen geometry
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        device_pixel_ratio = screen.devicePixelRatio()
        
        # Calculate physical coordinates
        x = 0
        y = 0
        width = geometry.width()
        height = geometry.height()
        
        print(f"Full screen size (logical): {width}x{height}")
        
        # Process the full screen region
        self.on_region_selected(x, y, width, height)
    
    def open_settings(self):
        """Open settings dialog"""
        from ui.settings import SettingsDialog
        
        dialog = SettingsDialog()
        dialog.settings_saved.connect(self.on_settings_saved)
        dialog.exec()
    
    def on_settings_saved(self):
        """Handle settings saved event"""
        print("Settings saved, reloading configuration...")
        
        # Reload config to get new languages
        import json
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.source_lang = config.get('source_lang', self.source_lang)
                    self.target_lang = config.get('target_lang', self.target_lang)
                    print(f"Updated languages: {self.source_lang} -> {self.target_lang}")
        except Exception as e:
            print(f"Error reloading config in main app: {e}")
            
        # Send reload command to pipeline
        self.command_queue.put({'type': 'reload_config'})
    
    def toggle_capture_button(self):
        """Toggle capture button visibility"""
        if self.capture_button.isVisible():
            self.capture_button.hide()
        else:
            self.capture_button.show()
    
    def on_region_selected(self, x, y, width, height):
        """
        Handle region selection from snipping tool.
        
        Args:
            x, y: Top-left corner coordinates (logical pixels)
            width, height: Region dimensions (logical pixels)
        """
        print(f"DEBUG: Region selected (logical): ({x}, {y}, {width}, {height})")
        
        if width <= 0 or height <= 0:
            print("DEBUG: Invalid region dimensions!")
            return

        # Handle Prompt Capture
        prompt = None
        if self.is_prompt_capture:
            dialog = PromptDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                prompt = dialog.get_prompt()
                print(f"User prompt: {prompt}")
            else:
                print("Capture cancelled by user")
                return

        # Show overlay with loading state
        self.overlay_controller.show_loading(x, y, width, height)
        print("DEBUG: Overlay shown (loading)")
        
        # Calculate DPI scale factor
        screen = QApplication.primaryScreen()
        device_pixel_ratio = screen.devicePixelRatio()
        print(f"DEBUG: Device Pixel Ratio: {device_pixel_ratio}")
        
        # Adjust coordinates for High DPI displays
        x_phys = int(x * device_pixel_ratio)
        y_phys = int(y * device_pixel_ratio)
        w_phys = int(width * device_pixel_ratio)
        h_phys = int(height * device_pixel_ratio)
        
        print(f"DEBUG: Region (physical): ({x_phys}, {y_phys}, {w_phys}, {h_phys})")
        
        # Send command to processing pipeline
        command_type = 'process_scrolling_region' if self.is_scrolling_capture else 'process_region'
        command = {
            'type': command_type,
            'region': {
                'x': x_phys,
                'y': y_phys,
                'width': w_phys,
                'height': h_phys
            },
            'prompt': prompt
        }
        self.command_queue.put(command)
        
        print(f"DEBUG: Processing request sent to pipeline: {command}")
    

    
    def quit_app(self):
        """Quit the application cleanly"""
        print("Shutting down...")
        
        # Close capture button
        try:
            if hasattr(self, 'capture_button'):
                self.capture_button.close()
        except:
            pass
        

        
        # Send shutdown command to pipeline
        self.command_queue.put({'type': 'shutdown'})
        
        # Wait for pipeline to finish
        self.pipeline.join(timeout=2)
        
        # Quit Qt application
        self.app.quit()
    
    
    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    # Required for multiprocessing on Windows
    mp.freeze_support()
    
    # Parse command line arguments for language selection
    import argparse
    parser = argparse.ArgumentParser(description='Screen Translator')
    parser.add_argument('--source', default='en', help='Source language code (default: en)')
    parser.add_argument('--target', default='vi', help='Target language code (default: vi)')
    args = parser.parse_args()
    
    # Create and run application
    app = ScreenTranslatorApp(source_lang=args.source, target_lang=args.target)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
