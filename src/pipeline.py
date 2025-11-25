"""
Processing pipeline that runs OCR and translation in a separate process
to avoid blocking the UI thread
"""

import multiprocessing as mp
from multiprocessing import Process, Queue
import numpy as np
from typing import Dict, Any, Optional
import time

from .capture import ScreenCapture
from .ocr_engine import OCREngine
from .translator import Translator


class ProcessingPipeline(Process):
    """
    Separate process for heavy AI tasks (OCR + Translation).
    Communicates with UI via queues to keep the interface responsive.
    """
    
    def __init__(self, command_queue: Queue, result_queue: Queue, 
                 source_lang: str = "en", target_lang: str = "vi"):
        """
        Initialize the processing pipeline.
        
        Args:
            command_queue: Queue to receive commands from UI
            result_queue: Queue to send results back to UI
            source_lang: Source language for translation
            target_lang: Target language for translation
        """
        super().__init__()
        self.command_queue = command_queue
        self.result_queue = result_queue
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.running = True
        
        # These will be initialized in the run() method
        self.screen_capture = None
        self.ocr_engine = None
        self.translator = None
    
    def initialize_engines(self):
        """
        Initialize OCR and translation engines.
        This is done in the separate process to avoid blocking the UI.
        """
        try:
            print("Initializing processing engines...")
            
            # Initialize screen capture
            self.screen_capture = ScreenCapture()
            print("✓ Screen capture initialized")
            
            # Initialize OCR engine
            self.ocr_engine = OCREngine()
            print("✓ OCR engine initialized")
            
            # Initialize translator
            self.translator = Translator(source_lang=self.source_lang, target_lang=self.target_lang)
            
            if self.translator.is_available():
                print("✓ Translator initialized")
            else:
                print("⚠ Translator not available (model not found)")
            
            # Send initialization complete signal
            self.result_queue.put({
                'type': 'init_complete',
                'translator_available': self.translator.is_available()
            })
            
        except Exception as e:
            print(f"Error initializing engines: {e}")
            self.result_queue.put({
                'type': 'init_error',
                'error': str(e)
            })
            self.running = False
    
    def process_region(self, region: Dict[str, int]):
        """
        Capture, OCR, and translate a screen region.
        
        Args:
            region: Dictionary with 'x', 'y', 'width', 'height' keys
        """
        try:
            start_time = time.time()
            
            # Capture screen region
            image = self.screen_capture.capture_region(
                region['x'], region['y'], region['width'], region['height']
            )
            
            if image is None:
                self.result_queue.put({
                    'type': 'error',
                    'error': 'Failed to capture screen region'
                })
                return
            
            capture_time = time.time() - start_time
            
            # Perform OCR
            ocr_start = time.time()
            ocr_results = self.ocr_engine.detect_and_recognize(image)
            ocr_time = time.time() - ocr_start
            
            if not ocr_results:
                self.result_queue.put({
                    'type': 'result',
                    'region': region,
                    'texts': [],
                    'timing': {
                        'capture': capture_time,
                        'ocr': ocr_time,
                        'translation': 0,
                        'total': time.time() - start_time
                    }
                })
                return
            
            # Translate detected texts
            translate_start = time.time()
            translations = []
            
            if self.translator.is_available():
                # Extract texts for batch translation
                texts_to_translate = [text for _, text, _ in ocr_results]
                translated_texts = self.translator.translate_batch(texts_to_translate)
            else:
                # No translation available, use original texts
                translated_texts = [text for _, text, _ in ocr_results]
            
            translate_time = time.time() - translate_start
            
            # Combine OCR results with translations
            for i, (bbox, original_text, confidence) in enumerate(ocr_results):
                translations.append({
                    'bbox': bbox,
                    'original': original_text,
                    'translated': translated_texts[i],
                    'confidence': confidence
                })
            
            total_time = time.time() - start_time
            
            # Send results back to UI
            self.result_queue.put({
                'type': 'result',
                'region': region,
                'texts': translations,
                'timing': {
                    'capture': capture_time,
                    'ocr': ocr_time,
                    'translation': translate_time,
                    'total': total_time
                }
            })
            
            print(f"Processing complete: {total_time:.3f}s (capture: {capture_time:.3f}s, "
                  f"OCR: {ocr_time:.3f}s, translation: {translate_time:.3f}s)")
            
        except Exception as e:
            print(f"Error processing region: {e}")
            self.result_queue.put({
                'type': 'error',
                'error': str(e)
            })
    
    def run(self):
        """
        Main loop for the processing pipeline.
        Runs in a separate process.
        """
        print("Processing pipeline started")
        
        # Initialize engines in this process
        self.initialize_engines()
        
        # Main processing loop
        while self.running:
            try:
                # Wait for commands from UI (with timeout to allow clean shutdown)
                if not self.command_queue.empty():
                    command = self.command_queue.get(timeout=0.1)
                    
                    if command['type'] == 'process_region':
                        self.process_region(command['region'])
                    
                    elif command['type'] == 'shutdown':
                        print("Shutdown command received")
                        self.running = False
                        break
                
                else:
                    # Small sleep to prevent busy waiting
                    time.sleep(0.01)
                    
            except Exception as e:
                print(f"Error in processing loop: {e}")
                time.sleep(0.1)
        
        # Cleanup
        if self.screen_capture:
            self.screen_capture.close()
        
        print("Processing pipeline stopped")
