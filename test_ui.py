"""
Simple UI test without OCR/Translation
"""

import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter

# Test imports
print("Testing imports...")
print("✓ PyQt6 imported successfully")

try:
    import mss
    print("✓ mss imported successfully")
except Exception as e:
    print(f"✗ mss import failed: {e}")

try:
    import cv2
    print("✓ opencv imported successfully")
except Exception as e:
    print(f"✗ opencv import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except Exception as e:
    print(f"✗ numpy import failed: {e}")

print("\nStarting UI test...")

app = QApplication(sys.argv)

# Create simple tray icon
tray_icon = QSystemTrayIcon()

# Create icon
pixmap = QPixmap(64, 64)
pixmap.fill(Qt.GlobalColor.transparent)
painter = QPainter(pixmap)
painter.setBrush(Qt.GlobalColor.blue)
painter.drawEllipse(8, 8, 48, 48)
painter.end()

icon = QIcon(pixmap)
tray_icon.setIcon(icon)

# Create menu
menu = QMenu()

test_action = QAction("Test - Click Me!", None)
test_action.triggered.connect(lambda: QMessageBox.information(None, "Success!", "UI is working! 🎉"))
menu.addAction(test_action)

menu.addSeparator()

quit_action = QAction("Quit", None)
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)

tray_icon.setContextMenu(menu)
tray_icon.show()

print("\n✓ UI started successfully!")
print("Look for the blue circle icon in your system tray")
print("Right-click it to test the menu")
print("Press Ctrl+C here to quit\n")

sys.exit(app.exec())
