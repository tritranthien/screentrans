# Development Guide

## Project Overview

Screen Translator is a Python-based application that provides real-time screen translation using offline OCR and neural machine translation.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)
- Windows OS (current version optimized for Windows)

### Setting Up Development Environment

1. **Clone/Navigate to the project**
   ```bash
   cd c:\Users\t480\Desktop\person\screentrans
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development tools (optional)**
   ```bash
   pip install pytest black flake8 mypy
   ```

## Project Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│                      (src/main.py)                       │
│  - System tray integration                              │
│  - Application lifecycle management                     │
│  - Process coordination                                 │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  UI Layer    │  │  Processing  │  │   Capture    │
│              │  │   Pipeline   │  │    Layer     │
│ - Snipping   │  │              │  │              │
│ - Overlay    │  │ - OCR        │  │ - mss        │
│              │  │ - Translation│  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Key Design Patterns

1. **Multi-Process Pattern**: Separate process for CPU-intensive tasks
2. **Queue-based Communication**: Non-blocking IPC between processes
3. **Observer Pattern**: Qt signals/slots for UI events
4. **Facade Pattern**: Simple interfaces for complex subsystems (OCR, Translation)

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for docstrings, single quotes for strings
- **Imports**: Group by standard library, third-party, local

### Docstring Format

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
    pass
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Tuple

def process_data(items: List[str], config: Optional[Dict] = None) -> Tuple[int, str]:
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_ocr.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_new_feature.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from your_module import YourClass

def test_your_feature():
    """Test description"""
    obj = YourClass()
    result = obj.method()
    assert result == expected_value
```

## Adding New Features

### Adding a New Language Pair

1. Update `setup_models.py` with the new language pair:
   ```python
   model_map = {
       # ... existing pairs ...
       ("en", "new_lang"): "Helsinki-NLP/opus-mt-en-new_lang",
   }
   ```

2. Download the model:
   ```bash
   python setup_models.py --source en --target new_lang
   ```

3. Test the translation:
   ```bash
   python src/main.py --source en --target new_lang
   ```

### Adding a New UI Feature

1. Create a new widget in `src/ui/`:
   ```python
   # src/ui/new_widget.py
   from PyQt6.QtWidgets import QWidget
   
   class NewWidget(QWidget):
       def __init__(self):
           super().__init__()
           # Implementation
   ```

2. Integrate with main application in `src/main.py`

3. Add tests in `tests/test_ui.py`

### Modifying the Processing Pipeline

1. Edit `src/pipeline.py`
2. Update the command/result queue message format if needed
3. Update `src/ui/overlay.py` to handle new result types
4. Test with `tests/test_integration.py`

## Debugging

### Debug Mode

Add debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Common Issues

**Issue**: Models not loading
- Check `models/` directory exists
- Verify model files are present
- Check file permissions

**Issue**: UI not responding
- Check if processing pipeline is running
- Monitor queue sizes
- Look for exceptions in pipeline process

**Issue**: OCR not detecting text
- Save captured image for inspection
- Check image format (should be BGR)
- Verify text contrast

### Profiling

Profile performance:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Building for Distribution

### Creating Executable (PyInstaller)

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create executable:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico src/main.py
   ```

3. Include models directory in distribution

### Creating Installer (Inno Setup)

1. Install Inno Setup
2. Create installer script
3. Include Python runtime and dependencies

## Contributing

### Workflow

1. Create a feature branch
2. Make changes
3. Run tests
4. Update documentation
5. Submit pull request

### Commit Messages

Format: `type: description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Example:
```
feat: add support for Japanese translation
fix: resolve OCR crash on empty images
docs: update installation instructions
```

## Performance Optimization

### Profiling Checklist

- [ ] Screen capture latency
- [ ] OCR processing time
- [ ] Translation latency
- [ ] UI responsiveness
- [ ] Memory usage
- [ ] Process startup time

### Optimization Strategies

1. **Reduce Model Size**: Use int8 quantization
2. **Batch Processing**: Process multiple texts together
3. **Caching**: Cache frequently translated phrases
4. **Async I/O**: Use async for network operations
5. **GPU Acceleration**: Use CUDA for OCR/translation if available

## Troubleshooting Development Issues

### Import Errors

```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%\src  # Windows
```

### Qt Issues

```bash
# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

### Model Conversion Errors

```bash
# Install all required packages
pip install transformers torch sentencepiece
```

## Resources

### Documentation

- [RapidOCR Documentation](https://github.com/RapidAI/RapidOCR)
- [CTranslate2 Documentation](https://opennmt.net/CTranslate2/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [mss Documentation](https://python-mss.readthedocs.io/)

### Useful Tools

- **Qt Designer**: Visual UI design
- **PyCharm**: Python IDE with Qt support
- **Visual Studio Code**: Lightweight editor with Python extensions

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please open an issue on the project repository.
