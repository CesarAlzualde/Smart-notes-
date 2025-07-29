#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para generar resúmenes de texto utilizando el modelo T5 de Google
a través de la biblioteca Transformers de Hugging Face.
"""

import logging
import os
import time
from typing import Optional, Union, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from transformers import AutoTokenizer, TFAutoModelForSeq2SeqLM, pipeline
    import numpy as np
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de instalar: pip install tensorflow transformers")
    raise

# Configurar para usar memoria GPU de forma dinámica (si está disponible)
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logger.info(f"GPU detectada: {gpus}")
    except RuntimeError as e:
        logger.warning(f"Error al configurar GPU: {e}")
else:
    logger.info("No se detectó GPU. Usando CPU.")

class TextSummarizer:
    """
    Clase para generar resúmenes de texto utilizando el modelo T5.
    """
    
    def __init__(self, model_name: str = "google/mt5-small", 
                 max_input_length: int = 512, 
                 max_output_length: int = 150,
                 device: int = -1):
        """
        Inicializa el modelo de resumen de texto.
        
        Args:
            model_name: Nombre del modelo a utilizar (por defecto: google/mt5-small)
            max_input_length: Longitud máxima del texto de entrada en tokens
            max_output_length: Longitud máxima del resumen generado en tokens
            device: Dispositivo a utilizar (-1 para CPU, 0+ para GPU específica)
        """
        self.model_name = model_name
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.device = device
        
        logger.info(f"Cargando modelo {model_name}...")
        start_time = time.time()
        
        # Cargar tokenizer y modelo
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Crear pipeline de resumen
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            framework="tf",
            device=device
        )
        
        load_time = time.time() - start_time
        logger.info(f"Modelo cargado en {load_time:.2f} segundos")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesa el texto añadiendo el prefijo 'resumir: '.
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            Texto preprocesado
        """
        # Añadir prefijo para T5
        return f"resumir: {text}"
    
    def generate_summary(self, text: str, num_beams: int = 5) -> str:
        """
        Genera un resumen del texto proporcionado.
        
        Args:
            text: Texto a resumir
            num_beams: Número de beams para la búsqueda de beam (mejora la calidad)
            
        Returns:
            Resumen generado
        """
        # Preprocesar texto
        preprocessed_text = self.preprocess_text(text)
        
        # Tokenizar para verificar la longitud
        tokens = self.tokenizer.encode(preprocessed_text)
        if len(tokens) > self.max_input_length:
            logger.warning(f"El texto tiene {len(tokens)} tokens, se truncará a {self.max_input_length}")
            # Truncar texto si es demasiado largo
            tokens = tokens[:self.max_input_length]
            preprocessed_text = self.tokenizer.decode(tokens)
        
        # Generar resumen
        try:
            summary = self.summarizer(
                preprocessed_text,
                max_length=self.max_output_length,
                min_length=30,  # Longitud mínima para evitar resúmenes demasiado cortos
                num_beams=num_beams,
                early_stopping=True
            )
            
            # Extraer el texto del resumen
            summary_text = summary[0]['summary_text']
            return summary_text
            
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return ""

# Función de conveniencia para uso directo
def generate_summary(text: str, model_name: str = "google/mt5-small", num_beams: int = 5) -> str:
    """
    Función de conveniencia para generar un resumen sin necesidad de instanciar la clase.
    
    Args:
        text: Texto a resumir
        model_name: Nombre del modelo a utilizar
        num_beams: Número de beams para la búsqueda de beam
        
    Returns:
        Resumen generado
    """
    summarizer = TextSummarizer(model_name=model_name)
    return summarizer.generate_summary(text, num_beams=num_beams)

# Ejemplo de uso
if __name__ == "__main__":
    # Texto de ejemplo sobre cambio climático
    texto_ejemplo = """
    El cambio climático es la variación global del clima de la Tierra. Esta variación se debe a causas naturales y a la acción del hombre y se produce sobre todos los parámetros climáticos: temperatura, precipitaciones, nubosidad, etc., a muy diversas escalas de tiempo.

    El término "efecto invernadero" se refiere a la retención del calor del Sol en la atmósfera de la Tierra por parte de una capa de gases en la atmósfera. Sin ellos la vida tal como la conocemos no sería posible, ya que el planeta sería demasiado frío. Entre estos gases se encuentran el dióxido de carbono, el óxido nitroso y el metano, que son liberados por la industria, la agricultura y la combustión de combustibles fósiles.

    El mundo industrializado ha conseguido que la concentración de estos gases haya aumentado un 30% desde el siglo pasado, cuando, sin la actuación humana, la naturaleza se encargaba de equilibrar las emisiones. El cambio climático nos afecta a todos. El impacto potencial es enorme, con predicciones de falta de agua potable, grandes cambios en las condiciones para la producción de alimentos y un aumento en los índices de mortalidad debido a inundaciones, tormentas, sequías y olas de calor.

    En definitiva, el cambio climático no es un fenómeno sólo ambiental sino de profundas consecuencias económicas y sociales. Los países más pobres, que están peor preparados para enfrentar cambios rápidos, serán los que sufrirán las peores consecuencias.
    """
    
    print("Generando resumen...")
    resumen = generate_summary(texto_ejemplo)
    print("\nTexto original:")
    print(texto_ejemplo[:200] + "...")
    print("\nResumen generado:")
    print(resumen)
