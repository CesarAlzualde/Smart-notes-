#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, time, re, json
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from transformers.utils.logging import set_verbosity_error
    import torch
    set_verbosity_error()
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.error("Dependencies 'transformers' and 'torch' not found. Summarization will be disabled.")
    TRANSFORMERS_AVAILABLE = False

@dataclass
class ModelStatus:
    loaded: bool = False
    model_name: str = ""
    error_msg: str = ""
    last_error_time: float = 0.0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

class TextSummarizer:
    SPANISH_WORDS = {'el', 'la', 'de', 'y', 'en', 'que', 'un', 'una', 'a', 'o', 'con', 'por'}
    ENGLISH_WORDS = {'the', 'a', 'of', 'and', 'in', 'that', 'is', 'it', 'to', 'for', 'with', 'on'}
    MODELS = {'primary': "facebook/bart-large-cnn", 'fallback': "sshleifer/distilbart-cnn-12-6"}

    def __init__(self, model_name: str = "facebook/bart-large-cnn", max_input_length: int = 1024, max_output_length: int = 150, cache_dir: Optional[str] = None, default_compression_ratio: float = 0.3):
        if not TRANSFORMERS_AVAILABLE:
            self.model_status = ModelStatus(loaded=False, error_msg="Dependencies not installed")
            self.tokenizer, self.model = None, None
            logger.error("TextSummarizer cannot operate without 'transformers' and 'torch'.")
            return
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initial_model_name = model_name
        self.cache_dir = cache_dir
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.default_compression_ratio = max(0.1, min(default_compression_ratio, 0.9))
        self.tokenizer, self.model = None, None
        self.model_status = ModelStatus(model_name=model_name)
        logger.info(f"TextSummarizer initialized for device: {self.device}. Model will be loaded on demand.")

    def _load_model(self, model_to_load: str) -> bool:
        try:
            start_time = time.time()
            logger.info(f"Loading model and tokenizer: {model_to_load}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_to_load, cache_dir=self.cache_dir)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_to_load, cache_dir=self.cache_dir).to(self.device)
            logger.info(f"Model {model_to_load} loaded in {time.time() - start_time:.2f}s.")
            self.model_status.loaded = True
            self.model_status.model_name = model_to_load
            self.model_status.error_msg = ""
            return True
        except Exception as e:
            logger.error(f"Failed to load model '{model_to_load}': {e}", exc_info=True)
            self.model_status.loaded = False
            self.model_status.model_name = model_to_load
            self.model_status.error_msg = str(e)
            self.model_status.last_error_time = time.time()
            return False

    def _ensure_model_loaded(self) -> bool:
        if self.model_status.loaded and self.model and self.tokenizer: return True
        logger.info("Model not loaded. Attempting to load...")
        if self._load_model(self.initial_model_name): return True
        fallback_model = self.MODELS.get('fallback')
        if fallback_model and fallback_model != self.initial_model_name:
            logger.warning(f"Primary model '{self.initial_model_name}' failed. Trying fallback: '{fallback_model}'")
            if self._load_model(fallback_model): return True
        logger.critical("Could not load any summarization model. Functionality disabled.")
        return False

    def detect_language(self, text: str) -> str:
        words = set(re.findall(r'\b\w+\b', text.lower()))
        if not words: return 'en'
        return "es" if len(words.intersection(self.SPANISH_WORDS)) > len(words.intersection(self.ENGLISH_WORDS)) else "en"

    def _calculate_length(self, num_tokens: int, compression_ratio: Optional[float]) -> Tuple[int, int]:
        ratio = compression_ratio if compression_ratio is not None else self.default_compression_ratio
        ratio = max(0.1, min(1.0, ratio))
        target_len = int(num_tokens * ratio)
        max_len = min(target_len, self.max_output_length)
        min_len = max(30, int(max_len * 0.4))
        return min_len, max(min_len + 1, max_len)

    def post_process_summary(self, summary: str) -> str:
        if not summary: return ""
        summary = re.sub(r'\s+([.,;:!?])', r'\1', summary)
        summary = summary.strip()
        if summary:
            summary = summary[0].upper() + summary[1:]
            if not summary.endswith(('.', '!', '?')): summary += '.'
        return ' '.join(summary.split())

    def generate_summary(self, text: str, compression_ratio: Optional[float] = None) -> Dict[str, Any]:
        start_total_time = time.time()
        if not TRANSFORMERS_AVAILABLE or not self._ensure_model_loaded():
            return {"error": "Summarizer is not available."}
        
        try:
            lang = self.detect_language(text)
            
            inputs = self.tokenizer(text, return_tensors="pt", max_length=self.max_input_length, truncation=True, padding="max_length")
            input_token_count = len(inputs['input_ids'][0])
            
            min_len, max_len = self._calculate_length(input_token_count, compression_ratio)
            
            logger.info(f"Generating summary. Input tokens: {input_token_count}, Min/Max length: {min_len}/{max_len}, Ratio: {compression_ratio or self.default_compression_ratio:.2f}")
            
            start_gen_time = time.time()
            summary_ids = self.model.generate(
                inputs['input_ids'].to(self.device),
                num_beams=4,
                min_length=min_len,
                max_length=max_len,
                early_stopping=True
            )
            gen_time = time.time() - start_gen_time
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
            summary = self.post_process_summary(summary)
            
            output_token_count = len(summary_ids[0])
            actual_ratio = output_token_count / input_token_count if input_token_count > 0 else 0
            total_time = time.time() - start_total_time

            logger.info(f"Summary generated in {total_time:.2f}s (generation: {gen_time:.2f}s).")
            
            return {
                "summary_text": summary,
                "model_used": self.model_status.model_name,
                "language": lang,
                "statistics": {
                    "input_chars": len(text),
                    "output_chars": len(summary),
                    "input_tokens": input_token_count,
                    "output_tokens": output_token_count,
                    "compression_ratio_target": compression_ratio or self.default_compression_ratio,
                    "compression_ratio_actual": actual_ratio,
                    "total_time_seconds": total_time,
                    "generation_time_seconds": gen_time
                }
            }
        except Exception as e:
            logger.error(f"Error during summary generation: {e}", exc_info=True)
            return {"error": f"An unexpected error occurred: {e}"}

def get_text_summarizer(config: Optional[Dict[str, Any]] = None) -> 'TextSummarizer':
    if config:
        return TextSummarizer(**config)
    return TextSummarizer()
