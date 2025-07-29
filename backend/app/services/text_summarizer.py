"""
Servicio para resumir texto utilizando técnicas avanzadas de procesamiento de lenguaje natural.
Combina modelos transformers de Hugging Face para resúmenes abstractivos con técnicas extractivas.
"""

import nltk
import string
import heapq
import logging
import time
import os
import re
import json
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, asdict
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar dependencias de transformers
HF_AVAILABLE = False
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, T5Tokenizer, T5ForConditionalGeneration, AutoModelForSequenceClassification, pipeline, AutoModelForTokenClassification, BartForConditionalGeneration
    from transformers.utils.logging import set_verbosity_error
    import torch
    
    # Reducir verbosidad de transformers para mensajes no críticos
    set_verbosity_error()
    HF_AVAILABLE = True
    logger.info("Hugging Face Transformers disponible: modelos avanzados de resumen habilitados")
except ImportError as e:
    logger.warning(f"Hugging Face Transformers no disponible: {e}. Se usará el método extractivo básico.")
    logger.info("Para habilitar modelos avanzados: pip install transformers torch")

@dataclass
class ModelStatus:
    """Clase para almacenar el estado de un modelo."""
    loaded: bool = False
    model_name: str = ""
    retries: int = 0
    error_msg: str = ""
    last_error_time: float = 0.0
    recovery_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a un diccionario."""
        return asdict(self)

class TextSummarizer:
    """
    Clase para resumir textos utilizando algoritmos avanzados.
    Soporta tanto resumen extractivo (basado en NLTK) como abstractivo (basado en Hugging Face Transformers).
    """
    
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    local_model_path = os.path.join(backend_dir, 'local_models', 'spanish-summarizer')

    MODELS = {
        'primary': [
            # Modelos confirmados para español
            'mrm8488/bert2bert_shared-spanish-finetuned-summarization',  # Especializado para español
            'josmunpen/mt5-small-spanish-summarization',  # Modelo español fiable
            'facebook/bart-large-cnn'  # Modelo multilenguaje de alta calidad
        ],
        'multilingual': [], # Vaciamos para evitar modelos no deseados
        'fallback': [] # Vaciamos para evitar modelos de baja calidad
    }
    
    def __init__(self, model_name: Optional[str] = None, 
                max_input_length: int = 8192,
                max_output_length: int = 2048,
                cache_dir: Optional[str] = None,
                default_compression_ratio: float = 0.25,
                max_retries: int = 2,
                config_path: Optional[str] = None):
        
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Descargando recursos de NLTK (punkt, stopwords)...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

        self.stopwords = set(stopwords.words('spanish')) | set(stopwords.words('english'))
        
        # Configuración y modelos
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Usando dispositivo: {self.device}")
        
        # Parámetros básicos
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.default_compression_ratio = default_compression_ratio
        self.cache_dir = cache_dir
        
        # Inicializar atributos de modelo
        self.model_name = model_name  # Guardar el nombre del modelo solicitado
        self._summarizer = None
        self._summarizer_tokenizer = None
        self._correction_model = None
        self._correction_tokenizer = None
        self._ner_pipeline = None
        self._sentiment_model = None
        self.model_status = ModelStatus()
        
        # Configuraciones adicionales
        self.force_spanish_output = True  # Fuerza salida en español
        
        # Cargar configuración completa desde archivo JSON
        self._load_ai_config()
        
        # Si transformers está disponible, cargar modelos
        if HF_AVAILABLE:
            logger.info(f"Iniciando carga de modelos en dispositivo: {self.device}")
            
            # Cargar solo el modelo de resumen principal para evitar problemas de memoria
            # Los otros modelos se cargarán bajo demanda si es necesario
            summarization_models = self.models_config.get('summarization_models')
            if not summarization_models:
                logger.warning("No se encontraron modelos de resumen en la configuración. Usando modelo por defecto.")
                # Solo usar el primer modelo para evitar problemas de memoria
                summarization_models = [self.MODELS['primary'][0]]
            
            # Cargar modelos con estrategia de fallback completa
            if isinstance(summarization_models, list) and summarization_models:
                logger.info(f"Intentando cargar modelos con fallback: {summarization_models}")
                # Intentar cargar todos los modelos hasta que uno funcione
                self._load_model_with_fallback(summarization_models)
            elif summarization_models:
                # summarization_models es un string único
                logger.info(f"Cargando modelo único: {summarization_models}")
                self._load_model_with_fallback([summarization_models])
            else:
                # Usar modelo por defecto si no hay configuración
                logger.warning("No se encontraron modelos en configuración. Usando modelo por defecto.")
                default_models = [self.MODELS['primary'][0]]
                logger.info(f"Cargando modelo por defecto: {default_models}")
                self._load_model_with_fallback(default_models)

            # DESHABILITADO: Cargar modelos adicionales bajo demanda para evitar problemas de memoria
            # Estos se cargarán automáticamente cuando se necesiten
            logger.info("⚠️ Modelos adicionales (corrección, NER, sentimiento) se cargarán bajo demanda para optimizar memoria")
            # self._load_correction_model()
            # self._load_ner_model() 
            # self._load_sentiment_model()
        else:
            logger.error("Hugging Face Transformers no está instalado. Funcionalidad limitada.")

    def load_summarization_params(self) -> Dict[str, Any]:
        """Carga los parámetros de resumen desde el archivo de configuración."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            params = config.get('summarization_params', {})
            logger.info(f"Parámetros de resumen configurados: {params}")
            return params
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error al cargar o parsear ai_config.json: {e}")
            return {}

    def load_model_configs(self) -> Dict[str, Any]:
        """Carga las configuraciones de modelos desde el archivo de configuración."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            models = config.get('models', {})
            logger.info(f"Configuración de modelos cargada: {models}")
            return models
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error al cargar o parsear ai_config.json: {e}")
            return {}

    def _load_ai_config(self):
        """Carga los parámetros de IA desde un archivo de configuración JSON."""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'ai_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.ai_config = json.load(f)
            logger.info(f"Configuración de IA cargada desde {config_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"No se pudo cargar ai_config.json: {e}. Usando valores por defecto.")
            self.ai_config = {}

        # Extraer parámetros específicos
        self.summarization_params = self.ai_config.get('summarization_params', {})
        self.correction_params = self.ai_config.get('correction_params', {})
        self.models_config = self.ai_config.get('models', {})
        self.use_local_model = self.models_config.get('use_local_model', False)
        self.correction_model_name = self.models_config.get('grammar_correction_model')

        # Log de los parámetros cargados
        logger.info(f"Parámetros de resumen configurados: {self.summarization_params}")

    def _load_config(self):
        """Carga la configuración de modelos desde el archivo de configuración."""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'ai_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # La configuración de modelos está dentro de la clave 'models'
                self.model_configs = config.get('models', {})
                
                # Extraer variables de configuración específicas
                # Soportar tanto el formato antiguo como el nuevo
                self.correction_model_name = self.model_configs.get('grammar_correction_model')
                self.correction_models = self.model_configs.get('grammar_correction_models', [])
                self.use_local_model = self.model_configs.get('use_local_model', False)
                
                # Usar models_config para compatibilidad
                self.models_config = self.model_configs
                
                # Cargar parámetros de resumen
                self.summarization_params = config.get('summarization_params', {
                    'min_length': 50,
                    'max_length': 2048,
                    'compression_ratio': 0.25,
                    'num_beams': 8,
                    'length_penalty': 1.2,
                    'repetition_penalty': 1.8,
                    'top_k': 40,
                    'top_p': 0.9
                })
                
                # Valores por defecto para correction_params
                self.correction_params = config.get('correction_params', {
                    'max_length': 512,
                    'num_beams': 4,
                    'early_stopping': True,
                    'do_sample': False
                })
                
            logger.info(f"Configuración de modelos cargada desde {config_path}")
            logger.info(f"Parámetros de resumen cargados: {self.summarization_params}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"No se pudo cargar ai_config.json: {e}. Usando valores por defecto.")
            self.model_configs = {}
            # Valores por defecto para correction_params
            self.correction_params = {
                'max_length': 512,
                'num_beams': 4,
                'early_stopping': True,
                'do_sample': False
            }
            # Valores por defecto para summarization_params
            self.summarization_params = {
                'min_length': 50,
                'max_length': 2048,
                'compression_ratio': 0.25,
                'num_beams': 8,
                'length_penalty': 1.2,
                'repetition_penalty': 1.8,
                'top_k': 40,
                'top_p': 0.9
            }

    def _load_model_with_fallback(self, model_names: List[str]) -> bool:
        """
        Intenta cargar modelos en orden hasta que uno funcione.
        
        Args:
            model_names: Lista de nombres de modelos a intentar cargar
            
        Returns:
            bool: True si se cargó un modelo exitosamente, False en caso contrario
        """
        self._summarizer = None
        self._summarizer_tokenizer = None
        self.model_status.loaded = False
        
        if not model_names:
            logger.error("No se proporcionaron modelos para intentar cargar")
            return False
            
        logger.info(f"Intentando cargar modelos de la lista: {model_names}")
        
        # Eliminar duplicados preservando orden
        unique_candidates = list(dict.fromkeys(model_names))
        logger.info(f"Lista final de modelos candidatos (en orden): {unique_candidates}")

        # Intentar cargar cada modelo en orden
        for i, model_name in enumerate(unique_candidates):
            logger.info(f"Intento #{i+1}/{len(unique_candidates)}: Cargando modelo '{model_name}'")
            
            try:
                # Intentar cargar el tokenizador primero
                logger.info(f"Cargando tokenizador para '{model_name}'...")
                if 't5' in model_name.lower():
                    tokenizer = T5Tokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
                    logger.info(f"Tokenizador T5 cargado para '{model_name}'")
                else:
                    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
                    logger.info(f"AutoTokenizer cargado para '{model_name}'")
                
                # Ahora intentar cargar el modelo
                logger.info(f"Cargando modelo '{model_name}'...")
                if 't5' in model_name.lower():
                    model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=self.cache_dir)
                    model = model.to(self.device)
                elif 'bart' in model_name.lower():
                    model = BartForConditionalGeneration.from_pretrained(model_name, cache_dir=self.cache_dir)
                    model = model.to(self.device)
                else:
                    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=self.cache_dir)
                    model = model.to(self.device)
                
                # Si llegamos hasta aquí, asignamos el modelo y tokenizador
                self._summarizer = model
                self._summarizer_tokenizer = tokenizer
                self.model_name = model_name
                self.model_status.loaded = True
                self.model_status.model_name = model_name
                
                # Intentar una generación de prueba para verificar que funciona
                texto_prueba = "Este es un texto de prueba."
                try:
                    logger.info("Realizando prueba de generación con el modelo...")
                    # Usamos directamente el modelo para una prueba simple
                    tokens = self._summarizer_tokenizer(texto_prueba, return_tensors="pt").to(self.device)
                    logger.info(f"Tokenizador generó {len(tokens['input_ids'][0])} tokens")
                    
                    # Intentar una generación mínima
                    with torch.no_grad():
                        output_ids = self._summarizer.generate(
                            tokens['input_ids'],
                            max_length=20,
                            min_length=5,
                            num_beams=2
                        )
                    
                    output = self._summarizer_tokenizer.decode(output_ids[0], skip_special_tokens=True)
                    logger.info(f"Prueba de generación exitosa: '{output}'")
                    
                    logger.info(f"✅ Modelo '{model_name}' cargado y validado exitosamente!")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error en prueba de generación con '{model_name}': {e}")
                    self._summarizer = None
                    self._summarizer_tokenizer = None
                    self.model_name = None  # Reset model name when test fails
                    self.model_status.loaded = False
                    self.model_status.model_name = ""
                    continue
                    
            except Exception as e:
                logger.error(f"Error al cargar el modelo '{model_name}': {e}")
                continue

        # Si llegamos aquí, ningún modelo se cargó exitosamente
        logger.error("❌ No se pudo cargar ningún modelo de resumen después de todos los intentos.")
        self.model_status.error_msg = "Fallo al cargar todos los modelos de resumen disponibles."
        return False

    def detect_language(self, text: str) -> str:
        return 'spanish'

    def calculate_output_length(self, input_len: int, compression_ratio: float) -> Tuple[int, int]:
        """Calcula la longitud mínima y máxima del resumen basada en la longitud de entrada."""
        config_min_len = self.summarization_params.get('min_summary_words', 50)
        config_max_len = self.summarization_params.get('max_output_length', 2048)

        # Calcular la longitud máxima deseada basada en el ratio de compresión.
        calculated_max_len = int(input_len * compression_ratio)

        # Asegurar que la longitud máxima esté dentro de los límites globales de la configuración.
        # No puede ser más grande que config_max_len ni más pequeña que config_min_len.
        max_len = max(config_min_len, min(calculated_max_len, config_max_len))

        # La longitud mínima es la definida en la configuración, pero no puede ser mayor que max_len.
        min_len = min(config_min_len, max_len)
        
        # Caso extremo: si después de los cálculos min_len y max_len son iguales, 
        # se reduce un poco min_len para dar margen al modelo.
        if min_len == max_len and min_len > 10:
            min_len = max(10, int(min_len * 0.8))

        logger.info(f"Longitud de entrada: {input_len}. Longitud calculada: min={min_len}, max={max_len}")
        return min_len, max_len

    def _clean_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def evaluate_summary_quality(self, summary: str) -> float:
        """
        Evalúa la calidad de un resumen. Devuelve una puntuación entre 0.0 y 1.0.
        Un resumen de mayor calidad tendrá una puntuación más alta.
        """
        if not summary or summary is None:
            return 0.0
            
        # Criterios de evaluación simple
        score = 1.0
        
        # Penalizar resúmenes muy cortos (menos de 50 caracteres)
        if len(summary) < 50:
            score *= 0.5
        
        # Penalizar resúmenes truncados (que terminan en '...' o similar)
        if summary.endswith(('...', '…', '.', ',')):
            score *= 0.8
            
        # Penalizar resúmenes que contienen palabras en inglés comunes
        english_indicators = ['the', 'of', 'and', 'in', 'to', 'for', 'with', 'by']
        english_word_count = sum(1 for word in english_indicators if f' {word} ' in f' {summary.lower()} ')
        if english_word_count > 2:  # Si hay más de dos palabras en inglés
            score *= 0.7
            
        # Si hay tokens extraños
        if re.search(r'<.*?>', summary):
            score *= 0.9
            
        return score

    def _appears_to_be_english(self, text: str) -> bool:
        """Heurística simple para determinar si un texto parece estar en inglés."""
        if not text or len(text) < 10:
            return False
            
        # Palabras comunes en inglés que no existen o son raras en español
        english_markers = ['the', 'and', 'with', 'for', 'this', 'that', 'what', 'where', 
                           'when', 'how', 'which', 'who', 'is', 'are', 'were', 'was']
        
        # Palabras comunes en español que no existen o son raras en inglés
        spanish_markers = ['el', 'la', 'los', 'las', 'y', 'o', 'pero', 'porque', 'como', 'qué', 'quién', 'cómo', 'dónde', 'cuándo', 
                            'es', 'son', 'está', 'están']
                            
        words = re.findall(r'\b\w+\b', text.lower())
        
        english_count = sum(1 for w in words if w in english_markers)
        spanish_count = sum(1 for w in words if w in spanish_markers)
        
        # Si hay más palabras en inglés que en español, probablemente es inglés
        return english_count > spanish_count and english_count > 2
        
    def _try_load_summarizer_model(self, model_name: str) -> bool:
        """
        Intenta cargar un modelo específico de resumen.
        
        Args:
            model_name: Nombre del modelo a cargar
            
        Returns:
            bool: True si se cargó exitosamente, False en caso contrario
        """
        try:
            logger.info(f"Intentando cargar modelo de resumen: '{model_name}'")
            
            # Cargar tokenizer
            if 't5' in model_name.lower():
                tokenizer = T5Tokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
            
            # Cargar modelo
            if 't5' in model_name.lower():
                model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=self.cache_dir)
            elif 'bart' in model_name.lower():
                model = BartForConditionalGeneration.from_pretrained(model_name, cache_dir=self.cache_dir)
            else:
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=self.cache_dir)
            
            model = model.to(self.device)
            
            # Asignar el modelo cargado
            self._summarizer = model
            self._summarizer_tokenizer = tokenizer
            self.model_name = model_name
            
            logger.info(f"Modelo '{model_name}' cargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar modelo '{model_name}': {e}")
            return False

    def _summarize_nltk(self, text: str, lang: str, max_sentences: int = 5, max_length: Optional[int] = None) -> Dict[str, Any]:
        sentences = sent_tokenize(text, language=lang)
        if not sentences:
            return {'summary': '', 'sentences': 0}
        word_frequencies = {}
        for word in word_tokenize(text.lower(), language=lang):
            if word not in self.stopwords and word not in string.punctuation:
                word_frequencies[word] = word_frequencies.get(word, 0) + 1
        if not word_frequencies:
             return {'summary': ' '.join(sentences[:max_sentences]), 'sentences': len(sentences[:max_sentences])}
        max_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word] / max_frequency)
        sentence_scores = {}
        for sent in sentences:
            for word in word_tokenize(sent.lower(), language=lang):
                if word in word_frequencies:
                    if len(sent.split(' ')) < 30:
                        sentence_scores[sent] = sentence_scores.get(sent, 0) + word_frequencies[word]
        summary_sentences = heapq.nlargest(max_sentences, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return {'summary': self.post_process_summary(summary), 'sentences': len(summary_sentences)}

    def _generate_summary_hf(self, text: str, compression_ratio: float) -> Dict[str, Any]:
        try:
            # Preparamos el prompt según el idioma del modelo
            if self.force_spanish_output or 'spanish' in self.model_name.lower():
                input_text = f"resumir: {self._clean_text(text)}"
                if self.force_spanish_output:
                    input_text = f"resumir en español: {self._clean_text(text)}"
            else:
                input_text = f"summarize: {self._clean_text(text)}"
                
            # Tokenización y generación
            inputs = self._summarizer_tokenizer(input_text, return_tensors="pt", max_length=self.max_input_length, truncation=True, padding="longest").to(self.device)
            
            # Cargar parámetros y decidir la longitud del resumen
            generation_params = self.summarization_params.copy()
            if not generation_params.get('min_length') or not generation_params.get('max_length'):
                min_len, max_len = self.calculate_output_length(inputs["input_ids"].shape[1], compression_ratio)
                generation_params['min_length'] = min_len
                generation_params['max_length'] = max_len

            generation_params["attention_mask"] = inputs.get("attention_mask", None)
            
            # Registro detallado de parámetros
            logger.info(f"Generando resumen con prompt: '{input_text[:50]}...' y parámetros: {json.dumps({k: str(v) for k, v in generation_params.items() if k != 'attention_mask'}, indent=2)}")
            
            # Primer intento: Group beam search con diversidad (requiere do_sample=False)
            try:
                first_attempt_params = generation_params.copy()
                if first_attempt_params.get('diversity_penalty', 0) > 0 and first_attempt_params.get('num_beam_groups', 1) > 1:
                    # Para group beam search, do_sample debe ser False
                    first_attempt_params['do_sample'] = False
                    # Remover parámetros de sampling que no son compatibles
                    for param in ['temperature', 'top_k', 'top_p']:
                        first_attempt_params.pop(param, None)
                    
                logger.info("Primer intento: generación con group beam search")
                summary_ids = self._summarizer.generate(inputs["input_ids"], **first_attempt_params)
                
            except Exception as e:
                logger.warning(f"Primer intento falló: {e}. Intentando con parámetros alternativos...")
                
                # Segundo intento: Beam search normal con sampling
                second_attempt_params = {
                    'min_length': generation_params['min_length'],
                    'max_length': generation_params['max_length'],
                    'num_beams': 4,  # Sin grupos
                    'do_sample': True,
                    'temperature': 0.8,
                    'top_p': 0.95,
                    'top_k': 50,
                    'repetition_penalty': 1.8,
                    'early_stopping': False,  # Forzar resúmenes más largos
                    'attention_mask': generation_params.get('attention_mask')
                }
                
                logger.info("Segundo intento: generación con sampling y beam search simple")
                summary_ids = self._summarizer.generate(inputs["input_ids"], **second_attempt_params)
            summary = self._summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            processed_summary = self.post_process_summary(summary)
            # Aplicar limpieza adicional para eliminar artefactos
            cleaned_summary = self._clean_summary_text(processed_summary, input_text)
            
            # Si debemos forzar español y el resumen parece en inglés, intentamos traducirlo
            if self.force_spanish_output and self._appears_to_be_english(cleaned_summary):
                logger.warning(f"El resumen parece estar en inglés a pesar de solicitar español: {cleaned_summary[:50]}...")
                try:
                    # Intento de reformulación en español usando el mismo modelo
                    translate_input = f"traducir al español: {cleaned_summary}"
                    translate_tokens = self._summarizer_tokenizer(translate_input, return_tensors="pt", max_length=self.max_input_length, truncation=True).to(self.device)
                    translate_ids = self._summarizer.generate(
                        translate_tokens["input_ids"],
                        max_length=int(len(cleaned_summary.split()) * 1.5),  # 50% más largo para acomodar traducción
                        num_beams=5,
                        length_penalty=1.2
                    )
                    spanish_summary = self._summarizer_tokenizer.decode(translate_ids[0], skip_special_tokens=True)
                    logger.info(f"Resumen traducido al español: {spanish_summary[:50]}...")
                    cleaned_summary = spanish_summary
                except Exception as e:
                    logger.error(f"Error al intentar traducir el resumen a español: {str(e)}")
            
            return {"summary": cleaned_summary, "model_name": self.model_name}
        except Exception as e:
            logger.error(f"Error al generar el resumen con Hugging Face: {str(e)}")
            logger.exception(e)
            return {"summary": "", "model_name": self.model_name, "error": str(e)}

    def generate_summary(self, text: str, compression_ratio: Optional[float] = None, min_length: Optional[int] = None, max_length: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Genera un resumen de un texto dado, aplicando corrección gramatical al resultado si está disponible."""
        if not text:
            return {"summary": "", "error": "No se proporcionó texto para resumir."}
        
        logger.info(f"🔍 INICIO generate_summary - model_name: '{self.model_name}', model_loaded: {self.model_status.loaded}")
        
        try:
            # Si no hay modelo cargado, usar el método extractivo de NLTK
            if self._summarizer is None:
                logger.warning("No hay modelos de resumen disponibles. Usando NLTK (extractivo).")
                return self._summarize_nltk(text, self.detect_language(text), max_sentences=3)
                
            # Estrategia de múltiples modelos con evaluación de calidad
            result = self._generate_summary_with_best_model(text, compression_ratio or self.default_compression_ratio)
            
            # # Aplicar corrección gramatical al mejor resultado si está disponible
            # if self._correction_model is not None and result.get("summary"):
            #     logger.info("Aplicando corrección gramatical al resumen generado...")
            #     corrected_result = self.correct_grammar(result["summary"])
            #     corrected = corrected_result.get("corrected_text", "")
                
            #     # Verificar que la corrección no esté vacía y sea mejor que el original
            #     if corrected and len(corrected) > len(result["summary"]) * 0.5:
            #         if self._is_correction_better(result["summary"], corrected):
            #             logger.info("El resumen fue mejorado por el corrector gramatical.")
            #             result["summary"] = corrected
            #         else:
            #             logger.info("La corrección no mejoró el resumen. Manteniendo el original.")
            #     else:
            #         logger.warning("La corrección gramatical produjo un resultado vacío o muy corto. Usando resumen original.")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al generar el resumen: {e}", exc_info=True)
            return {"summary": "", "error": str(e)}

    def _generate_summary_with_best_model(self, text: str, compression_ratio: float) -> Dict[str, Any]:
        """
        Intenta generar un resumen con varios modelos diferentes y devuelve el de mejor calidad.
        La estrategia es:
        1. Probar con el modelo actual (si existe)
        2. Si el resumen es de baja calidad, intentar con otros modelos de la lista de candidatos
        3. Devolver el resumen de mayor calidad encontrado
        """
        results = []
        current_model_result = None
        models_to_try = []
        
        # Primero intentar con el modelo ya cargado, si existe
        if self._summarizer is not None:
            try:
                logger.info(f"Generando resumen con el modelo actual '{self.model_name}'...")
                logger.debug(f"DEBUG: Model status - loaded: {self.model_status.loaded}, model_name: '{self.model_status.model_name}'")
                logger.debug(f"DEBUG: Instance model_name: '{self.model_name}'")
                logger.debug(f"DEBUG: Summarizer model is None: {self._summarizer is None}")
                logger.debug(f"DEBUG: Summarizer tokenizer is None: {self._summarizer_tokenizer is None}")
                current_model_result = self._generate_summary_hf(text, compression_ratio)
                current_quality = self.evaluate_summary_quality(current_model_result.get("summary", ""))
                results.append(current_model_result)
                
                # Si la calidad es buena (> 0.7), no necesitamos probar más modelos
                if current_quality > 0.7:
                    logger.info(f"Resumen de buena calidad (score: {current_quality:.2f}) obtenido con el modelo actual. No se intentarán otros modelos.")
                    return current_model_result
                else:
                    logger.warning(f"Resumen de baja calidad (score: {current_quality:.2f}). Intentando con modelos alternativos...")
            except Exception as e:
                logger.error(f"Error al generar resumen con el modelo actual: {e}")
        
        # Si llegamos aquí, necesitamos probar con modelos alternativos
        # Usaremos los modelos definidos en self.MODELS['primary'] que no sean el actual
        for model_name in self.MODELS['primary']:
            # Evitar repetir el modelo actual
            if model_name == self.model_name:
                continue
                
            try:
                # Guardar el modelo y tokenizer actuales para restaurarlos después
                original_model = self._summarizer
                original_tokenizer = self._summarizer_tokenizer
                original_model_name = self.model_name
                
                # Cargar temporalmente el nuevo modelo
                logger.info(f"Intentando cargar modelo alternativo: '{model_name}'")
                if self._try_load_summarizer_model(model_name):
                    # Si se cargó correctamente, generar resumen
                    logger.info(f"Generando resumen con modelo alternativo '{model_name}'...")
                    alt_result = self._generate_summary_hf(text, compression_ratio)
                    alt_quality = self.evaluate_summary_quality(alt_result.get("summary", ""))
                    logger.info(f"Resumen generado con '{model_name}'. Calidad: {alt_quality:.2f}")
                    results.append(alt_result)
                
                # Restaurar el modelo original
                self._summarizer = original_model
                self._summarizer_tokenizer = original_tokenizer
                self.model_name = original_model_name
                
            except Exception as e:
                logger.error(f"Error al probar con modelo alternativo '{model_name}': {e}")
        
        # Si no hay resultados, devolver error
        if not results:
            return {"summary": "", "error": "No se pudo generar un resumen con ninguno de los modelos disponibles."}
        
        # Evaluar calidad de cada resumen y elegir el mejor
        best_result = max(results, key=lambda x: self.evaluate_summary_quality(x.get("summary", "")))
        best_quality = self.evaluate_summary_quality(best_result.get("summary", ""))
        logger.info(f"Se seleccionó el mejor resumen con calidad {best_quality:.2f}")
        
        return best_result

    def _is_correction_better(self, original: str, corrected: str) -> bool:
        # Comparar calidad de resumen original y corregido
        original_quality = self.evaluate_summary_quality(original)
        corrected_quality = self.evaluate_summary_quality(corrected)
        return corrected_quality > original_quality
    
    def _is_valid_entity(self, entity_text: str, confidence: float = 0.5) -> bool:
        """
        Valida si una entidad extraída es de calidad suficiente para ser incluida.
        
        Args:
            entity_text: Texto de la entidad
            confidence: Nivel de confianza del modelo NER (0.0 a 1.0)
            
        Returns:
            bool: True si la entidad es válida, False si debe ser filtrada
        """
        if not entity_text or not entity_text.strip():
            return False
        
        entity_text = entity_text.strip()
        
        # Filtrar entidades muy cortas (menos de 2 caracteres)
        if len(entity_text) < 2:
            return False
            
        # Filtrar tokens que son solo espacios o puntuación
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', entity_text):
            return False
            
        # Filtrar fragmentos de palabras comunes en inglés que no son nombres propios
        english_fragments = ['the', 'and', 'with', 'for', 'ht', 'th', 'er', 'ing', 'ed']
        if entity_text.lower() in english_fragments:
            return False
            
        # Filtrar artículos y preposiciones en español (si no tienen mayúscula inicial)
        spanish_stopwords = ['el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'por', 'para']
        if entity_text.lower() in spanish_stopwords and not entity_text[0].isupper():
            return False
            
        # Filtrar entidades con confianza muy baja
        if confidence < 0.65:
            return False
            
        # Filtrar palabras que son solo números o caracteres especiales
        if entity_text.isdigit() or all(c in '.,;:!?()[]{}"\'-' for c in entity_text):
            return False
            
        return True

    def keywords(self, text, max_keywords=10):
        if not text: return []
        tokens = word_tokenize(text.lower())
        filtered_tokens = [word for word in tokens if word.isalpha() and word not in self.stopwords]
        freq_dist = nltk.FreqDist(filtered_tokens)
        return [word for word, freq in freq_dist.most_common(max_keywords)]

    def _load_ner_model(self):
        logger.info("🔄 Iniciando carga del modelo NER...")
        if self._ner_pipeline: 
            logger.info("Pipeline NER ya está cargado, saltando.")
            return
        
        # Lista de modelos NER compatibles para español
        ner_models = [
            "mrm8488/bert-spanish-cased-finetuned-ner",  # Más estable
            "dslim/bert-base-NER",                       # Multiidioma, compatible
            "dbmdz/bert-large-cased-finetuned-conll03-english"  # Fallback en inglés
        ]
        
        for model_id in ner_models:
            try:
                logger.info(f"🔄 Intentando cargar modelo NER: {model_id}")
                
                # Cargar con configuraciones específicas para evitar errores
                self._ner_pipeline = pipeline(
                    "ner", 
                    model=model_id, 
                    tokenizer=model_id, 
                    device=-1,  # Forzar CPU para evitar problemas
                    grouped_entities=True,  # Agrupar entidades relacionadas
                    aggregation_strategy="simple",  # Estrategia de agregación simple
                    ignore_labels=[],  # No ignorar etiquetas por defecto
                )
                
                # Hacer una prueba rápida
                test_result = self._ner_pipeline("María vive en Madrid y trabaja en Barcelona")
                logger.info(f"✅ Pipeline NER cargado exitosamente: {model_id}")
                logger.info(f"Prueba NER exitosa. Entidades encontradas: {len(test_result)}")
                return
                
            except Exception as e:
                logger.warning(f"❌ Error con modelo NER '{model_id}': {e}")
                continue
        
        logger.error("❌ No se pudo cargar ningún modelo NER")
        self._ner_pipeline = None

    def extract_entities(self, text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
        logger.info(f"Iniciando extracción de entidades para texto de {len(text)} caracteres...")
        
        # Lazy loading: cargar modelo NER bajo demanda
        if not self._ner_pipeline: 
            logger.info("🔄 Cargando modelo NER bajo demanda...")
            try:
                self._load_ner_model()
                if not self._ner_pipeline:
                    logger.warning("❌ No se pudo cargar pipeline NER. Devolviendo diccionario vacío.")
                    return {}
            except Exception as e:
                logger.error(f"Error al cargar modelo NER bajo demanda: {e}")
                return {}
        
        try:
            logger.info("Ejecutando pipeline NER...")
            entities = self._ner_pipeline(text)
            logger.info(f"Pipeline NER devolvió {len(entities)} entidades brutas")
            
            # Definir entidades relevantes que queremos mostrar (filtrar 'O' y otros irrelevantes)
            relevant_entity_types = {'PER', 'LOC', 'ORG', 'MISC', 'PERSON', 'LOCATION', 'ORGANIZATION'}
            
            # Mapeo de etiquetas a español para mejor UX
            label_translation = {
                'PER': 'Personas',
                'PERSON': 'Personas', 
                'LOC': 'Lugares',
                'LOCATION': 'Lugares',
                'ORG': 'Organizaciones',
                'ORGANIZATION': 'Organizaciones',
                'MISC': 'Otros'
            }
            
            extracted_data = {}
            for entity in entities:
                label = entity['entity_group']
                word = entity['word'].strip()
                confidence = entity.get('score', 0.0)
                
                # FILTRO 1: Solo procesar entidades relevantes (no 'O' ni otros tokens irrelevantes)
                if label not in relevant_entity_types:
                    logger.debug(f"Entidad irrelevante filtrada: {label} -> {word}")
                    continue
                    
                # FILTRO 2: Filtros de calidad para entidades
                if self._is_valid_entity(word, confidence):
                    logger.info(f"✅ Procesando entidad válida: {label} -> {word} (confianza: {confidence:.2f})")
                    
                    # FILTRO 3: Aplicar filtro de tipos específicos si se especifica
                    if not entity_types or label in entity_types:
                        # Usar etiqueta en español para mejor UX
                        spanish_label = label_translation.get(label, label)
                        
                        if spanish_label not in extracted_data:
                            extracted_data[spanish_label] = []
                        if word not in extracted_data[spanish_label]:
                            extracted_data[spanish_label].append(word)
                else:
                    logger.debug(f"Entidad filtrada por baja calidad: {label} -> {word} (confianza: {confidence:.2f})")
                        
            logger.info(f"✅ Entidades extraidas finales: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Error al extraer entidades: {e}", exc_info=True)
            return {}

    def _load_sentiment_model(self):
        if self._sentiment_model: return
        
        # Usar modelos de la configuración actualizada
        config_models = self.models_config.get('sentiment_models', [])
        
        # Modelos por defecto más compatibles si no hay configuración
        default_models = [
            "nlptown/bert-base-multilingual-uncased-sentiment",  # Más estable para español
            "cardiffnlp/twitter-xlm-roberta-base-sentiment",    # Multiidioma, sin meta tensor issues
            "distilbert-base-uncased-finetuned-sst-2-english"   # Fallback básico
        ]
        
        models_to_try = config_models if config_models else default_models
        
        for model_id in models_to_try:
            try:
                logger.info(f"🔄 Intentando cargar modelo de sentimiento: {model_id}")
                
                # Cargar con configuraciones específicas para evitar errores de meta tensor
                self._sentiment_model = pipeline(
                    "sentiment-analysis", 
                    model=model_id, 
                    device=-1,  # Forzar CPU para evitar problemas de GPU
                    return_all_scores=False,  # Solo el resultado principal
                    truncation=True,  # Truncar texto largo automáticamente
                    max_length=512    # Límite de longitud para evitar problemas
                )
                
                # Hacer una prueba rápida
                test_result = self._sentiment_model("Este es un texto de prueba")
                logger.info(f"✅ Pipeline de sentimiento cargado exitosamente: {model_id}")
                logger.info(f"Prueba exitosa: {test_result}")
                return
                
            except Exception as e:
                logger.warning(f"❌ Error con modelo '{model_id}': {e}")
                continue
        
        logger.error("❌ No se pudo cargar ningún modelo de análisis de sentimiento")
        self._sentiment_model = None

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        # Lazy loading: cargar modelo de sentimiento bajo demanda
        if not self._sentiment_model: 
            logger.info("🔄 Cargando modelo de análisis de sentimiento bajo demanda...")
            try:
                self._load_sentiment_model()
                if not self._sentiment_model:
                    return {"label": "NEU", "score": 0.0, "error": "No se pudo cargar modelo de sentimiento"}
            except Exception as e:
                logger.error(f"Error al cargar modelo de sentimiento bajo demanda: {e}")
                return {"label": "NEU", "score": 0.0, "error": "Modelo no disponible"}
                
        try:
            # Limitamos el texto para evitar errores de tamaño
            max_len = min(512, getattr(self._sentiment_model.tokenizer, 'model_max_length', 512))
            truncated_text = text[:max_len] if len(text) > max_len else text
            
            logger.debug(f"Analizando sentimiento de texto de {len(truncated_text)} caracteres")
            results = self._sentiment_model(truncated_text)
            
            if not results or len(results) == 0:
                return {"label": "NEU", "score": 0.0, "error": "Análisis fallido"}
                
            main_result = results[0]
            label = main_result.get('label', 'UNKNOWN')
            score = main_result.get('score', 0.0)
            
            # Mapear etiquetas en inglés a español
            label_mapping = {
                'POSITIVE': 'POS',
                'NEGATIVE': 'NEG', 
                'NEUTRAL': 'NEU',
                'LABEL_0': 'NEG',  # Para algunos modelos
                'LABEL_1': 'POS',  # Para algunos modelos
                'LABEL_2': 'NEU'   # Para algunos modelos
            }
            
            mapped_label = label_mapping.get(label.upper(), 'NEU')
            logger.info(f"Análisis de sentimiento exitoso: {mapped_label} (confianza: {score:.2f})")
            
            return {"label": mapped_label, "score": float(score)}
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimiento: {e}")
            # Retornar resultado neutro en caso de error
            return {"label": "NEU", "score": 0.0, "error": "Análisis de sentimiento falló, usando neutro"}

    # El método _load_model_with_fallback duplicado ha sido eliminado.
    # Se usa la versión corregida de arriba que maneja listas de modelos correctamente.
        
    def _try_load_summarizer_model(self, model_name: str) -> bool:
        """
        Intenta cargar temporalmente un modelo alternativo para generar un resumen.
        Devuelve True si se cargó correctamente, False en caso contrario.
        """
        try:
            if os.path.exists(model_name):
                logger.info(f"Cargando modelo local alternativo desde: {model_name}")
            else:
                logger.info(f"Descargando modelo alternativo desde Hugging Face: {model_name}")
                
            self._summarizer_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._summarizer = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
            self.model_name = model_name
            return True
        except Exception as e:
            logger.error(f"No se pudo cargar el modelo alternativo '{model_name}': {e}")
            return False

    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        sentences = sent_tokenize(text, language='spanish')
        chunks = []
        current_chunk = sentences[0] if sentences else ""
        
        for sentence in sentences[1:]:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        # No olvidar el último fragmento
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks

    def _load_correction_model(self, model_id: Optional[str] = None) -> None:
        """
        Carga el modelo de corrección gramatical usando modelos ligeros.
        
        Args:
            model_id: ID del modelo de corrección a cargar desde Hugging Face
        """
        # Usar modelos de la configuración actualizada (más ligeros)
        config_models = self.models_config.get('grammar_correction_models', [])
        
        # Modelos ligeros por defecto si no hay configuración
        default_models = [
            "google/mt5-small",     # Modelo pequeño y confiable
            "t5-small",            # Modelo base muy ligero
            "google/flan-t5-small" # Alternativa ligera
        ]
        
        model_candidates = []
        
        # Agregar modelo específico si se proporciona
        if model_id:
            model_candidates.append(model_id)
            
        # Usar modelos de configuración o defaults
        if config_models:
            model_candidates.extend(config_models)
        else:
            model_candidates.extend(default_models)
        
        # Eliminar duplicados manteniendo orden
        unique_candidates = list(dict.fromkeys(model_candidates))
        logger.info(f"Candidatos para modelo de corrección: {unique_candidates}")

        for model_to_try in unique_candidates:
            try:
                logger.info(f"Intentando cargar modelo de corrección: '{model_to_try}'")
                self._correction_tokenizer = AutoTokenizer.from_pretrained(model_to_try)
                self._correction_model = AutoModelForSeq2SeqLM.from_pretrained(model_to_try).to(self.device)
                self.correction_model_name = model_to_try
                
                # Ajustar los parámetros de generación según el modelo
                if "spanish" in model_to_try.lower():
                    self.correction_params.update({
                        'num_beams': 5,
                        'max_length': 512,
                        'early_stopping': True,
                        'do_sample': False
                    })
                
                logger.info(f"Modelo de corrección '{model_to_try}' cargado exitosamente.")
                return
            except Exception as e:
                logger.warning(f"No se pudo cargar el modelo de corrección '{model_to_try}': {e}")
        
        logger.error("No se pudo cargar ningún modelo de corrección gramatical.")
        self._correction_model = None
        self._correction_tokenizer = None
        
    def post_process_summary(self, text: str) -> str:
        """Procesa el texto del resumen para eliminar prompts, prefijos y texto extraño.
        
        Args:
            text: Texto a procesar del modelo de resumen.
            
        Returns:
            Texto limpio, solo el resumen en español.
        """
        if not text:
            return ""
        
        import re
        processed_text = text.strip()
        
        # PASO 1: Eliminar tokens especiales problemáticos como <extra_id_X>
        # Eliminar tokens <extra_id_X> que aparecen con modelos T5/mT5
        processed_text = re.sub(r'<extra_id_\d+>', '', processed_text)
        # Eliminar otros tokens especiales comunes
        processed_text = re.sub(r'<pad>|<unk>|<s>|</s>|<eos>|<bos>', '', processed_text)
        # Eliminar tokens de padding o separadores
        processed_text = re.sub(r'\[PAD\]|\[UNK\]|\[CLS\]|\[SEP\]|\[MASK\]', '', processed_text)
        
        # PASO 2: Eliminar prompts que aparecen en el resumen
        prompts_to_remove = [
            "resumir en español:", "summarize:", "resume:", "resumen:",
            "resumir:", "texto a resumir:", "summary:", "resumen en español:"
        ]
        
        # Buscar y eliminar prompts (case insensitive)
        text_lower = processed_text.lower()
        for prompt in prompts_to_remove:
            if text_lower.startswith(prompt.lower()):
                processed_text = processed_text[len(prompt):].strip()
                break
        
        # PASO 3: Eliminar prefijos comunes de modelos
        prefixes_to_remove = [
            "Corresponding in Spanish:", "In Spanish:", "Translation:", "Corrected text:", 
            "Corrected sentence:", "Spanish correction:", "Spanish translation:", 
            "Corrected version:", "Grammar correction:", "Corrected grammar:",
            "El resumen es:", "Resumen:"
        ]
        
        for prefix in prefixes_to_remove:
            if processed_text.startswith(prefix):
                processed_text = processed_text[len(prefix):].strip()
        
        # PASO 4: Eliminar comillas y caracteres extraños
        processed_text = processed_text.strip('"').strip("'").strip()
        
        # PASO 5: Eliminar patrones extraños al inicio
        processed_text = re.sub(r'^[A-Z][a-z]+: [A-Z][a-z]+ [A-Z][a-z]+ de [A-Z][a-z]+\.\s*', '', processed_text)
        
        # PASO 6: Limpiar fragmentos de prompt que quedan
        processed_text = re.sub(r'\b(resumir|summary|resumen)\s+(en\s+español|in\s+spanish)\s*:?\s*', '', processed_text, flags=re.IGNORECASE)
        
        # PASO 7: Corregir palabras en inglés comunes que aparecen en resúmenes
        english_to_spanish = {
            r'\bis\b': 'es',
            r'\bare\b': 'son', 
            r'\bthe\b': 'el',
            r'\band\b': 'y',
            r'\bof\b': 'de',
            r'\bto\b': 'a',
            r'\bin\b': 'en',
            r'\bfor\b': 'para',
            r'\bwith\b': 'con',
            r'\bthat\b': 'que',
            r'\bthis\b': 'este',
            r'\bhas\b': 'tiene',
            r'\bhave\b': 'tienen'
        }
        
        # Aplicar correcciones de inglés a español
        for english_pattern, spanish_word in english_to_spanish.items():
            processed_text = re.sub(english_pattern, spanish_word, processed_text, flags=re.IGNORECASE)
        
        # PASO 8: Si el texto contiene ":", verificar si es formato "etiqueta: contenido"
        if ":" in processed_text:
            parts = processed_text.split(":", 1)
            if len(parts) == 2 and len(parts[0].split()) <= 3:
                # Si la primera parte es corta, probablemente sea una etiqueta
                potential_content = parts[1].strip()
                if len(potential_content) > 20:  # Solo si el contenido es sustancial
                    processed_text = potential_content
        
        # PASO 9: Detectar y eliminar frases en inglés
        sentences = re.split(r'(?<=[.!?])\s+', processed_text)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not self._appears_to_be_english(sentence):
                cleaned_sentences.append(sentence)
        
        final_text = " ".join(cleaned_sentences).strip()
        
        # PASO 10: Capitalizar primera letra si es necesario
        if final_text and final_text[0].islower():
            final_text = final_text[0].upper() + final_text[1:]
        
        # PASO 11: Limpiar espacios múltiples
        final_text = re.sub(r'\s+', ' ', final_text).strip()
            
        return final_text
        
    def correct_grammar(self, text: str) -> dict:
        # Lazy loading: cargar modelo de corrección bajo demanda
        if not self._correction_model or not self._correction_tokenizer:
            logger.info("🔄 Cargando modelo de corrección gramatical bajo demanda...")
            try:
                self._load_correction_model()
                if not self._correction_model or not self._correction_tokenizer:
                    return {"corrected_text": text, "corrections": [], "error": "No se pudo cargar el modelo de corrección"}
            except Exception as e:
                logger.error(f"Error al cargar modelo de corrección bajo demanda: {e}")
                return {"corrected_text": text, "corrections": [], "error": "Modelo no disponible"}

        try:
            # Si el texto es muy corto, aplicar corrección directa
            if len(text) < 100:
                return self._correct_single_text(text)
                
            chunks = self._split_text_into_chunks(self._clean_text(text))
            corrected_chunks = []
            logger.info(f"Iniciando corrección gramatical en {len(chunks)} fragmentos...")

            for i, chunk in enumerate(chunks):
                if not chunk.strip(): 
                    continue
                    
                logger.debug(f"Corrigiendo fragmento {i+1}/{len(chunks)}: {chunk[:50]}...")
                
                # Usar un prompt más simple y directo
                input_text = f"corregir: {chunk.strip()}"
                tokenized_chunk = self._correction_tokenizer(
                    input_text, 
                    return_tensors='pt', 
                    truncation=True, 
                    max_length=400,
                    padding=True
                ).to(self.device)
                
                generation_params = self.correction_params.copy()
                generation_params.update({
                    'input_ids': tokenized_chunk.input_ids,
                    'attention_mask': tokenized_chunk.attention_mask,
                    'max_length': min(len(tokenized_chunk.input_ids[0]) + 50, 512),
                    'do_sample': False,
                    'temperature': 1.0
                })

                corrected_ids = self._correction_model.generate(**generation_params)
                corrected_text_chunk = self._correction_tokenizer.decode(
                    corrected_ids[0], 
                    skip_special_tokens=True, 
                    clean_up_tokenization_spaces=True
                )
                
                # Limpiar la corrección
                corrected_text_chunk = self._clean_corrected_text(corrected_text_chunk, chunk)
                if corrected_text_chunk.strip():
                    corrected_chunks.append(corrected_text_chunk.strip())

            final_corrected_text = " ".join(corrected_chunks)
            
            # Post-procesar solo para correcciones, no para resúmenes
            final_corrected_text = self._post_process_correction(final_corrected_text)
            
            logger.info(f"Corrección gramatical completada: {len(text)} -> {len(final_corrected_text)} caracteres")
            return {"corrected_text": final_corrected_text, "corrections": []}
            
        except Exception as e:
            logger.error(f"Error durante la corrección gramatical: {e}")
            return {"corrected_text": text, "corrections": [], "error": str(e)}
    
    def _correct_single_text(self, text: str) -> dict:
        """Corrige un texto corto directamente."""
        try:
            input_text = f"corregir: {text.strip()}"
            inputs = self._correction_tokenizer(
                input_text, 
                return_tensors='pt', 
                truncation=True, 
                max_length=300
            ).to(self.device)
            
            outputs = self._correction_model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=min(len(inputs.input_ids[0]) + 30, 400),
                num_beams=3,
                do_sample=False,
                early_stopping=True
            )
            
            corrected = self._correction_tokenizer.decode(outputs[0], skip_special_tokens=True)
            corrected = self._clean_corrected_text(corrected, text)
            return {"corrected_text": corrected, "corrections": []}
            
        except Exception as e:
            logger.error(f"Error en corrección de texto corto: {e}")
            return {"corrected_text": text, "corrections": []}
    
    def _clean_summary_text(self, summary: str, original_text: str) -> str:
        """Limpia el texto del resumen eliminando artefactos y secuencias extrañas."""
        if not summary:
            return summary
            
        logger.info(f"🧹 Limpiando resumen: '{summary[:100]}...'")
        
        # PASO 1: Eliminar acrónimos y códigos extraños al final
        # Patrón para secuencias como "TMY CUCD USB LED O"
        summary = re.sub(r'\s+[A-Z]{2,}(\s+[A-Z]{2,})*\s*$', '', summary)
        summary = re.sub(r'\s+[A-Z]+\d+[A-Z]*\s*$', '', summary)
        summary = re.sub(r'\s+\b[A-Z]{1,4}\b(\s+\b[A-Z]{1,4}\b){2,}\s*$', '', summary)
        
        # PASO 2: Eliminar secuencias de números y fechas extrañas
        summary = re.sub(r'\s+\d{1,2}:\d{1,2}/\d{4}\s*', '', summary)
        summary = re.sub(r'\s+\d{4}-\d{2}-\d{2}\s*', '', summary)
        
        # PASO 3: Eliminar texto que parece código o referencias técnicas al final
        summary = re.sub(r'\s+(ET|ING|USB|LED|CD|DVD)\s*$', '', summary, flags=re.IGNORECASE)
        
        # PASO 4: Eliminar fragmentos que parecen metadatos
        summary = re.sub(r'\s+[A-Z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$', '', summary)
        
        # PASO 5: Limpiar espacios múltiples
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # PASO 6: Si el resumen quedó muy corto o vacío, intentar recuperar
        if len(summary) < 50 and len(original_text) > 100:
            logger.warning("Resumen muy corto después de limpieza, usando post_process_summary")
            return self.post_process_summary(summary)
            
        logger.info(f"✅ Resumen limpiado: '{summary[:100]}...'")
        return summary
    
    def _clean_corrected_text(self, corrected: str, original: str) -> str:
        """Limpia el texto corregido eliminando prompts y artefactos."""
        if not corrected:
            return original
            
        # Eliminar múltiples tipos de prompts que pueden aparecer
        prompt_patterns = [
            r'^\s*(corregir|correct|corrección|grammar|gramática)\s*:?\s*',
            r'^\s*(fix|repair|improve)\s*:?\s*',
            r'^\s*(spanish|español)\s*:?\s*',
            r'^\s*(text|texto)\s*:?\s*'
        ]
        
        for pattern in prompt_patterns:
            corrected = re.sub(pattern, '', corrected, flags=re.IGNORECASE)
        
        # Eliminar líneas que son claramente prompts o instrucciones en inglés
        lines = corrected.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Eliminar líneas que son prompts/instrucciones en inglés
            if any(phrase in line.lower() for phrase in [
                'correct the following', 'fix the grammar', 'improve the text',
                'here is the corrected', 'corrected version', 'grammar correction',
                'spanish translation', 'translate to spanish'
            ]):
                continue
                
            # Eliminar líneas que son solo instrucciones
            if re.match(r'^\s*(task|instruction|note)\s*:', line, re.IGNORECASE):
                continue
                
            clean_lines.append(line)
        
        corrected = ' '.join(clean_lines).strip()
        
        # FILTRO ADICIONAL: Eliminar acrónimos y texto extraño al final
        # Patrón para detectar secuencias de acrónimos/códigos al final
        corrected = re.sub(r'\s+[A-Z]{2,}(\s+[A-Z]{2,})*\s*$', '', corrected)
        corrected = re.sub(r'\s+[A-Z]+\d+[A-Z]*\s*$', '', corrected)  # Ej: USB12LED
        corrected = re.sub(r'\s+\b[A-Z]{1,4}\b(\s+\b[A-Z]{1,4}\b){2,}\s*$', '', corrected)  # Ej: TMY CUCD USB LED O
        
        # Si la corrección está vacía después de la limpieza, devolver original
        if not corrected.strip():
            return original
            
        # Eliminar comillas extras
        corrected = corrected.strip('"').strip("'").strip()
        
        # Si la corrección es muy diferente en longitud, preferir original
        if len(corrected) < len(original) * 0.3 or len(corrected) > len(original) * 3:
            logger.warning(f"Corrección sospechosa descartada: '{corrected[:50]}...'")
            return original
            
        return corrected
    
    def _post_process_correction(self, text: str) -> str:
        """Post-procesa específicamente para correcciones gramaticales."""
        if not text:
            return text
            
        # Eliminar múltiples tipos de prompts y artefactos
        cleanup_patterns = [
            r'^\s*(corregir|correct|corrección|grammar|gramática)\s*:?\s*',
            r'^\s*(fix|repair|improve)\s*:?\s*',
            r'^\s*(spanish|español)\s*:?\s*',
            r'^\s*(text|texto)\s*:?\s*',
            r'^\s*(here is|aquí está|this is)\s*:?\s*',
            r'^\s*(corrected|corregido)\s*:?\s*',
            r'\s*\[.*?\]\s*',  # Eliminar contenido entre corchetes
            r'\s*\(.*?correction.*?\)\s*',  # Eliminar notas sobre corrección
        ]
        
        for pattern in cleanup_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Eliminar frases comunes en inglés que aparecen al inicio
        english_starters = [
            r'^\s*(the corrected text is|corrected version|fixed text):\s*',
            r'^\s*(here\'s the corrected|this is the corrected)\s*',
            r'^\s*(grammar corrected|text corrected):\s*'
        ]
        
        for pattern in english_starters:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Eliminar texto extraño al final
        text = re.sub(r'\s*(end|fin|done|completed)\s*$', '', text, flags=re.IGNORECASE)
        
        # Capitalizar primera letra
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return text
