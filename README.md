# Screen Translator

A low-latency, high-accuracy screen translation application for Windows using Python.

## Features

- **Real-time Screen Capture**: Fast screen region capture using `mss`
- **Offline OCR**: High-accuracy text recognition using RapidOCR
- **Offline Translation**: Low-latency neural translation using CTranslate2
- **Transparent Overlay**: Display translations directly over original text using PyQt6
- **Multi-process Architecture**: Separate process for AI tasks to keep UI responsive

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `mss` - Fast screen capture
- `rapidocr-onnxruntime` - Offline OCR engine
- `ctranslate2` - Fast translation inference
- `sentencepiece` - Tokenization for translation
- `PyQt6` - GUI framework
- `numpy`, `opencv-python` - Image processing

### 2. Download Translation Models

**IMPORTANT**: The application requires translation models to function. RapidOCR models are downloaded automatically, but translation models need manual setup.

#### Option A: Use Pre-converted CTranslate2 Models

1. Download a pre-converted model from [CTranslate2 Model Hub](https://github.com/OpenNMT/CTranslate2#model-conversion) or other sources
2. Place the model in `models/en-vi/` directory (create if doesn't exist)
3. The directory should contain:
   - `model.bin`
   - `config.json`
   - `sentencepiece.model` (if using SentencePiece tokenization)

#### Option B: Convert Your Own Model

If you have a Hugging Face model or other format:

```bash
# Install conversion tool
pip install ctranslate2

# Convert a Hugging Face model (example: Helsinki-NLP/opus-mt-en-vi)
ct2-transformers-converter --model Helsinki-NLP/opus-mt-en-vi --output_dir models/en-vi
```

Popular translation models:
- **English → Vietnamese**: `Helsinki-NLP/opus-mt-en-vi`
- **English → Spanish**: `Helsinki-NLP/opus-mt-en-es`
- **English → French**: `Helsinki-NLP/opus-mt-en-fr`
- **English → German**: `Helsinki-NLP/opus-mt-en-de`

### 3. Verify Installation

Run a quick test:

```bash
python -c "from rapidocr_onnxruntime import RapidOCR; print('OCR OK')"
python -c "import ctranslate2; print('CTranslate2 OK')"
```

## Usage

### Start the Application

```bash
python src/main.py
```

Or specify custom languages:

```bash
python src/main.py --source en --target es  # English to Spanish
```

### Capture and Translate

1. **Double-click** the system tray icon, or
2. **Right-click** the tray icon and select "Capture Region", or
3. Press **Ctrl+Shift+S** (if global hotkeys are configured)

4. **Click and drag** to select the screen region containing text
5. Release to capture and process
6. Translations will appear as an overlay on top of the original text

### Controls

- **ESC**: Clear current translations
- **Right-click tray icon**: Access menu
  - Capture Region
  - Clear Translations
  - Quit

## Project Structure

```
screentrans/
├── src/
│   ├── __init__.py
│   ├── capture.py       # Screen capture using mss
│   ├── ocr_engine.py    # OCR wrapper for RapidOCR
│   ├── translator.py    # Translation wrapper for CTranslate2
│   ├── pipeline.py      # Multi-process pipeline for AI tasks
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── overlay.py   # Transparent overlay window
│   │   └── snipping.py  # Region selection tool
│   └── main.py          # Application entry point
├── models/              # Translation models directory
│   └── en-vi/          # English to Vietnamese model
├── requirements.txt
└── README.md
```

## Architecture

### Multi-Process Design

The application uses Python's `multiprocessing` to bypass the GIL and keep the UI responsive:

1. **Main Process (UI)**:
   - PyQt6 application
   - System tray icon
   - Snipping tool for region selection
   - Transparent overlay for displaying results

2. **Processing Process (AI)**:
   - Screen capture
   - OCR (RapidOCR)
   - Translation (CTranslate2)
   - Sends results back via Queue

### Communication Flow

```
User selects region
    ↓
Main Process → command_queue → Processing Process
    ↓
Processing Process:
    - Capture screen
    - Run OCR
    - Translate text
    ↓
Processing Process → result_queue → Main Process
    ↓
Overlay displays translations
```

## Performance

Expected latency breakdown:
- **Screen Capture**: 10-50ms
- **OCR**: 100-500ms (depends on text amount)
- **Translation**: 50-200ms (depends on text length)
- **Total**: ~200-750ms for typical use cases

## Troubleshooting

### "Translator not available" message

- Make sure you have downloaded and placed translation models in `models/en-vi/` (or appropriate language pair)
- Verify the model directory contains `model.bin` and `config.json`

### OCR not detecting text

- Ensure the captured region has good contrast
- Try capturing a larger region
- Check that the text is not too small

### High CPU usage

- This is normal during processing (OCR + Translation are CPU-intensive)
- The separate process design prevents UI freezing
- Consider reducing the capture region size for faster processing

### Application won't start

- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (requires Python 3.8+)
- On Windows, ensure you have Visual C++ redistributables installed

## Development

### Running Tests

Test individual components:

```bash
# Test OCR
python -c "from src.ocr_engine import OCREngine; import cv2; ocr = OCREngine(); img = cv2.imread('test.png'); print(ocr.get_text_only(img))"

# Test Translation
python -c "from src.translator import Translator; t = Translator(); print(t.translate('Hello World'))"

# Test Screen Capture
python -c "from src.capture import ScreenCapture; sc = ScreenCapture(); img = sc.capture_region(0, 0, 500, 500); print(img.shape)"
```

## License

MIT License - feel free to use and modify as needed.

## Credits

- **RapidOCR**: Fast and accurate OCR engine
- **CTranslate2**: Efficient transformer inference
- **PyQt6**: Cross-platform GUI framework
- **mss**: Fast screen capture library
