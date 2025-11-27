"""
Main entry point for Screen Translator application
"""

import sys
import os
import multiprocessing as mp
from multiprocessing import Queue
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget)
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
        # Don't show overlay on startup - only show when there are results
        # self.overlay_controller.show()
        
        # Snipping widget
        self.snipping_widget = None
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Create floating capture button
        from ui.capture_button import FloatingCaptureButton
        self.capture_button = FloatingCaptureButton(self.start_capture)
        self.capture_button.show()
        
        # Setup global hotkeys
        self.setup_hotkeys()
        
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
        
        # Capture full screen action
        fullscreen_action = QAction("🖥️ Capture Full Screen", self.app)
        fullscreen_action.triggered.connect(self.capture_full_screen)
        menu.addAction(fullscreen_action)
        
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
        
        # Hide overlay temporarily
        self.overlay_controller.hide()
        
        # Create and show snipping widget
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.region_selected.connect(self.on_region_selected)
        self.snipping_widget.show()
    
    def capture_full_screen(self):
        """Capture the entire screen and process it"""
        print("Capturing full screen...")
        
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
    
    def setup_hotkeys(self):
        """Setup global hotkeys for capture actions"""
        import json
        
        # Load hotkey configuration
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Region capture hotkey
                    region_hotkey = config.get('hotkey', 'Ctrl+J')
                    try:
                        self.region_hotkey_window = HotkeyWindow(region_hotkey, self.start_capture)
                        print(f"✓ Region capture hotkey: {region_hotkey}")
                    except Exception as e:
                        print(f"⚠ Could not register region hotkey '{region_hotkey}': {e}")
                        self.region_hotkey_window = None
                    
                    # Full screen capture hotkey
                    fullscreen_hotkey = config.get('fullscreen_hotkey', 'Ctrl+Shift+J')
                    try:
                        self.fullscreen_hotkey_window = HotkeyWindow(fullscreen_hotkey, self.capture_full_screen)
                        print(f"✓ Full screen capture hotkey: {fullscreen_hotkey}")
                    except Exception as e:
                        print(f"⚠ Could not register fullscreen hotkey '{fullscreen_hotkey}': {e}")
                        self.fullscreen_hotkey_window = None
            else:
                print("⚠ Config file not found, hotkeys not registered")
                self.region_hotkey_window = None
                self.fullscreen_hotkey_window = None
        except Exception as e:
            print(f"⚠ Error loading hotkey config: {e}")
            self.region_hotkey_window = None
            self.fullscreen_hotkey_window = None
    
    def quit_app(self):
        """Quit the application cleanly"""
        print("Shutting down...")
        
        # Close capture button
        try:
            if hasattr(self, 'capture_button'):
                self.capture_button.close()
        except:
            pass
        
        # Close hotkey windows
        try:
            if hasattr(self, 'region_hotkey_window') and self.region_hotkey_window:
                self.region_hotkey_window.close()
            if hasattr(self, 'fullscreen_hotkey_window') and self.fullscreen_hotkey_window:
                self.fullscreen_hotkey_window.close()
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


class HotkeyWindow(QWidget):
    """Hidden window to listen for global hotkey events"""
    
    def __init__(self, hotkey_str, callback):
        super().__init__()
        self.hotkey_str = hotkey_str
        self.callback = callback
        self.hotkey_id = 1
        
        # Window setup
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1, 1)
        self.show() # Must be shown to receive messages
        self.hide() # But we can hide it immediately
        
        self.register_hotkey()
        
    def register_hotkey(self):
        """Register the hotkey with Windows API"""
        import ctypes
        from ctypes import wintypes
        
        # Parse hotkey
        parts = [p.strip() for p in self.hotkey_str.split('+')]
        
        # Build modifier flags
        MOD_ALT = 0x0001
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        MOD_WIN = 0x0008
        
        modifiers = 0
        vk_code = None
        
        for part in parts:
            part_lower = part.lower()
            if part_lower in ('ctrl', 'control'):
                modifiers |= MOD_CONTROL
            elif part_lower == 'shift':
                modifiers |= MOD_SHIFT
            elif part_lower == 'alt':
                modifiers |= MOD_ALT
            elif part_lower == 'win':
                modifiers |= MOD_WIN
            else:
                # This is the key
                if len(part) == 1:
                    vk_code = ord(part.upper())
                elif part_lower.startswith('f') and len(part_lower) <= 3:
                    try:
                        f_num = int(part_lower[1:])
                        vk_code = 0x70 + f_num - 1
                    except:
                        pass
        
        if vk_code is None:
            print(f"⚠ Could not parse hotkey: {self.hotkey_str}")
            return
            
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            result = user32.RegisterHotKey(hwnd, self.hotkey_id, modifiers, vk_code)
            
            if result:
                print(f"✓ Global hotkey registered: {self.hotkey_str}")
            else:
                print(f"⚠ Failed to register hotkey (Error: {ctypes.get_last_error()})")
        except Exception as e:
            print(f"⚠ Error registering hotkey: {e}")

    def nativeEvent(self, eventType, message):
        """Handle native Windows events"""
        try:
            if eventType == "windows_generic_MSG":
                import ctypes
                from ctypes import wintypes
                
                # Get message structure
                if isinstance(message, int):
                    msg_addr = message
                else:
                    # In PyQt6, message might be a sip.voidptr
                    msg_addr = int(message)
                
                msg = ctypes.cast(msg_addr, ctypes.POINTER(wintypes.MSG)).contents
                
                # WM_HOTKEY = 0x0312
                if msg.message == 0x0312:
                    if msg.wParam == self.hotkey_id:
                        print(f"Hotkey triggered: {self.hotkey_str}")
                        self.callback()
                        return True, 0
        except Exception as e:
            print(f"Error in nativeEvent: {e}")
            
        return super().nativeEvent(eventType, message)
    
    def closeEvent(self, event):
        """Unregister hotkey on close"""
        import ctypes
        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.UnregisterHotKey(hwnd, self.hotkey_id)
        except:
            pass
        super().closeEvent(event)


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
