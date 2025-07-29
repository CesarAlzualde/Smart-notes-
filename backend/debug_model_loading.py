#!/usr/bin/env python3
"""
Script de depuración para identificar exactamente dónde ocurre el error de lista vs string
en la carga de modelos de resumen.
"""

import os
import sys
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Asegurar que estamos en el directorio correcto
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def debug_model_loading():
    """Función principal de depuración"""
    logger.info("=" * 50)
    logger.info("INICIANDO DEBUG DE CARGA DE MODELOS")
    logger.info("=" * 50)
    
    try:
        # Importar después de configurar el path
        from app.services.text_summarizer import TextSummarizer
        
        # Crear instancia con logging detallado
        logger.info("Creando instancia de TextSummarizer...")
        summarizer = TextSummarizer()
        
        # Verificar el estado de los modelos
        logger.info(f"Estado del modelo: {summarizer.model_status.to_dict()}")
        logger.info(f"Modelos primary definidos: {summarizer.MODELS['primary']}")
        logger.info(f"Tipo de MODELS['primary']: {type(summarizer.MODELS['primary'])}")
        
        # Verificar cada modelo individual
        for i, model in enumerate(summarizer.MODELS['primary']):
            logger.info(f"Modelo {i}: '{model}' (tipo: {type(model)})")
        
        # Intentar generar un resumen simple
        logger.info("Intentando generar un resumen de prueba...")
        test_text = "Este es un texto de prueba para verificar que el sistema de resumen funciona correctamente. Contiene varias oraciones para poder generar un resumen coherente."
        
        result = summarizer.generate_summary(test_text, compression_ratio=0.3)
        logger.info(f"Resultado del resumen: {result}")
        
    except Exception as e:
        logger.error(f"Error durante la depuración: {e}", exc_info=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_model_loading()
