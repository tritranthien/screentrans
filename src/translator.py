"""
Translation module supporting both Google Translate and Gemini AI
"""

from typing import List, Optional
import json
import os

class Translator:
    """
    Wrapper for translation engines (Google Translate or Gemini AI).
    """
    
    def __init__(self, model_path: Optional[str] = None, source_lang: str = "en", target_lang: str = "vi"):
        """
        Initialize the translator.
        
        Args:
            model_path: Ignored (kept for compatibility)
            source_lang: Source language code (default: "en")
            target_lang: Target language code (default: "vi")
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Load config
        self.config = self._load_config()
        
        # Initialize translation engine based on config
        self.engine_type = self.config.get('translation_engine', 'google')
        self.custom_prompt = self.config.get('custom_prompt', 'Dịch văn bản sau sang tiếng Việt:')
        
        if self.engine_type == 'gemini':
            self._init_gemini()
        else:
            self._init_google_translate()
    
    def _load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return {
            'translation_engine': 'google',
            'gemini_api_key': '',
            'custom_prompt': 'Dịch văn bản sau sang tiếng Việt:'
        }
    
    def _init_gemini(self):
        """Initialize Gemini AI"""
        try:
            import google.generativeai as genai
            
            # Always initialize Google Translate as backup
            self._init_google_translate(as_backup=True)
            
            api_key = self.config.get('gemini_api_key', '')
            if not api_key:
                print("⚠ Gemini API key not found. Using Google Translate.")
                self.engine_type = 'google'
                return
            
            genai.configure(api_key=api_key)
            
            # Try to use the best available model
            # Priority: 2.0 Flash -> 2.5 Flash -> 1.5 Flash -> Pro
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-2.5-flash',
                'gemini-1.5-flash',
                'gemini-pro'
            ]
            
            self.gemini_model = None
            for model_name in models_to_try:
                try:
                    # Test if model is available by listing it or just creating it
                    # Note: GenerativeModel constructor doesn't validate immediately,
                    # but we'll use the first one in our list.
                    self.gemini_model = genai.GenerativeModel(model_name)
                    print(f"Selected Gemini model: {model_name}")
                    break
                except:
                    continue
            
            if not self.gemini_model:
                # Fallback default
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("Defaulted to Gemini model: gemini-pro")
            
            print(f"Gemini AI Translator initialized: {self.source_lang} -> {self.target_lang}")
            print(f"Custom prompt: {self.custom_prompt}")
            
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            print("Falling back to Google Translate")
            self.engine_type = 'google'
    
    def _init_google_translate(self, as_backup=False):
        """Initialize Google Translate"""
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
            
            if not as_backup:
                self.gemini_model = None
                self.engine_type = 'google'
                print(f"Google Translate initialized: {self.source_lang} -> {self.target_lang}")
            else:
                print("Google Translate initialized as backup")
                
        except Exception as e:
            print(f"Error initializing Google Translate: {e}")
            self.translator = None
            if not as_backup:
                self.gemini_model = None

    def translate(self, text: str, beam_size: int = 2) -> str:
        """
        Translate text.
        
        Args:
            text: Text to translate
            beam_size: Ignored
            
        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return text
        
        if self.engine_type == 'gemini' and self.gemini_model:
            return self._translate_with_gemini(text)
        elif self.translator:
            return self._translate_with_google(text)
        else:
            return text

    def _translate_with_gemini(self, text: str) -> str:
        """Translate using Gemini AI"""
        try:
            # Build prompt with custom context
            prompt = f"{self.custom_prompt}\n\n{text}"
            
            # Generate content
            response = self.gemini_model.generate_content(prompt)
            
            # Check if response has text (might be blocked by safety filters)
            if hasattr(response, 'text'):
                return response.text.strip()
            elif hasattr(response, 'parts'):
                return response.parts[0].text.strip()
            else:
                print("Gemini response blocked or empty")
                return self._translate_with_google(text)
            
        except Exception as e:
            print(f"Gemini translation error: {e}")
            # Fallback to Google Translate
            return self._translate_with_google(text)
    
    def _translate_with_google(self, text: str) -> str:
        """Translate using Google Translate"""
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"Google Translate error: {e}")
            return text
    
    def translate_batch(self, texts: List[str], beam_size: int = 2) -> List[str]:
        """
        Translate multiple texts.
        Note: For Gemini, we translate individually to avoid token limits.
        
        Args:
            texts: List of texts to translate
            beam_size: Ignored
            
        Returns:
            List[str]: List of translated texts
        """
        if not texts:
            return []
        
        # For batch, just translate each individually
        # (Gemini has token limits, Google Translate is fast enough)
        results = []
        for text in texts:
            results.append(self.translate(text))
        
        return results
    
    def is_available(self) -> bool:
        """Check if translator is ready"""
        return (self.gemini_model is not None) or (self.translator is not None)
