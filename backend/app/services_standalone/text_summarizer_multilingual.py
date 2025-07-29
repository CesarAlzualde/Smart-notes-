#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para generar resúmenes de texto utilizando el modelo mBART multilingüe.
Esta versión tiene mejor soporte para español e inglés.
"""

import logging
import time
import os
from typing import Optional, Union, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from transformers import MBartForConditionalGeneration, MBartTokenizer
    import torch
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de instalar: pip install transformers torch")
    raise

class MultilingualSummarizer:
    """
    Clase para generar resúmenes de texto utilizando el modelo mBART multilingüe.
    """
    
    def __init__(self, model_name: str = "facebook/mbart-large-50", 
                 max_input_length: int = 1024, 
                 max_output_length: int = 150,
                 cache_dir: Optional[str] = None):
        """
        Inicializa el modelo de resumen de texto multilingüe.
        
        Args:
            model_name: Nombre del modelo a utilizar (por defecto: facebook/mbart-large-50)
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
        self.tokenizer = MBartTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        
        # Mover a GPU si está disponible
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        
        load_time = time.time() - start_time
        logger.info(f"Modelo cargado en {load_time:.2f} segundos en {self.device}")
    
    def detect_language(self, text: str) -> str:
        """
        Detecta el idioma del texto para establecer el token correcto.
        Método simple basado en palabras comunes.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Código de idioma (es_XX, en_XX, etc.)
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
            return "es_XX"
        else:
            return "en_XX"
    
    def generate_summary(self, text: str, num_beams: int = 5, language: Optional[str] = None) -> str:
        """
        Genera un resumen del texto proporcionado.
        
        Args:
            text: Texto a resumir
            num_beams: Número de beams para la búsqueda de beam (mejora la calidad)
            language: Código de idioma (es_XX, en_XX). Si es None, se detecta automáticamente.
            
        Returns:
            Resumen generado
        """
        # Detectar idioma si no se proporciona
        if language is None:
            language = self.detect_language(text)
        
        # Establecer el token de idioma de origen
        self.tokenizer.src_lang = language
        
        # Tokenizar para verificar la longitud
        inputs = self.tokenizer(text, max_length=self.max_input_length, 
                               return_tensors="pt", truncation=True)
        
        # Mover a GPU si está disponible
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generar resumen
        try:
            # Establecer el token de idioma de destino (mismo que el origen para resumir)
            self.model.config.forced_bos_token_id = self.tokenizer.lang_code_to_id[language]
            
            summary_ids = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=self.max_output_length,
                min_length=30,
                num_beams=num_beams,
                early_stopping=True,
                length_penalty=2.0,  # Favorece resúmenes más largos
                no_repeat_ngram_size=3,  # Evita repeticiones
                encoder_no_repeat_ngram_size=3
            )
            
            # Decodificar el resumen
            summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary_text
            
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return ""

# Función de conveniencia para uso directo
def generate_summary(text: str, model_name: str = "facebook/mbart-large-50", 
                    num_beams: int = 5, language: Optional[str] = None) -> str:
    """
    Función de conveniencia para generar un resumen sin necesidad de instanciar la clase.
    
    Args:
        text: Texto a resumir
        model_name: Nombre del modelo a utilizar
        num_beams: Número de beams para la búsqueda de beam
        language: Código de idioma (es_XX, en_XX). Si es None, se detecta automáticamente.
        
    Returns:
        Resumen generado
    """
    # Crear directorio de caché en la carpeta del usuario
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    
    summarizer = MultilingualSummarizer(model_name=model_name, cache_dir=cache_dir)
    return summarizer.generate_summary(text, num_beams=num_beams, language=language)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear directorio de caché en la carpeta del usuario
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    
    # Instanciar el summarizer una sola vez para reutilizarlo
    summarizer = MultilingualSummarizer(cache_dir=cache_dir)
    
    # Texto de ejemplo en inglés
    texto_ingles = """
    Climate change is the global variation of the Earth's climate. This variation is due to natural causes and human action and occurs on all climate parameters: temperature, precipitation, cloudiness, etc., at very diverse time scales.

    The term "greenhouse effect" refers to the retention of the Sun's heat in the Earth's atmosphere by a layer of gases in the atmosphere. Without them, life as we know it would not be possible, as the planet would be too cold. These gases include carbon dioxide, nitrous oxide, and methane, which are released by industry, agriculture, and the burning of fossil fuels.

    The industrialized world has managed to increase the concentration of these gases by 30% since the last century, when, without human action, nature was responsible for balancing emissions. Climate change affects us all. The potential impact is enormous, with predictions of lack of drinking water, major changes in conditions for food production, and increased mortality rates due to floods, storms, droughts, and heat waves.

    In short, climate change is not just an environmental phenomenon but has profound economic and social consequences. The poorest countries, which are less prepared to face rapid changes, will be the ones to suffer the worst consequences.
    """
    
    print("Generando resumen en inglés...")
    resumen_ingles = summarizer.generate_summary(texto_ingles, language="en_XX")
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
    resumen_espanol = summarizer.generate_summary(texto_espanol, language="es_XX")
    print("\nTexto original en español (primeros 200 caracteres):")
    print(texto_espanol[:200] + "...")
    print("\nResumen generado en español:")
    print(resumen_espanol)
    
    # Ejemplo de detección automática de idioma
    print("\n\nEjemplo con detección automática de idioma:")
    texto_corto_espanol = "El cambio climático es uno de los mayores desafíos de nuestro tiempo y sus efectos adversos socavan la capacidad de todos los países para alcanzar el desarrollo sostenible."
    idioma_detectado = summarizer.detect_language(texto_corto_espanol)
    print(f"Idioma detectado: {idioma_detectado}")
    resumen_auto = summarizer.generate_summary(texto_corto_espanol)  # Detección automática
    print("\nTexto original:")
    print(texto_corto_espanol)
    print("\nResumen generado con detección automática:")
    print(resumen_auto)
