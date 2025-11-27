"""
Script to list available Gemini models
"""
import google.generativeai as genai
import json
import os

def load_api_key():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('gemini_api_key')
    except:
        return None

def list_models():
    api_key = load_api_key()
    if not api_key:
        print("Error: API key not found in config.json")
        return

    try:
        genai.configure(api_key=api_key)
        print("Listing available models...")
        print("-" * 50)
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}")
                print(f"Display Name: {m.display_name}")
                print("-" * 50)
                
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
