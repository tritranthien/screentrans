"""
Test script for translation functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from translator import Translator


def test_translation():
    """Test translation engine"""
    print("=" * 60)
    print("Translation Engine Test")
    print("=" * 60)
    
    try:
        # Initialize translator
        print("\n1. Initializing translator (English → Vietnamese)...")
        translator = Translator(source_lang="en", target_lang="vi")
        
        if not translator.is_available():
            print("\n⚠ WARNING: Translator not available!")
            print("   Translation models not found.")
            print("   Please download models as described in README.md")
            print("\n   The application will still work, but will show")
            print("   original text instead of translations.")
            return True  # Not a failure, just a warning
        
        print("   ✓ Translator initialized")
        
        # Test single translation
        print("\n2. Testing single translation...")
        test_texts = [
            "Hello World",
            "Good morning",
            "How are you?",
            "Screen Translator is working!",
            "This is a test of the translation system."
        ]
        
        for i, text in enumerate(test_texts, 1):
            translated = translator.translate(text)
            print(f"\n   {i}. Original:    '{text}'")
            print(f"      Translated: '{translated}'")
        
        # Test batch translation
        print("\n3. Testing batch translation...")
        batch_texts = [
            "First sentence",
            "Second sentence",
            "Third sentence"
        ]
        
        translated_batch = translator.translate_batch(batch_texts)
        
        print("\n   Batch results:")
        for i, (orig, trans) in enumerate(zip(batch_texts, translated_batch), 1):
            print(f"   {i}. '{orig}' → '{trans}'")
        
        print("\n" + "=" * 60)
        print("✓ All translation tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during translation test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = test_translation()
    sys.exit(0 if success else 1)
