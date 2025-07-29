"""
Servicio para análisis de texto: clasificación de tópicos y generación de embeddings semánticos.
"""

import logging
import torch
import spacy
from collections import Counter
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Manejo de importación opcional para sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("La librería 'sentence-transformers' no está instalada. La generación de embeddings no estará disponible.")
    logging.warning("Para habilitarla, ejecuta: pip install sentence-transformers")

class NlpAnalyser:
    """
    Analizador de NLP que combina dos funcionalidades:
    1. Clasificación de tópicos (Zero-Shot) con un modelo NLI.
    2. Generación de embeddings semánticos con un modelo Sentence-BERT.
    """
    
    def __init__(self, 
                 classifier_model='MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7',
                 embedding_model='paraphrase-multilingual-MiniLM-L12-v2'):
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logging.info(f"NlpAnalyser instanciado. Usará el dispositivo: {self.device}")

        # Configuración del clasificador
        self.classifier_model_name = classifier_model
        self.classifier = None
        self.candidate_labels = [
            # Tecnología y Computación
            'Tecnología', 'Programación y Desarrollo de Software', 'Inteligencia Artificial', 
            'Machine Learning', 'Ciencia de Datos', 'Ciberseguridad', 'Redes y Sistemas',
            'Desarrollo Web y Móvil', 'Bases de Datos', 'Computación en la Nube', 'Blockchain',
            
            # Ciencias
            'Ciencia', 'Física', 'Química', 'Biología', 'Astronomía', 'Geología', 
            'Ciencias Ambientales', 'Matemáticas', 'Estadística',
            
            # Negocios y Economía
            'Negocios', 'Finanzas', 'Economía', 'Marketing y Ventas', 'Emprendimiento', 
            'Gestión de Proyectos', 'Recursos Humanos', 'Contabilidad',
            
            # Humanidades y Ciencias Sociales
            'Historia', 'Filosofía', 'Psicología', 'Sociología', 'Antropología', 
            'Política y Gobierno', 'Derecho y Leyes', 'Geografía',
            
            # Arte y Cultura
            'Arte', 'Música', 'Cine y Televisión', 'Literatura', 'Teatro y Danza', 
            'Fotografía', 'Diseño Gráfico', 'Arquitectura',
            
            # Salud y Bienestar
            'Medicina', 'Salud Pública', 'Nutrición y Dietética', 'Fitness y Deporte', 
            'Salud Mental', 'Farmacología',
            
            # Educación y Desarrollo Personal
            'Educación', 'Aprendizaje de Idiomas', 'Desarrollo Personal', 'Productividad',
            
            # Otros
            'General', 'Viajes y Turismo', 'Gastronomía', 'Noticias y Actualidad'
        ]
        self._load_classifier_model()

        # Configuración del modelo de embeddings
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_embedding_model()

        # Configuración de spaCy para extracción de keywords
        self.nlp = None
        self._load_spacy_model()

    def _load_classifier_model(self):
        """Carga el modelo de clasificación de tópicos."""
        try:
            logging.info(f"Cargando el modelo de clasificación: {self.classifier_model_name}...")
            self.classifier = pipeline(
                'zero-shot-classification',
                model=self.classifier_model_name,
                device=self.device
            )
            logging.info("Modelo de clasificación cargado exitosamente.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de clasificación: {e}", exc_info=True)

    def _load_embedding_model(self):
        """Carga el modelo para generar embeddings semánticos."""
        try:
            logging.info(f"Cargando el modelo de embeddings: {self.embedding_model_name}...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name, device=self.device)
            logging.info("Modelo de embeddings cargado exitosamente.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de embeddings: {e}", exc_info=True)

    def classify_text(self, text: str, top_n: int = 3) -> list:
        """Clasifica un texto en tópicos predefinidos."""
        if not self.classifier or not text or text.isspace():
            return [("General", 1.0)]
        try:
            results = self.classifier(text, self.candidate_labels, multi_label=True)
            return [(label, round(score, 4)) for label, score in zip(results['labels'], results['scores'])][:top_n]
        except Exception as e:
            logging.error(f"Error durante la clasificación: {e}", exc_info=True)
            return [("Error de Clasificación", 1.0)]

    def generate_embedding(self, text: str) -> list:
        """Genera un embedding vectorial para un texto dado."""
        if not self.embedding_model or not text or text.isspace():
            return []
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            # Convertir numpy array a lista para ser JSON serializable
            if hasattr(embedding, 'tolist'):
                return embedding.tolist()
            return embedding
        except Exception as e:
            logging.error(f"Error durante la generación del embedding: {e}", exc_info=True)
            return []

    def _load_spacy_model(self):
        """Carga el modelo de spaCy para NLP."""
        try:
            logging.info("Cargando modelo de spaCy para extracción de palabras clave...")
            self.nlp = spacy.load('es_core_news_sm')
            logging.info("Modelo de spaCy cargado exitosamente.")
        except OSError:
            logging.error("El modelo de spaCy 'es_core_news_sm' no está descargado.")
            logging.info("Para descargarlo, ejecuta: python -m spacy download es_core_news_sm")
            self.nlp = None
        except Exception as e:
            logging.error(f"Error al cargar el modelo de spaCy: {e}", exc_info=True)
            self.nlp = None

    def extract_keywords(self, text: str, top_n: int = 15) -> list:
        """Extrae palabras clave de un texto usando spaCy."""
        if not self.nlp or not text or text.isspace():
            return []
        try:
            doc = self.nlp(text)
            keywords = [
                token.lemma_.lower()
                for token in doc
                if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and not token.is_stop and not token.is_punct and len(token.text) > 3
            ]
            # Contar la frecuencia y devolver los más comunes sin duplicados
            most_common = [word for word, freq in Counter(keywords).most_common(top_n)]
            return most_common
        except Exception as e:
            logging.error(f"Error durante la extracción de palabras clave: {e}", exc_info=True)
            return []
