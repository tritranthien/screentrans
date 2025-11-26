"""
Configuration tool for Screen Translator
Allows users to set Gemini API key and custom translation prompt
"""

import json
import os

def load_config():
    """Load current configuration"""
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'translation_engine': 'google',
        'gemini_api_key': '',
        'custom_prompt': 'Dịch văn bản sau sang tiếng Việt một cách tự nhiên và dễ hiểu:',
        'source_lang': 'en',
        'target_lang': 'vi'
    }

def save_config(config):
    """Save configuration"""
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("\n✓ Configuration saved!")

def main():
    print("="*60)
    print("Screen Translator - Configuration")
    print("="*60)
    
    config = load_config()
    
    print("\nCurrent settings:")
    print(f"1. Translation Engine: {config.get('translation_engine', 'google')}")
    print(f"2. Gemini API Key: {'*' * 20 if config.get('gemini_api_key') else '(not set)'}")
    print(f"3. Custom Prompt: {config.get('custom_prompt', '')}")
    print(f"4. Source Language: {config.get('source_lang', 'en')}")
    print(f"5. Target Language: {config.get('target_lang', 'vi')}")
    
    print("\n" + "="*60)
    print("What would you like to configure?")
    print("="*60)
    print("1. Set Gemini API Key")
    print("2. Set Custom Translation Prompt")
    print("3. Choose Translation Engine (google/gemini)")
    print("4. Set Source/Target Languages")
    print("0. Exit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice == '1':
        print("\nTo get a Gemini API key:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Copy and paste it below\n")
        
        api_key = input("Enter Gemini API Key: ").strip()
        if api_key:
            config['gemini_api_key'] = api_key
            config['translation_engine'] = 'gemini'
            save_config(config)
        else:
            print("No API key entered.")
    
    elif choice == '2':
        print("\nCurrent prompt:")
        print(f">>> {config.get('custom_prompt', '')}")
        print("\nExamples:")
        print("- Dịch văn bản sau sang tiếng Việt một cách tự nhiên:")
        print("- Dịch văn bản sau với văn phong kiếm hiệp:")
        print("- Dịch văn bản kỹ thuật sau sang tiếng Việt chuyên nghiệp:")
        print()
        
        new_prompt = input("Enter new prompt (or press Enter to keep current): ").strip()
        if new_prompt:
            config['custom_prompt'] = new_prompt
            save_config(config)
        else:
            print("Prompt unchanged.")
    
    elif choice == '3':
        print("\nAvailable engines:")
        print("1. google - Google Translate (free, no API key needed)")
        print("2. gemini - Gemini AI (requires API key, better quality)")
        
        engine = input("\nChoose engine (google/gemini): ").strip().lower()
        if engine in ['google', 'gemini']:
            config['translation_engine'] = engine
            save_config(config)
        else:
            print("Invalid engine.")
    
    elif choice == '4':
        print("\nCurrent languages:")
        print(f"Source: {config.get('source_lang', 'en')}")
        print(f"Target: {config.get('target_lang', 'vi')}")
        
        source = input("\nEnter source language code (e.g., en, vi, ja): ").strip()
        target = input("Enter target language code (e.g., en, vi, ja): ").strip()
        
        if source:
            config['source_lang'] = source
        if target:
            config['target_lang'] = target
        
        if source or target:
            save_config(config)
        else:
            print("Languages unchanged.")
    
    elif choice == '0':
        print("Goodbye!")
    else:
        print("Invalid choice.")

if __name__ == '__main__':
    main()
