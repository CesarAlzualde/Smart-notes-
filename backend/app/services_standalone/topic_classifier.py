#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para clasificación automática de temas mediante embeddings vectoriales.
Utiliza Sentence-BERT para generar representaciones vectoriales de textos y
compararlos con temas predefinidos mediante similitud de coseno.
"""

import os
import time
import json
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de instalar: pip install sentence-transformers")
    raise

class TopicClassifier:
    """
    Clasificador de temas basado en embeddings de Sentence-BERT.
    
    Esta clase permite:
    - Generar vectores de embeddings para textos
    - Clasificar textos en categorías temáticas predefinidas
    - Guardar y cargar embeddings para optimizar rendimiento
    - Entrenar con ejemplos personalizados
    - Evaluar precisión del clasificador
    """
    
    # Modelos preentrenados recomendados para español
    SPANISH_MODELS = {
        "default": "hiiamsid/sentence_similarity_spanish_es",
        "multilingual": "distiluse-base-multilingual-cased-v1",
        "paraphrase": "paraphrase-multilingual-mpnet-base-v2"
    }
    
    # Temas académicos predefinidos comunes (incluye categorías generales)
    DEFAULT_TOPICS = [
        # Categorías generales
        "Ciencia", "Tecnología", "Humanidades", "Ciencias Sociales", "Artes",
        # Temas específicos
        "Matemáticas", "Física", "Química", "Biología", 
        "Historia", "Geografía", "Literatura", "Filosofía",
        "Economía", "Derecho", "Informática", "Medicina",
        "Psicología", "Sociología", "Arte", "Música",
        "Ingeniería", "Arquitectura", "Estadística", "Lingüística"
    ]
    
    # Agrupaciones temáticas: mapea temas específicos a categorías generales
    TOPIC_GROUPS = {
        "Ciencia": ["Matemáticas", "Física", "Química", "Biología", "Estadística"],
        "Tecnología": ["Informática", "Ingeniería", "Arquitectura"],
        "Humanidades": ["Historia", "Literatura", "Filosofía", "Lingüística"],
        "Ciencias Sociales": ["Economía", "Derecho", "Psicología", "Sociología", "Geografía"],
        "Artes": ["Arte", "Música"]
    }
    
    # Mapeo inverso: de temas específicos a sus categorías generales
    TOPIC_TO_CATEGORY = {}
    
    def __init__(self, 
                model_name: Optional[str] = None,
                topics: Optional[List[str]] = None,
                embeddings_file: Optional[str] = None,
                cache_dir: Optional[str] = None,
                max_retries: int = 2):
        """
        Inicializa el clasificador de temas.
        
        Args:
            model_name: Nombre del modelo de Sentence-BERT a utilizar
            topics: Lista de temas para clasificación
            embeddings_file: Archivo .npz con embeddings precalculados
            cache_dir: Directorio de caché para los modelos
            max_retries: Número máximo de intentos al cargar modelos alternativos
        """
        # Inicializar estado interno
        self.model_name = None
        self.model = None
        self.model_loaded = False
        self.model_fallback_used = False
        self.error_message = None
        self.embedding_dimension = None
        self.topic_embeddings = None
        self.custom_examples = {}  # Ejemplos por tema para entrenamiento personalizado
        
        # Inicializar lista de temas
        self.topics = topics if topics is not None else self.DEFAULT_TOPICS
        logger.info(f"Configurando clasificador con {len(self.topics)} temas")
        
        # Inicializar mapeo inverso si no está inicializado
        if not self.TOPIC_TO_CATEGORY:
            for category, subtopics in self.TOPIC_GROUPS.items():
                for topic in subtopics:
                    self.TOPIC_TO_CATEGORY[topic] = category
            logger.info(f"Inicializado mapeo de {len(self.TOPIC_TO_CATEGORY)} temas a categorías generales")
        
        # Crear directorio de caché si no existe
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        self.cache_dir = cache_dir
            
        # Seleccionar modelo inicial
        self.model_name = model_name or self.SPANISH_MODELS["default"]
        logger.info(f"Intentando cargar modelo: {self.model_name}")
        
        # Intentar cargar el modelo con reintentos si falla
        self._load_model_with_fallbacks(max_retries)
            
        # Inicializar embeddings de temas si el modelo está disponible
        if self.model_loaded:
            # Intentar cargar embeddings desde archivo si se proporciona
            if embeddings_file and os.path.exists(embeddings_file):
                try:
                    self.load_embeddings(embeddings_file)
                    logger.info(f"Embeddings cargados desde {embeddings_file}")
                except Exception as e:
                    logger.warning(f"No se pudieron cargar embeddings desde {embeddings_file}: {e}")
                    self._generate_topic_embeddings()
            else:
                # Generar embeddings nuevos
                self._generate_topic_embeddings()
    
    def _load_model_with_fallbacks(self, max_retries: int) -> None:
        """
        Intenta cargar el modelo con reintentos usando modelos alternativos si falla.
        
        Args:
            max_retries: Número máximo de intentos con modelos alternativos
        """
        # Lista de modelos de respaldo a intentar si falla el principal
        fallback_models = list(self.SPANISH_MODELS.values())
        if self.model_name in fallback_models:
            fallback_models.remove(self.model_name)
        
        # Primer intento con el modelo principal
        if self._try_load_model(self.model_name):
            return
            
        # Si falla, intentar con modelos alternativos
        retries = 0
        while retries < max_retries and not self.model_loaded and fallback_models:
            fallback_model = fallback_models.pop(0)
            logger.warning(f"Intentando con modelo alternativo {fallback_model} (intento {retries+1}/{max_retries})")
            
            if self._try_load_model(fallback_model):
                self.model_name = fallback_model
                self.model_fallback_used = True
                logger.info(f"Modelo alternativo {fallback_model} cargado con éxito")
                return
                
            retries += 1
            
        if not self.model_loaded:
            logger.error("No se pudo cargar ningún modelo después de múltiples intentos")
            self.error_message = "Fallo al cargar todos los modelos disponibles"
    
    def _try_load_model(self, model_name: str) -> bool:
        """
        Intenta cargar un modelo específico y captura excepciones.
        
        Args:
            model_name: Nombre del modelo a cargar
            
        Returns:
            True si el modelo se cargó correctamente, False en caso contrario
        """
        start_time = time.time()
        try:
            self.model = SentenceTransformer(model_name, cache_folder=self.cache_dir)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            load_time = time.time() - start_time
            
            logger.info(f"Modelo {model_name} cargado en {load_time:.2f} segundos")
            logger.info(f"Dimensión de embeddings: {self.embedding_dimension}")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo {model_name}: {e}")
            self.error_message = str(e)
            return False
        
        # Cargar embeddings si se proporciona un archivo
        if embeddings_file and os.path.exists(embeddings_file):
            self.load_embeddings(embeddings_file)
        else:
            # Generar embeddings de temas básicos
            self._generate_topic_embeddings()
    
    def _generate_topic_embeddings(self):
        """Genera embeddings para los temas definidos."""
        if not self.model_loaded:
            logger.error("No se pueden generar embeddings: modelo no disponible")
            raise RuntimeError("Modelo no disponible para generar embeddings")
            
        logger.info(f"Generando embeddings para {len(self.topics)} temas")
        start_time = time.time()
        
        try:
            # Generar embeddings para cada tema
            self.topic_embeddings = self.model.encode(self.topics, show_progress_bar=False)
            
            generation_time = time.time() - start_time
            logger.info(f"Embeddings generados en {generation_time:.2f} segundos")
            logger.info(f"Forma de la matriz de embeddings: {self.topic_embeddings.shape}")
            
            # Guardar embeddings en caché si hay directorio de caché
            if self.cache_dir:
                cache_path = os.path.join(self.cache_dir, f"topic_embeddings_{self.model_name.replace('/', '_')}.npz")
                try:
                    self.save_embeddings(cache_path)
                    logger.info(f"Embeddings guardados en caché: {cache_path}")
                except Exception as e:
                    logger.warning(f"No se pudieron guardar embeddings en caché: {e}")
                    
        except Exception as e:
            logger.error(f"Error al generar embeddings: {e}")
            raise
    
    def add_custom_examples(self, examples: Dict[str, List[str]]) -> None:
        """
        Añade ejemplos personalizados para mejorar la clasificación de temas.
        
        Args:
            examples: Diccionario con temas como claves y listas de ejemplos como valores
        """
        # Verificar si hay temas no reconocidos
        unknown_topics = [topic for topic in examples.keys() if topic not in self.topics]
        if unknown_topics:
            logger.warning(f"Temas no reconocidos: {unknown_topics}")
            logger.warning("Estos temas serán añadidos a la lista de temas")
            self.topics.extend(unknown_topics)
        
        # Añadir o actualizar ejemplos
        for topic, texts in examples.items():
            if topic in self.custom_examples:
                self.custom_examples[topic].extend(texts)
                logger.info(f"Añadidos {len(texts)} ejemplos adicionales para '{topic}'")
            else:
                self.custom_examples[topic] = texts
                logger.info(f"Añadidos {len(texts)} ejemplos para nuevo tema '{topic}'")
        
        # Regenerar embeddings
        self._update_embeddings_with_examples()
    
    def _update_embeddings_with_examples(self) -> None:
        """Actualiza embeddings de temas usando ejemplos personalizados."""
        if not self.custom_examples:
            logger.info("No hay ejemplos personalizados para actualizar embeddings")
            self._generate_topic_embeddings()
            return
            
        logger.info("Actualizando embeddings con ejemplos personalizados")
        
        # Calcular embedding promedio para cada tema
        topic_vectors = []
        
        for topic in self.topics:
            # Si hay ejemplos personalizados, usarlos
            if topic in self.custom_examples and self.custom_examples[topic]:
                examples = self.custom_examples[topic]
                logger.info(f"Usando {len(examples)} ejemplos para '{topic}'")
                
                # Calcular embeddings de todos los ejemplos
                example_embeddings = self.model.encode(examples)
                
                # Promediar embeddings
                topic_vector = np.mean(example_embeddings, axis=0)
                topic_vectors.append(topic_vector)
            else:
                # Si no hay ejemplos, usar el nombre del tema
                logger.info(f"Usando solo el nombre para '{topic}'")
                topic_vector = self.model.encode([topic])[0]
                topic_vectors.append(topic_vector)
        
        # Actualizar embeddings
        self.topic_embeddings = np.array(topic_vectors)
        logger.info(f"Embeddings actualizados, nueva forma: {self.topic_embeddings.shape}")
    
    def save_embeddings(self, file_path: str) -> None:
        """
        Guarda los embeddings actuales en un archivo .npz.
        
        Args:
            file_path: Ruta donde guardar el archivo
        """
        if self.topic_embeddings is None:
            logger.error("No hay embeddings para guardar")
            return
            
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        try:
            # Guardar embeddings y metadatos
            np.savez_compressed(
                file_path,
                embeddings=self.topic_embeddings,
                topics=np.array(self.topics, dtype=object)
            )
            
            # Guardar ejemplos personalizados en un archivo JSON separado
            if self.custom_examples:
                examples_file = f"{os.path.splitext(file_path)[0]}_examples.json"
                with open(examples_file, 'w', encoding='utf-8') as f:
                    json.dump(self.custom_examples, f, ensure_ascii=False, indent=2)
                logger.info(f"Ejemplos personalizados guardados en {examples_file}")
            
            logger.info(f"Embeddings guardados en {file_path}")
        except Exception as e:
            logger.error(f"Error al guardar embeddings: {e}")
            raise
    
    def load_embeddings(self, file_path: str) -> None:
        """
        Carga embeddings desde un archivo .npz.
        
        Args:
            file_path: Ruta del archivo a cargar
        """
        try:
            start_time = time.time()
            
            # Cargar embeddings y metadatos
            data = np.load(file_path, allow_pickle=True)
            self.topic_embeddings = data['embeddings']
            self.topics = data['topics'].tolist()
            
            load_time = time.time() - start_time
            logger.info(f"Embeddings cargados en {load_time:.2f} segundos")
            logger.info(f"Temas cargados: {len(self.topics)}")
            
            # Intentar cargar ejemplos personalizados si existen
            examples_file = f"{os.path.splitext(file_path)[0]}_examples.json"
            if os.path.exists(examples_file):
                with open(examples_file, 'r', encoding='utf-8') as f:
                    self.custom_examples = json.load(f)
                logger.info(f"Ejemplos personalizados cargados: {sum(len(examples) for examples in self.custom_examples.values())} en total")
            
        except Exception as e:
            logger.error(f"Error al cargar embeddings: {e}")
            self._generate_topic_embeddings()  # Generar embeddings básicos como respaldo
    
    def classify_text(self, text: str, top_n: int = 1, include_categories: bool = True) -> List[Tuple[str, float]]:
        """
        Clasifica un texto según los temas disponibles.
        
        Args:
            text: Texto a clasificar
            top_n: Número de temas a devolver (ordenados por similitud)
            include_categories: Si es True, incluye categorías generales relacionadas con los temas detectados
            
        Returns:
            Lista de tuplas (tema, puntuación) ordenadas por similitud
        """
        if not self.model_loaded or self.topic_embeddings is None:
            logger.error("El modelo o los embeddings de temas no están cargados")
            return [("Error", 0.0)]
        
        try:
            # Preprocesar texto
            if not text or len(text.strip()) == 0:
                logger.warning("Texto vacío proporcionado para clasificación")
                return [("Desconocido", 0.0)]
            
            # Generar embedding del texto
            start_time = time.time()
            text_embedding = self.model.encode([text], show_progress_bar=False)
            
            # Calcular similitud con cada tema
            similarities = cosine_similarity(text_embedding, self.topic_embeddings)[0]
            
            # Obtener los top_n temas más similares
            top_indices = similarities.argsort()[-top_n:][::-1]
            pairs = list(zip(self.topics, similarities))
            sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
            
            # Tomar los top_n resultados
            top_results = sorted_pairs[:top_n]
            
            # Registrar tiempo y resultados
            process_time = time.time() - start_time
            logger.debug(f"Clasificación completada en {process_time:.3f} segundos")
            logger.debug(f"Tema principal: {top_results[0][0]} (score: {top_results[0][1]:.3f})")
            
            return top_results
            
        except Exception as e:
            logger.error(f"Error durante la clasificación: {e}")
            # Intento de auto-reparación: regenerar embeddings
            try:
                logger.info("Intentando auto-reparación: regenerando embeddings...")
                self._generate_topic_embeddings()
                # Segundo intento de clasificación
                text_embedding = self.model.encode([text], show_progress_bar=False)[0]
                text_embedding = text_embedding.reshape(1, -1)
                similarities = cosine_similarity(text_embedding, self.topic_embeddings)[0]
                pairs = list(zip(self.topics, similarities))
                sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
                return sorted_pairs[:top_n]
            except Exception as e2:
                logger.error(f"Auto-reparación fallida: {e2}")
                return [("Error", 0.0)]
    
    def batch_classify(self, texts: List[str], top_n: int = 1) -> List[List[Tuple[str, float]]]:
        """
        Clasifica múltiples textos en lote.
        
        Args:
            texts: Lista de textos a clasificar
            top_n: Número de temas a devolver por texto
            
        Returns:
            Lista de resultados de clasificación para cada texto
        """
        # Verificar si el modelo está cargado
        if not self.model_loaded:
            logger.error("No se puede clasificar por lotes: modelo no disponible")
            return [[('Error', 0.0)]] * len(texts) if texts else []
        
        # Generar embeddings de temas si no existen
        if self.topic_embeddings is None:
            try:
                self._generate_topic_embeddings()
            except Exception as e:
                logger.error(f"Error al generar embeddings de temas: {e}")
                return [[('Error', 0.0)]] * len(texts) if texts else []
            
        # Validar entrada
        if not texts:
            logger.warning("Lista de textos vacía para clasificación por lotes")
            return []
            
        # Eliminar textos vacíos y registrar advertencia
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if len(valid_texts) < len(texts):
            logger.warning(f"Se omitieron {len(texts) - len(valid_texts)} textos vacíos")
            
        if not valid_texts:
            return [[("General", 0.0)]] * len(texts)
            
        try:
            # Generar embeddings para todos los textos válidos
            start_time = time.time()
            text_embeddings = self.model.encode(valid_texts, show_progress_bar=False)
            
            # Clasificar cada texto
            results = []
            for i, text_embedding in enumerate(text_embeddings):
                # Reshape para compatibilidad con cosine_similarity
                text_embedding = text_embedding.reshape(1, -1)
                
                # Calcular similitud con cada tema
                similarities = cosine_similarity(text_embedding, self.topic_embeddings)[0]
                
                # Ordenar resultados por similitud
                pairs = list(zip(self.topics, similarities))
                sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
                
                # Tomar los top_n resultados
                results.append(sorted_pairs[:top_n])
            
            # Registrar tiempo
            process_time = time.time() - start_time
            logger.info(f"Clasificación por lotes de {len(valid_texts)} textos completada en {process_time:.3f} segundos")
            
            return results
            
        except Exception as e:
            logger.error(f"Error durante la clasificación por lotes: {e}")
            # Intento de auto-reparación
            try:
                logger.info("Intentando auto-reparación para clasificación por lotes...")
                self._generate_topic_embeddings()
                
                # Segundo intento
                batch_size = min(10, len(valid_texts))  # Reducir tamaño del lote si hay muchos textos
                results = []
                for i in range(0, len(valid_texts), batch_size):
                    batch = valid_texts[i:i+batch_size]
                    batch_embeddings = self.model.encode(batch, show_progress_bar=False)
                    
                    for embedding in batch_embeddings:
                        embedding = embedding.reshape(1, -1)
                        similarities = cosine_similarity(embedding, self.topic_embeddings)[0]
                        pairs = list(zip(self.topics, similarities))
                        sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
                        results.append(sorted_pairs[:top_n])
                        
                return results
            except Exception as e2:
                logger.error(f"Auto-reparación fallida para clasificación por lotes: {e2}")
                return [[('Error', 0.0)]] * len(valid_texts)
    
    def evaluate(self, texts: List[str], true_labels: List[str]) -> Dict[str, Any]:
        """
        Evalúa la precisión del clasificador con textos de prueba.
        
        Args:
            texts: Lista de textos para evaluar
            true_labels: Etiquetas reales de los textos
            
        Returns:
            Diccionario con métricas de evaluación
        """
        if len(texts) != len(true_labels):
            raise ValueError("El número de textos y etiquetas debe ser igual")
            
        # Clasificar todos los textos
        predictions = []
        for text in texts:
            top_topic = self.classify_text(text, top_n=1)[0]
            predictions.append(top_topic[0])
        
        # Calcular métricas
        accuracy = accuracy_score(true_labels, predictions)
        report = classification_report(true_labels, predictions, output_dict=True)
        conf_matrix = confusion_matrix(
            true_labels, predictions, 
            labels=sorted(set(true_labels).union(set(predictions)))
        )
        
        # Calcular ejemplos incorrectos
        incorrect_examples = []
        for text, true_label, pred_label in zip(texts, true_labels, predictions):
            if true_label != pred_label:
                incorrect_examples.append({
                    'text': text[:100] + ('...' if len(text) > 100 else ''),
                    'true_label': true_label,
                    'predicted': pred_label
                })
        
        logger.info(f"Evaluación completada. Precisión: {accuracy:.3f}")
        logger.info(f"Muestras evaluadas: {len(texts)}")
        logger.info(f"Ejemplos incorrectos: {len(incorrect_examples)}")
        
        return {
            'accuracy': accuracy,
            'report': report,
            'confusion_matrix': conf_matrix.tolist(),
            'incorrect_examples': incorrect_examples[:10],  # Limitar a 10 ejemplos
            'total_incorrect': len(incorrect_examples)
        }
    
    def add_topic(self, topic: str, examples: Optional[List[str]] = None) -> None:
        """
        Añade un nuevo tema al clasificador.
        
        Args:
            topic: Nombre del tema
            examples: Lista opcional de textos de ejemplo
        """
        if topic in self.topics:
            logger.warning(f"El tema '{topic}' ya existe")
            # Actualizar ejemplos si se proporcionan
            if examples:
                if topic in self.custom_examples:
                    self.custom_examples[topic].extend(examples)
                else:
                    self.custom_examples[topic] = examples
                logger.info(f"Añadidos {len(examples)} ejemplos para '{topic}'")
            return
        
        # Añadir nuevo tema
        self.topics.append(topic)
        logger.info(f"Añadido nuevo tema: '{topic}'")
        
        # Guardar ejemplos si se proporcionan
        if examples:
            self.custom_examples[topic] = examples
            logger.info(f"Añadidos {len(examples)} ejemplos para '{topic}'")
        
        # Actualizar embeddings
        self._update_embeddings_with_examples()
    
    def remove_topic(self, topic: str) -> bool:
        """
        Elimina un tema del clasificador.
        
        Args:
            topic: Nombre del tema a eliminar
            
        Returns:
            True si el tema fue eliminado, False si no existía
        """
        if topic not in self.topics:
            logger.warning(f"El tema '{topic}' no existe")
            return False
        
        # Obtener índice del tema
        topic_index = self.topics.index(topic)
        
        # Eliminar tema
        self.topics.pop(topic_index)
        logger.info(f"Eliminado tema: '{topic}'")
        
        # Eliminar ejemplos si existen
        if topic in self.custom_examples:
            del self.custom_examples[topic]
            logger.info(f"Eliminados ejemplos para '{topic}'")
        
        # Actualizar embeddings
        if self.topic_embeddings is not None:
            # Eliminar embedding correspondiente
            self.topic_embeddings = np.delete(self.topic_embeddings, topic_index, axis=0)
            logger.info(f"Embeddings actualizados, nueva forma: {self.topic_embeddings.shape}")
        
        return True
    
    def get_topics(self) -> List[str]:
        """
        Obtiene la lista de temas disponibles.
        
        Returns:
            Lista de temas
        """
        return self.topics.copy()
        
    def get_related_topics(self, topic: str) -> List[str]:
        """
        Obtiene temas relacionados con un tema dado.
        
        Args:
            topic: Tema para el que buscar relacionados
            
        Returns:
            Lista de temas relacionados incluyendo categorías y subtemas
        """
        related = []
        
        # Si es una categoría general, devolver sus subtemas
        if topic in self.TOPIC_GROUPS:
            related.extend(self.TOPIC_GROUPS[topic])
            
        # Si es un tema específico, devolver su categoría y otros temas de la misma categoría
        elif topic in self.TOPIC_TO_CATEGORY:
            category = self.TOPIC_TO_CATEGORY[topic]
            related.append(category)
            related.extend([t for t in self.TOPIC_GROUPS[category] if t != topic])
            
        return related

# Función de conveniencia para clasificación rápida
def classify_text(text: str, model_name: Optional[str] = None, top_n: int = 1, include_categories: bool = True, fallback_to_default: bool = True) -> Union[Tuple[str, float], List[Tuple[str, float]]]:
    """
    Función de conveniencia para clasificar un texto sin instanciar la clase.
    
    Args:
        text: Texto a clasificar
        model_name: Nombre opcional del modelo a utilizar
        top_n: Número de temas a devolver
        include_categories: Si es True, incluye categorías generales relacionadas
        fallback_to_default: Si es True, intenta con el modelo predeterminado en caso de error
        
    Returns:
        Si top_n=1, una tupla (tema principal, puntuación)
        Si top_n>1, lista de tuplas (tema, puntuación)
    """
    try:
        classifier = TopicClassifier(model_name=model_name)
        if not classifier.model_loaded:
            if fallback_to_default and model_name is not None:
                logger.warning(f"Modelo {model_name} falló, intentando con modelo predeterminado")
                classifier = TopicClassifier()  # Intenta con el predeterminado
                
        results = classifier.classify_text(text, top_n=top_n, include_categories=include_categories)
        return results[0] if top_n == 1 else results
    except Exception as e:
        logger.error(f"Error en función de conveniencia classify_text: {e}")
        return ("Error", 0.0) if top_n == 1 else [("Error", 0.0)]

# Ejemplo de uso
if __name__ == "__main__":
    # Crear directorio de caché
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "sentence_transformers")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Instanciar clasificador
    classifier = TopicClassifier(cache_dir=cache_dir)
    
    # Ejemplos de clasificación
    textos_ejemplo = [
        "La función exponencial y el cálculo de límites son conceptos fundamentales en el análisis matemático.",
        "El ADN contiene toda la información genética necesaria para el desarrollo y funcionamiento de los seres vivos.",
        "La Segunda Guerra Mundial fue un conflicto militar global que se desarrolló entre 1939 y 1945.",
        "Las células eucariotas se caracterizan por tener un núcleo definido donde se encuentra el material genético.",
        "El desarrollo de algoritmos eficientes es fundamental para resolver problemas computacionales complejos."
    ]
    
    print("\nClasificación de ejemplos:")
    for i, texto in enumerate(textos_ejemplo):
        tema, score = classifier.classify_text(texto)[0]
        print(f"{i+1}. Texto: {texto[:60]}...")
        print(f"   Tema: {tema} (Score: {score:.3f})\n")
    
    # Añadir ejemplos personalizados
    print("\nAñadiendo ejemplos personalizados...")
    ejemplos = {
        "Informática": [
            "Los lenguajes de programación permiten desarrollar software para diferentes plataformas.",
            "La inteligencia artificial está revolucionando numerosos campos de la tecnología moderna.",
            "El aprendizaje automático es una rama de la inteligencia artificial basada en algoritmos."
        ],
        "Biología": [
            "Las células son la unidad básica estructural y funcional de todos los seres vivos.",
            "La fotosíntesis es el proceso por el cual las plantas convierten la luz en energía.",
            "El sistema nervioso coordina las acciones mediante la transmisión de señales."
        ]
    }
    classifier.add_custom_examples(ejemplos)
    
    # Guardar embeddings (opcional)
    embeddings_file = "topic_embeddings.npz"
    print(f"\nGuardando embeddings en {embeddings_file}...")
    classifier.save_embeddings(embeddings_file)
    
    # Clasificar con ejemplos personalizados
    nuevo_texto = "Python es un lenguaje de programación interpretado de alto nivel con sintaxis clara y concisa."
    print("\nClasificando nuevo texto con ejemplos personalizados:")
    print(f"Texto: {nuevo_texto}")
    
    temas = classifier.classify_text(nuevo_texto, top_n=3)
    for tema, score in temas:
        print(f"Tema: {tema} (Score: {score:.3f})")
