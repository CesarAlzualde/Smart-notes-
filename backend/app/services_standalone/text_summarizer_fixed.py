#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para generar resúmenes de texto utilizando modelos de Hugging Face.
Versión mejorada con correcciones para evitar repeticiones y mejorar la calidad.
"""

import logging
import time
import os
import re
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from transformers import BartForConditionalGeneration, BartTokenizer
    import torch
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de instalar: pip install transformers torch")
    raise

class TextSummarizer:
    """
    Clase para generar resúmenes de texto utilizando modelos preentrenados.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn", 
                 max_input_length: int = 1024, 
                 max_output_length: int = 150,
                 cache_dir: Optional[str] = None):
        """
        Inicializa el modelo de resumen de texto.
        
        Args:
            model_name: Nombre del modelo a utilizar (por defecto: facebook/bart-large-cnn)
            max_input_length: Longitud máxima del texto de entrada en tokens
            max_output_length: Longitud máxima del resumen generado en tokens
            cache_dir: Directorio para almacenar los modelos descargados
        """
        self.model_name = model_name
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        
        # Crear directorio de caché si no existe
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        logger.info(f"Cargando modelo {model_name}...")
        start_time = time.time()
        
        # Cargar tokenizer y modelo
        self.tokenizer = BartTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = BartForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        
        # Mover a GPU si está disponible
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        
        load_time = time.time() - start_time
        logger.info(f"Modelo cargado en {load_time:.2f} segundos en {self.device}")
    
    def detect_language(self, text: str) -> str:
        """
        Detecta el idioma del texto para aplicar post-procesamiento específico.
        Método simple basado en palabras comunes.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Código de idioma ('es' o 'en')
        """
        # Lista de palabras comunes en español
        spanish_words = ['el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'pero', 'porque', 
                        'que', 'como', 'cuando', 'donde', 'quien', 'cual', 'este', 'esta', 
                        'estos', 'estas', 'ese', 'esa', 'esos', 'esas']
        
        # Convertir texto a minúsculas y dividir en palabras
        words = text.lower().split()
        
        # Contar palabras en español
        spanish_count = sum(1 for word in words if word in spanish_words)
        
        # Si más del 5% de las palabras son españolas, asumimos que es español
        if spanish_count / max(len(words), 1) > 0.05:
            return "es"
        else:
            return "en"
    
    def post_process_summary(self, summary: str, language: str) -> str:
        """
        Aplica post-procesamiento al resumen para mejorar su calidad.
        
        Args:
            summary: Texto del resumen generado
            language: Idioma del texto ('es' o 'en')
            
        Returns:
            Resumen mejorado
        """
        # Eliminar repeticiones de palabras consecutivas (como "El El El")
        summary = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', summary)
        
        # Corregir espacios antes de signos de puntuación
        summary = re.sub(r'\s+([.,;:!?])', r'\1', summary)
        
        # Asegurar que la primera letra esté en mayúscula
        if summary and len(summary) > 0:
            summary = summary[0].upper() + summary[1:]
        
        # Asegurar que el resumen termine con un punto
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        return summary
    
    def generate_summary(self, text: str, num_beams: int = 4, repetition_penalty: float = 2.5) -> str:
        """
        Genera un resumen del texto proporcionado.
        
        Args:
            text: Texto a resumir
            num_beams: Número de beams para la búsqueda de beam (mejora la calidad)
            repetition_penalty: Penalización para evitar repeticiones
            
        Returns:
            Resumen generado
        """
        # Detectar idioma para post-procesamiento
        language = self.detect_language(text)
        
        # Tokenizar para verificar la longitud
        inputs = self.tokenizer([text], max_length=self.max_input_length, 
                               return_tensors="pt", truncation=True)
        
        # Mover a GPU si está disponible
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generar resumen
        try:
            summary_ids = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=self.max_output_length,
                min_length=30,
                num_beams=num_beams,
                early_stopping=True,
                length_penalty=1.0,  # Valor más bajo para evitar resúmenes demasiado largos
                no_repeat_ngram_size=3,  # Evita repeticiones de frases
                repetition_penalty=repetition_penalty,  # Penalizar repeticiones
                do_sample=False  # Desactivar muestreo para resultados más deterministas
            )
            
            # Decodificar el resumen
            summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Aplicar post-procesamiento
            summary_text = self.post_process_summary(summary_text, language)
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return ""

# Función de conveniencia para uso directo
def generate_summary(text: str, model_name: str = "facebook/bart-large-cnn", 
                    num_beams: int = 4, repetition_penalty: float = 2.5) -> str:
    """
    Función de conveniencia para generar un resumen sin necesidad de instanciar la clase.
    
    Args:
        text: Texto a resumir
        model_name: Nombre del modelo a utilizar
        num_beams: Número de beams para la búsqueda de beam
        repetition_penalty: Penalización para evitar repeticiones
        
    Returns:
        Resumen generado
    """
    # Crear directorio de caché en la carpeta del usuario
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    
    summarizer = TextSummarizer(model_name=model_name, cache_dir=cache_dir)
    return summarizer.generate_summary(text, num_beams=num_beams, repetition_penalty=repetition_penalty)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear directorio de caché en la carpeta del usuario
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    
    # Instanciar el summarizer una sola vez para reutilizarlo
    summarizer = TextSummarizer(cache_dir=cache_dir)
    
    # Texto de ejemplo en inglés
    texto_ingles = """
    Climate change is the global variation of the Earth's climate. This variation is due to natural causes and human action and occurs on all climate parameters: temperature, precipitation, cloudiness, etc., at very diverse time scales.

    The term "greenhouse effect" refers to the retention of the Sun's heat in the Earth's atmosphere by a layer of gases in the atmosphere. Without them, life as we know it would not be possible, as the planet would be too cold. These gases include carbon dioxide, nitrous oxide, and methane, which are released by industry, agriculture, and the burning of fossil fuels.

    The industrialized world has managed to increase the concentration of these gases by 30% since the last century, when, without human action, nature was responsible for balancing emissions. Climate change affects us all. The potential impact is enormous, with predictions of lack of drinking water, major changes in conditions for food production, and increased mortality rates due to floods, storms, droughts, and heat waves.

    In short, climate change is not just an environmental phenomenon but has profound economic and social consequences. The poorest countries, which are less prepared to face rapid changes, will be the ones to suffer the worst consequences.
    """
    
    print("Generando resumen en inglés...")
    resumen_ingles = summarizer.generate_summary(texto_ingles)
    print("\nTexto original en inglés (primeros 200 caracteres):")
    print(texto_ingles[:200] + "...")
    print("\nResumen generado en inglés:")
    print(resumen_ingles)
    
    # Texto de ejemplo en español
    texto_espanol = """
    El cambio climático es la variación global del clima de la Tierra. Esta variación se debe a causas naturales y a la acción del hombre y se produce sobre todos los parámetros climáticos: temperatura, precipitaciones, nubosidad, etc., a muy diversas escalas de tiempo.

    El término "efecto invernadero" se refiere a la retención del calor del Sol en la atmósfera de la Tierra por parte de una capa de gases en la atmósfera. Sin ellos la vida tal como la conocemos no sería posible, ya que el planeta sería demasiado frío. Entre estos gases se encuentran el dióxido de carbono, el óxido nitroso y el metano, que son liberados por la industria, la agricultura y la combustión de combustibles fósiles.

    El mundo industrializado ha conseguido que la concentración de estos gases haya aumentado un 30% desde el siglo pasado, cuando, sin la actuación humana, la naturaleza se encargaba de equilibrar las emisiones. El cambio climático nos afecta a todos. El impacto potencial es enorme, con predicciones de falta de agua potable, grandes cambios en las condiciones para la producción de alimentos y un aumento en los índices de mortalidad debido a inundaciones, tormentas, sequías y olas de calor.

    En definitiva, el cambio climático no es un fenómeno sólo ambiental sino de profundas consecuencias económicas y sociales. Los países más pobres, que están peor preparados para enfrentar cambios rápidos, serán los que sufrirán las peores consecuencias.
    """
    
    print("\n\nGenerando resumen en español...")
    resumen_espanol = summarizer.generate_summary(texto_espanol)
    print("\nTexto original en español (primeros 200 caracteres):")
    print(texto_espanol[:200] + "...")
    print("\nResumen generado en español:")
    print(resumen_espanol)
    
    # Ejemplo con texto corto
    print("\n\nEjemplo con texto corto en español:")
    texto_corto_espanol = "El cambio climático es uno de los mayores desafíos de nuestro tiempo y sus efectos adversos socavan la capacidad de todos los países para alcanzar el desarrollo sostenible."
    resumen_corto = summarizer.generate_summary(texto_corto_espanol)
    print("\nTexto original:")
    print(texto_corto_espanol)
    print("\nResumen generado:")
    print(resumen_corto)
