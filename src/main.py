"""
Main entry point for Screen Translator application
"""

import sys
import os
import multiprocessing as mp
from multiprocessing import Queue
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QAction, QKeySequence

# Enable High DPI scaling
if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

# Set environment variable for Windows DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from pipeline import ProcessingPipeline
from ui.overlay import OverlayController
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
        self.overlay_controller.show()
        
        # Snipping widget
        self.snipping_widget = None
        
        # Create system tray icon
        self.create_tray_icon()
        
        print("Screen Translator started")
        print("Press Ctrl+Shift+S to capture and translate a region")
        print("Right-click the tray icon for options")
    
    def create_tray_icon(self):
        """Create system tray icon with menu"""
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Create icon (you can replace this with a custom icon file)
        # For now, using a simple colored icon
        from PyQt6.QtGui import QPixmap, QPainter
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
        capture_action = QAction("📸 Capture Region (Ctrl+Shift+S)", self.app)
        capture_action.triggered.connect(self.start_capture)
        menu.addAction(capture_action)
        
        menu.addSeparator()
        
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
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()
    
    def open_settings(self):
        """Open settings dialog"""
        from ui.settings import SettingsDialog
        
        dialog = SettingsDialog()
        dialog.exec()
    
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

        # Show overlay again
        self.overlay_controller.show()
        print("DEBUG: Overlay shown")
        
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
        command = {
            'type': 'process_region',
            'region': {
                'x': x_phys,
                'y': y_phys,
                'width': w_phys,
                'height': h_phys
            }
        }
        self.command_queue.put(command)
        
        print(f"DEBUG: Processing request sent to pipeline: {command}")
    
    def quit_app(self):
        """Quit the application cleanly"""
        print("Shutting down...")
        
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
