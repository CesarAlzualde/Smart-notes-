#!/usr/bin/env python3
"""
Script para probar la nueva configuración optimizada de resumen.
"""

import sys
import os
import logging

# --- Configuración de Logging a Archivo ---
log_file_path = os.path.join(os.path.dirname(__file__), 'test_v2.log')
# Configurar el logger para que escriba a un archivo, eliminando handlers anteriores
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file_path,
    filemode='w' # 'w' para sobrescribir el log en cada ejecución
)
logger = logging.getLogger(__name__)
# Añadir un handler para que también se muestre en consola por si acaso
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

logger.info("Logger configurado para escribir en archivo y consola.")

# --- Añadir el directorio del backend al path ---
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
logger.info(f"sys.path actualizado: {sys.path[0]}")

try:
    from app.services.text_summarizer import TextSummarizer
    logger.info("Importación de TextSummarizer exitosa.")
except ImportError as e:
    logger.error(f"Fallo al importar TextSummarizer: {e}")
    sys.exit(1)

def test_new_summarizer():
    """Prueba el resumidor con la nueva configuración."""
    
    # Texto de ejemplo (el mismo que falló antes)
    text = """
    Propuesta Técnica y Diseño (3 minutos)

    Tú: "Nuestra solución es una aplicación integral y multiplataforma. Permítanme explicarles su arquitectura.

    • ¿Cómo funciona para el usuario? El flujo es simple:

    1. El estudiante captura sus apuntes, ya sea tomando una foto o subiendo un PDF.

    2. Nuestra aplicación digitaliza el texto usando tecnología OCR.

    3. Aquí ocurre la magia: la Inteligencia Artificial procesa el contenido, identifica los temas y extrae las ideas más importantes.

    4. Finalmente, la aplicación genera automáticamente resúmenes y mapas conceptuales interactivos, organizando todo por materia.

    • ¿Qué tecnología usamos?

    1. En el Backend, utilizamos Python con el framework Flask para crear una API robusta. Para la base de datos, combinamos PostgreSQL para los datos de usuario y Neo4j, una base de datos de grafos, para modelar los mapas conceptuales y sus relaciones.

    2. Para la Inteligencia Artificial, integramos modelos de vanguardia: BART-large-cnn para generar resúmenes precisos y multilingües, y Sentence-BERT para el análisis semántico y la clasificación de temas. Para el reconocimiento de texto (OCR), usamos una combinación de Tesseract y la API de Google Vision para máxima precisión.

    3. Y en el Frontend, la interfaz que ve el usuario, usamos React para la versión web y de escritorio, y React Native para la aplicación móvil, garantizando una experiencia fluida en cualquier dispositivo.

    Este diseño nos permite crear un sistema potente, escalable y centrado en las necesidades del estudiante."
    """
    
    logger.info("🔥 PROBANDO NUEVA CONFIGURACIÓN OPTIMIZADA 🔥")
    logger.info("=" * 60)
    
    try:
        # Crear instancia del resumidor
        logger.info("Inicializando TextSummarizer...")
        summarizer = TextSummarizer()
        
        # Mostrar configuración cargada
        logger.info(f"📊 Parámetros de resumen: {summarizer.summarization_params}")
        logger.info(f"🤖 Modelos configurados: {summarizer.models_config.get('summarization_models', [])}")
        logger.info(f"📝 Modelo de corrección: {summarizer.models_config.get('grammar_correction_model', 'N/A')}")
        
        # Verificar modelo cargado
        if hasattr(summarizer, 'model_name') and summarizer.model_name:
            logger.info(f"✅ Modelo activo: {summarizer.model_name}")
        else:
            logger.warning("⚠️ No hay modelo activo cargado")
            
        # Generar resumen
        logger.info("\n🚀 GENERANDO RESUMEN...")
        logger.info("-" * 40)
        
        result = summarizer.generate_summary(text, compression_ratio=0.25)
        
        if result.get("error"):
            logger.error(f"❌ ERROR: {result['error']}")
            return False
            
        summary = result.get("summary", "")
        duration = result.get("duration", 0)
        model_used = result.get("model_name", "Unknown")
        
        logger.info(f"⏱️ Tiempo de generación: {duration:.2f}s")
        logger.info(f"🤖 Modelo usado: {model_used}")
        logger.info(f"📊 Longitud del texto original: {len(text)} caracteres")
        logger.info(f"📊 Longitud del resumen: {len(summary)} caracteres")
        logger.info(f"📊 Ratio de compresión: {len(summary)/len(text):.2%}")
        
        # Evaluar calidad
        quality = summarizer.evaluate_summary_quality(summary)
        logger.info(f"🎯 Calidad evaluada: {quality:.2f}/1.0")
        
        logger.info("\n📝 RESUMEN GENERADO:")
        logger.info("=" * 50)
        logger.info(f"'{summary}'")
        logger.info("=" * 50)
        
        # Verificar si el resumen es aceptable
        if len(summary) > 100 and quality >= 0.7 and not any(token in summary for token in ['<extra_id', '<pad>', '<unk>']):
            logger.info("🎉 ¡RESUMEN EXITOSO! La nueva configuración funciona correctamente.")
            return True
        else:
            logger.warning("⚠️ El resumen aún necesita mejoras.")
            return False
            
    except Exception as e:
        logger.error(f"💥 Error durante la prueba: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_new_summarizer()
    if success:
        print("\n✅ CONFIGURACIÓN OPTIMIZADA FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n❌ LA CONFIGURACIÓN NECESITA MÁS AJUSTES")
