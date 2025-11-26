"""
Helper script to download and setup translation models
"""

import os
import sys
from pathlib import Path
import subprocess


def setup_models(source_lang="en", target_lang="vi"):
    """
    Download and convert translation models using CTranslate2.
    
    Args:
        source_lang: Source language code
        target_lang: Target language code
    """
    print("=" * 60)
    print("Translation Model Setup")
    print("=" * 60)
    
    # Create models directory
    models_dir = Path(__file__).parent / "models" / f"{source_lang}-{target_lang}"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nModels will be saved to: {models_dir}")
    
    # Check if model already exists
    if (models_dir / "model.bin").exists():
        print("\n⚠ Model already exists!")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return
    
    # Determine model name based on language pair
    model_map = {
        ("en", "vi"): "Helsinki-NLP/opus-mt-en-vi",
        ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
        ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
        ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
        ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
        ("en", "ja"): "Helsinki-NLP/opus-mt-en-jap",
        ("en", "ko"): "Helsinki-NLP/opus-mt-en-ko",
    }
    
    model_name = model_map.get((source_lang, target_lang))
    
    if model_name is None:
        print(f"\n✗ No pre-configured model for {source_lang} → {target_lang}")
        print("\nAvailable language pairs:")
        for (src, tgt), name in model_map.items():
            print(f"  - {src} → {tgt}: {name}")
        print("\nYou can manually specify a Hugging Face model:")
        model_name = input("Enter Hugging Face model name (or press Enter to cancel): ").strip()
        if not model_name:
            print("Cancelled.")
            return
    
    print(f"\nUsing model: {model_name}")
    
    # Install ctranslate2 if not already installed
    print("\n1. Checking CTranslate2 installation...")
    try:
        import ctranslate2
        print("   ✓ CTranslate2 is installed")
    except ImportError:
        print("   Installing CTranslate2...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ctranslate2"])
        print("   ✓ CTranslate2 installed")
    
    # Convert model
    print(f"\n2. Downloading and converting model...")
    print(f"   This may take several minutes...")
    
    try:
        cmd = [
            "ct2-transformers-converter",
            "--model", model_name,
            "--output_dir", str(models_dir),
            "--quantization", "int8",  # Use int8 quantization for smaller size and faster inference
            "--force"
        ]
        
        print(f"\n   Running: {' '.join(cmd)}\n")
        subprocess.check_call(cmd)
        
        print("\n   ✓ Model downloaded and converted successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n   ✗ Error converting model: {e}")
        print("\n   You may need to install transformers:")
        print("   pip install transformers")
        return
    except FileNotFoundError:
        print("\n   ✗ ct2-transformers-converter not found!")
        print("\n   Please install it with:")
        print("   pip install ctranslate2")
        return
    
    # Verify model files
    print("\n3. Verifying model files...")
    required_files = ["model.bin", "config.json"]
    
    for file in required_files:
        file_path = models_dir / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✓ {file} ({size:.2f} MB)")
        else:
            print(f"   ✗ {file} not found!")
    
    # Check for optional files
    optional_files = ["sentencepiece.model", "source.spm", "target.spm"]
    for file in optional_files:
        file_path = models_dir / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✓ {file} ({size:.2f} MB)")
    
    print("\n" + "=" * 60)
    print("✓ Model setup complete!")
    print("=" * 60)
    print(f"\nYou can now run the application with:")
    print(f"  python src/main.py --source {source_lang} --target {target_lang}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup translation models')
    parser.add_argument('--source', default='en', help='Source language code (default: en)')
    parser.add_argument('--target', default='vi', help='Target language code (default: vi)')
    args = parser.parse_args()
    
    setup_models(args.source, args.target)
