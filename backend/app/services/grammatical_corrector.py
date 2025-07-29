"""
Servicio para la corrección gramatical de textos en español utilizando modelos de IA.
"""

import logging
from typing import Optional, Dict, Any

# Configurar logging
logger = logging.getLogger(__name__)

# Intentar importar dependencias de transformers
HF_AVAILABLE = False
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    HF_AVAILABLE = True
    logger.info("Hugging Face Transformers disponible para corrección gramatical.")
except ImportError:
    logger.warning("Transformers no disponible. La corrección gramatical estará desactivada.")

class GrammaticalCorrector:
    """
    Gestiona la carga de un modelo de corrección gramatical y la corrección de texto.
    """
    MODEL_NAME = "Abelardo/t5-base-spell-grammar-correction-spanish"

    def __init__(self, cache_dir: Optional[str] = None):
        self.device = "cuda" if HF_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.cache_dir = cache_dir
        self.is_loaded = False
        logger.info(f"GrammaticalCorrector inicializado. Dispositivo: {self.device}")

    def _load_model(self):
        """Carga el modelo y el tokenizador de forma perezosa."""
        global HF_AVAILABLE
        if not HF_AVAILABLE or self.is_loaded:
            return

        try:
            logger.info(f"Cargando modelo de corrección gramatical: {self.MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME, cache_dir=self.cache_dir)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.MODEL_NAME, cache_dir=self.cache_dir).to(self.device)
            self.is_loaded = True
            logger.info("Modelo de corrección gramatical cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al cargar el modelo de corrección: {e}", exc_info=True)
            # Desactivar para no reintentar continuamente
            HF_AVAILABLE = False

    def correct_text(self, text: str) -> Dict[str, Any]:
        """Corrige el texto proporcionado."""
        self._load_model()

        if not self.is_loaded:
            return {"error": "El servicio de corrección no está disponible."}

        try:
            # Para modelos T5, es común añadir un prefijo que indique la tarea.
            input_text = f"corregir: {text}"

            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=1024, # Aumentamos el límite para textos más largos
                truncation=True
            ).to(self.device)

            # Generar la corrección
            output_sequences = self.model.generate(
                input_ids=inputs.input_ids,
                max_length=1024,
                num_beams=5, # Usar beam search para mejores resultados
                early_stopping=True
            )

            corrected_text = self.tokenizer.decode(output_sequences[0], skip_special_tokens=True)

            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "model_used": self.MODEL_NAME
            }
        except Exception as e:
            logger.error(f"Error durante la corrección gramatical: {e}", exc_info=True)
            return {"error": str(e)}

# Instancia singleton para ser usada en la aplicación
grammatical_corrector_service = GrammaticalCorrector()
