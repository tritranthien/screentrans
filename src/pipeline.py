"""
Processing pipeline that runs OCR and translation in a separate process
to avoid blocking the UI thread
"""

import multiprocessing as mp
from multiprocessing import Process, Queue
import numpy as np
from typing import Dict, Any, Optional
import time

from capture import ScreenCapture
# OCREngine and Translator will be imported lazily in initialize_engines()
# to avoid loading heavy dependencies (PyTorch, etc.) at import time


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
            # Lazy import to avoid loading heavy dependencies at module import time
            from ocr_engine import OCREngine
            from translator import Translator
            
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
            
            # Log OCR results for debugging (both console and file)
            log_lines = []
            log_lines.append(f"\n{'='*60}")
            log_lines.append(f"OCR DETECTED {len(ocr_results)} TEXT SEGMENTS:")
            log_lines.append(f"{'='*60}")
            
            for i, (bbox, text, confidence) in enumerate(ocr_results):
                line = f"{i+1}. '{text}' (confidence: {confidence:.2f})"
                log_lines.append(line)
            
            if ocr_results:
                # Show combined text
                combined_text = " ".join([text for _, text, _ in ocr_results])
                log_lines.append(f"\nCOMBINED TEXT:")
                log_lines.append(f">>> {combined_text}")
                log_lines.append(f"{'='*60}\n")
            
            # Print to console
            for line in log_lines:
                print(line)
            
            # Save to file
            try:
                with open("ocr_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n".join(log_lines) + "\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            except:
                pass
            
            if not ocr_results:
                print("No text detected in region")
                # Save debug image
                import cv2
                debug_file = f"debug_no_text_{int(time.time())}.png"
                cv2.imwrite(debug_file, image)
                print(f"DEBUG: Saved captured image to {debug_file}")
                
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
                # Extract all texts and combine them
                texts_to_translate = [text for _, text, _ in ocr_results]
                combined_text = " ".join(texts_to_translate)
                
                # Translate ONLY the combined text (full sentence)
                # This gives much better translation quality than word-by-word
                translated_full = self.translator.translate(combined_text)
                
                print(f"\nTRANSLATION:")
                print(f"Original: {combined_text}")
                print(f"Translated: {translated_full}\n")
            else:
                # No translation available
                translated_full = " ".join([text for _, text, _ in ocr_results])
            
            translate_time = time.time() - translate_start
            
            # Combine OCR results with translations
            # For individual words, we keep original text (not translated)
            # because word-by-word translation is inaccurate
            for i, (bbox, original_text, confidence) in enumerate(ocr_results):
                translations.append({
                    'bbox': bbox,
                    'original': original_text,
                    'translated': original_text,  # Keep original for word-by-word view
                    'confidence': confidence
                })
            
            # Add the full translation as metadata
            # The overlay will use this for the "Full Text" tab
            result_data = {
                'type': 'result',
                'region': region,
                'texts': translations,
                'full_translation': translated_full,  # Full sentence translation
                'timing': {
                    'capture': capture_time,
                    'ocr': ocr_time,
                    'translation': translate_time,
                    'total': time.time() - start_time
                }
            }
            
            total_time = time.time() - start_time
            
            # Send results back to UI
            self.result_queue.put(result_data)
            
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
                    print(f"DEBUG: Pipeline received command: {command['type']}")
                    
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
