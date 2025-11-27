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
    '--onedir',  # Create a directory instead of single file (better for large dependencies)
    '--icon=NONE',  # No icon (you can add one later)
    
    # Add paths to search for imports
    f'--paths={src_dir}',
    
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
print("Building ScreenTranslator (Directory Mode)")
print("=" * 60)
print(f"Project directory: {project_dir}")
print(f"Source directory: {src_dir}")
print()

# Run PyInstaller
PyInstaller.__main__.run(args)

# Post-build: Copy Tesseract-OCR to dist folder
import shutil
dist_dir = os.path.join(project_dir, 'dist', 'ScreenTranslator')
tess_dst = os.path.join(dist_dir, 'Tesseract-OCR')

# Try local project copy first
tess_src = os.path.join(project_dir, 'Tesseract-OCR')

# If not found, try Program Files
if not os.path.exists(tess_src):
    tess_src = r'C:\Program Files\Tesseract-OCR'

if os.path.exists(tess_src):
    print(f"Copying Tesseract-OCR from {tess_src} to {tess_dst}...")
    if os.path.exists(tess_dst):
        shutil.rmtree(tess_dst)
    
    # Use ignore_errors=True to skip permission errors on some files
    try:
        shutil.copytree(tess_src, tess_dst, ignore=shutil.ignore_patterns('*.tmp', 'unins*'))
        print("✓ Tesseract-OCR bundled successfully")
    except Exception as e:
        print(f"⚠ Warning during Tesseract copy: {e}")
        print("  Some files might be missing, but main functionality should work.")
else:
    print("⚠ Tesseract-OCR directory not found!")
    print("  Please copy 'C:\\Program Files\\Tesseract-OCR' to the dist folder manually.")

print()
print("=" * 60)
print("Build complete!")
print("=" * 60)
print(f"Output directory: {dist_dir}")
print()
print("DISTRIBUTION INSTRUCTIONS:")
print("1. Zip the entire 'ScreenTranslator' folder inside 'dist'")
print("2. Send the Zip file to users")
print("3. Users just need to unzip and run ScreenTranslator.exe")
print("=" * 60)
