# Build Instructions for ScreenTranslator

## Prerequisites

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Make sure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Tesseract OCR must be installed** on the system where you build and run the .exe:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`

## Building the .exe

### Method 1: Using the build script (Recommended)

```bash
python build_exe.py
```

This will create a single executable file in the `dist` folder.

### Method 2: Manual PyInstaller command

```bash
pyinstaller --name=ScreenTranslator --windowed --onefile ^
  --add-data="config.json;." ^
  --add-data="src;src" ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=PIL ^
  --hidden-import=cv2 ^
  --hidden-import=numpy ^
  --hidden-import=pytesseract ^
  --hidden-import=deep_translator ^
  --hidden-import=google.generativeai ^
  --hidden-import=mss ^
  src/main.py
```

## Output

After building, you will find:
- **`dist/ScreenTranslator.exe`** - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `ScreenTranslator.spec` - PyInstaller spec file (can be customized)

## Distribution

To distribute the application:

1. **Copy the .exe file** from `dist/ScreenTranslator.exe`

2. **Requirements for end users**:
   - Windows 10/11 (64-bit)
   - Tesseract OCR installed at `C:\Program Files\Tesseract-OCR`
   - No Python installation needed!

3. **Optional**: Create an installer using tools like:
   - Inno Setup
   - NSIS
   - WiX Toolset

## Troubleshooting

### "Failed to execute script" error
- Make sure all dependencies are installed
- Check that Tesseract OCR is installed
- Run the .exe from command prompt to see error messages

### Large file size
The .exe will be large (~200-500 MB) because it includes:
- Python runtime
- PyQt6
- OpenCV
- Tesseract bindings
- AI libraries

To reduce size, consider using `--onedir` instead of `--onefile` (creates a folder with multiple files instead of a single .exe).

### Missing modules
If the app crashes due to missing modules, add them to the build script:
```python
'--hidden-import=module_name',
```

## Advanced: Creating an Installer

After building the .exe, you can create a professional installer:

### Using Inno Setup (Free)

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create a script file (example provided in `installer.iss`)
3. Compile to create `ScreenTranslator_Setup.exe`

This will:
- Install the application to Program Files
- Create desktop shortcut
- Add to Start Menu
- Include uninstaller

## Notes

- The first run of the .exe might be slower as it extracts temporary files
- Config file (`config.json`) is bundled with the .exe
- User settings are saved in the same directory as the .exe
- Tesseract OCR must be installed separately (not bundled)
