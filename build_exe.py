"""
Build script for creating standalone .exe using PyInstaller
"""

import PyInstaller.__main__
import os
import sys

# Get the absolute path to the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_dir, 'src')

# PyInstaller arguments
args = [
    os.path.join(src_dir, 'main.py'),  # Main script
    '--name=ScreenTranslator',  # Name of the executable
    '--windowed',  # No console window (GUI app)
    '--onefile',  # Single executable file
    '--icon=NONE',  # No icon (you can add one later)
    
    # Add data files
    f'--add-data={os.path.join(project_dir, "config.json")};.',
    
    # Add source modules
    f'--add-data={src_dir};src',
    
    # Hidden imports (modules that PyInstaller might miss)
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--hidden-import=pytesseract',
    '--hidden-import=deep_translator',
    '--hidden-import=google.generativeai',
    '--hidden-import=mss',
    '--hidden-import=multiprocessing',
    '--hidden-import=queue',
    
    # Exclude unnecessary modules to reduce size
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    '--exclude-module=pandas',
    
    # Build directory
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
    
    # Clean build
    '--clean',
    
    # No confirmation prompts
    '--noconfirm',
]

print("=" * 60)
print("Building ScreenTranslator.exe")
print("=" * 60)
print(f"Project directory: {project_dir}")
print(f"Source directory: {src_dir}")
print()

# Run PyInstaller
PyInstaller.__main__.run(args)

print()
print("=" * 60)
print("Build complete!")
print("=" * 60)
print(f"Executable location: {os.path.join(project_dir, 'dist', 'ScreenTranslator.exe')}")
print()
print("IMPORTANT NOTES:")
print("1. Make sure Tesseract OCR is installed on the target machine")
print("2. The config.json file will be bundled with the .exe")
print("3. First run might be slower as it initializes AI models")
print("=" * 60)
