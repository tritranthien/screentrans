"""
Translation module using CTranslate2 for fast, offline neural machine translation
"""

import ctranslate2
import sentencepiece as spm
from typing import List, Optional
import os
from pathlib import Path


class Translator:
    """
    Wrapper for CTranslate2 translation engine.
    Supports offline translation using pre-trained models.
    """
    
    def __init__(self, model_path: Optional[str] = None, source_lang: str = "en", target_lang: str = "vi"):
        """
        Initialize the translator.
        
        Args:
            model_path: Path to CTranslate2 model directory. If None, uses default path.
            source_lang: Source language code (default: "en" for English)
            target_lang: Target language code (default: "vi" for Vietnamese)
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Set default model path if not provided
        if model_path is None:
            # Use models directory in project root
            project_root = Path(__file__).parent.parent
            model_path = project_root / "models" / f"{source_lang}-{target_lang}"
        
        self.model_path = Path(model_path)
        
        # Check if model exists
        if not self.model_path.exists():
            print(f"Warning: Model not found at {self.model_path}")
            print("You need to download and convert a translation model.")
            print("See README.md for instructions.")
            self.translator = None
            self.sp_model = None
            return
        
        try:
            # Load CTranslate2 model
            self.translator = ctranslate2.Translator(str(self.model_path))
            
            # Load SentencePiece tokenizer if available
            sp_model_path = self.model_path / "sentencepiece.model"
            if sp_model_path.exists():
                self.sp_model = spm.SentencePieceProcessor(str(sp_model_path))
            else:
                self.sp_model = None
                print("Warning: SentencePiece model not found. Using simple tokenization.")
            
            print(f"Translator initialized: {source_lang} -> {target_lang}")
            
        except Exception as e:
            print(f"Error initializing translator: {e}")
            self.translator = None
            self.sp_model = None
    
    def translate(self, text: str, beam_size: int = 2) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            beam_size: Beam search size (higher = better quality but slower)
            
        Returns:
            str: Translated text, or original text if translation fails
        """
        if not text or not text.strip():
            return text
        
        if self.translator is None:
            print("Translator not initialized. Returning original text.")
            return text
        
        try:
            # Tokenize input
            if self.sp_model:
                tokens = self.sp_model.encode(text, out_type=str)
            else:
                # Simple whitespace tokenization as fallback
                tokens = text.split()
            
            # Translate
            results = self.translator.translate_batch(
                [tokens],
                beam_size=beam_size,
                max_input_length=512,
                max_decoding_length=256,  # Reduced to prevent repetition
                repetition_penalty=1.2  # Penalize repetition
            )
            
            # Get the best translation
            translated_tokens = results[0].hypotheses[0]
            
            # Detokenize
            if self.sp_model:
                translated_text = self.sp_model.decode(translated_tokens)
            else:
                translated_text = " ".join(translated_tokens)
            
            return translated_text
            
        except Exception as e:
            print(f"Error during translation: {e}")
            return text
    
    def translate_batch(self, texts: List[str], beam_size: int = 2) -> List[str]:
        """
        Translate multiple texts in batch for better performance.
        
        Args:
            texts: List of texts to translate
            beam_size: Beam search size
            
        Returns:
            List[str]: List of translated texts
        """
        if not texts:
            return []
        
        if self.translator is None:
            print("Translator not initialized. Returning original texts.")
            return texts
        
        try:
            # Tokenize all inputs
            if self.sp_model:
                tokenized_inputs = [self.sp_model.encode(text, out_type=str) for text in texts]
            else:
                tokenized_inputs = [text.split() for text in texts]
            
            # Translate batch
            results = self.translator.translate_batch(
                tokenized_inputs,
                beam_size=beam_size,
                max_input_length=512,
                max_decoding_length=256,  # Reduced to prevent repetition
                repetition_penalty=1.2  # Penalize repetition
            )
            
            # Detokenize results
            translated_texts = []
            for result in results:
                translated_tokens = result.hypotheses[0]
                
                if self.sp_model:
                    translated_text = self.sp_model.decode(translated_tokens)
                else:
                    translated_text = " ".join(translated_tokens)
                
                translated_texts.append(translated_text)
            
            return translated_texts
            
        except Exception as e:
            print(f"Error during batch translation: {e}")
            return texts
    
    def is_available(self) -> bool:
        """
        Check if translator is properly initialized and ready to use.
        
        Returns:
            bool: True if translator is ready, False otherwise
        """
        return self.translator is not None
