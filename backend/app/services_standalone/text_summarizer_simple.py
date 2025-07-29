#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para generar resúmenes de texto utilizando modelos de Hugging Face.
Versión simplificada con menos dependencias.
"""

import logging
import time
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de instalar: pip install transformers")
    raise

class TextSummarizer:
    """
    Clase para generar resúmenes de texto utilizando el modelo T5.
    """
    
    def __init__(self, model_name: str = "t5-small", 
                 max_input_length: int = 512, 
                 max_output_length: int = 150):
        """
        Inicializa el modelo de resumen de texto.
        
        Args:
            model_name: Nombre del modelo a utilizar (por defecto: t5-small)
            max_input_length: Longitud máxima del texto de entrada en tokens
            max_output_length: Longitud máxima del resumen generado en tokens
        """
        self.model_name = model_name
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        
        logger.info(f"Cargando modelo {model_name}...")
        start_time = time.time()
        
        # Cargar tokenizer y modelo
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        load_time = time.time() - start_time
        logger.info(f"Modelo cargado en {load_time:.2f} segundos")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesa el texto añadiendo el prefijo 'summarize: ' para el modelo T5 en inglés.
        Para texto en español, usaremos el modelo en inglés y luego traduciremos el resultado.
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            Texto preprocesado
        """
        # T5 en inglés usa "summarize: " como prefijo
        return f"summarize: {text}"
    
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
        input_ids = self.tokenizer.encode(preprocessed_text, return_tensors="pt", 
                                         max_length=self.max_input_length, truncation=True)
        
        # Generar resumen
        try:
            summary_ids = self.model.generate(
                input_ids,
                max_length=self.max_output_length,
                min_length=30,
                num_beams=num_beams,
                early_stopping=True
            )
            
            # Decodificar el resumen
            summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary_text
            
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return ""

# Función de conveniencia para uso directo
def generate_summary(text: str, model_name: str = "t5-small", num_beams: int = 5) -> str:
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
    # Texto de ejemplo sobre cambio climático (en inglés para mejor compatibilidad con t5-small)
    texto_ejemplo = """
    Climate change is the global variation of the Earth's climate. This variation is due to natural causes and human action and occurs on all climate parameters: temperature, precipitation, cloudiness, etc., at very diverse time scales.

    The term "greenhouse effect" refers to the retention of the Sun's heat in the Earth's atmosphere by a layer of gases in the atmosphere. Without them, life as we know it would not be possible, as the planet would be too cold. These gases include carbon dioxide, nitrous oxide, and methane, which are released by industry, agriculture, and the burning of fossil fuels.

    The industrialized world has managed to increase the concentration of these gases by 30% since the last century, when, without human action, nature was responsible for balancing emissions. Climate change affects us all. The potential impact is enormous, with predictions of lack of drinking water, major changes in conditions for food production, and increased mortality rates due to floods, storms, droughts, and heat waves.

    In short, climate change is not just an environmental phenomenon but has profound economic and social consequences. The poorest countries, which are less prepared to face rapid changes, will be the ones to suffer the worst consequences.
    """
    
    print("Generando resumen...")
    resumen = generate_summary(texto_ejemplo)
    print("\nTexto original (primeros 200 caracteres):")
    print(texto_ejemplo[:200] + "...")
    print("\nResumen generado:")
    print(resumen)
    
    # Ejemplo con texto en español (nota: el modelo t5-small está entrenado principalmente en inglés)
    print("\n\nEjemplo con texto en español (resultados pueden ser limitados):")
    texto_espanol = """
    El cambio climático es la variación global del clima de la Tierra. Esta variación se debe a causas naturales y a la acción del hombre y se produce sobre todos los parámetros climáticos: temperatura, precipitaciones, nubosidad, etc., a muy diversas escalas de tiempo.
    """
    resumen_espanol = generate_summary(texto_espanol)
    print("\nTexto original en español:")
    print(texto_espanol)
    print("\nResumen generado (puede ser limitado debido al modelo en inglés):")
    print(resumen_espanol)
