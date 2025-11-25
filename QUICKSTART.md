# Quick Start Guide

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages (~500MB download).

### 2. Setup Translation Models

**Option A: Automatic Setup (Recommended)**

```bash
python setup_models.py
```

This will download and convert the English→Vietnamese model (~200MB).

For other languages:
```bash
python setup_models.py --source en --target es  # English to Spanish
python setup_models.py --source en --target fr  # English to French
```

**Option B: Manual Setup**

If automatic setup fails, you can manually download models:

1. Install conversion tool:
   ```bash
   pip install transformers
   ```

2. Convert a model:
   ```bash
   ct2-transformers-converter --model Helsinki-NLP/opus-mt-en-vi --output_dir models/en-vi
   ```

### 3. Run Tests (Optional)

Test individual components:

```bash
# Test screen capture
python tests/test_capture.py

# Test OCR
python tests/test_ocr.py

# Test translation (requires models)
python tests/test_translation.py
```

### 4. Run the Application

```bash
python src/main.py
```

Or with custom languages:
```bash
python src/main.py --source en --target es
```

## Usage

1. **Start the app** - A system tray icon will appear
2. **Double-click the tray icon** or right-click → "Capture Region"
3. **Click and drag** to select the area with text
4. **Release** to capture and translate
5. **View translations** overlaid on the screen

### Keyboard Shortcuts

- **ESC**: Clear translations
- **Ctrl+Shift+S**: Capture region (when implemented)

## Troubleshooting

### "Translator not available"
- Run `python setup_models.py` to download models
- Check that `models/en-vi/` directory exists and contains `model.bin`

### OCR not working
- Ensure text has good contrast
- Try a larger capture region
- Check that RapidOCR installed correctly: `python -c "from rapidocr_onnxruntime import RapidOCR; print('OK')"`

### Application won't start
- Verify Python 3.8+ is installed
- Check all dependencies: `pip install -r requirements.txt`
- On Windows, install Visual C++ Redistributables if needed

## Performance Tips

- **Smaller regions = faster processing**
- **Good contrast = better OCR accuracy**
- **First run is slower** (model loading)
- **Subsequent captures are faster** (models cached in memory)

## Next Steps

- Try different language pairs
- Adjust overlay display time in `src/ui/overlay.py`
- Customize hotkeys in `src/main.py`
- Add more translation models for different languages
