#!/usr/bin/env python3
"""
Test script para verificar la limpieza del resumen y las mejoras en sentimiento
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_summary_cleaning():
    """Prueba la limpieza del resumen con el mismo texto del usuario"""
    logger.info("=" * 60)
    logger.info("🧹 PRUEBA DE LIMPIEZA DE RESUMEN - APUNTES 2.0")
    logger.info("=" * 60)
    
    # El mismo texto que generó el problema
    problematic_text = """
    La POO es "Un método de implementación en el que los programas se organizan como colecciones cooperativas de 
    objetos" Graby Booch. TMY CUCD USB LED O. ET Ing Software Universidad California Santa Barbara 17:02/1955 
    Intricado: juego Semántico de Abstracciones La POO es "UnMétodo de Implementación en which el programas son 
    organized as coleciones Cooperativas (POOs) texto origina ET Ing Software Universidad California Santa Barbara 
    17:02/1955 Intricado: juego Semántico de Abstracciones La POO es "Un método de implementación en el que los 
    programas se organizan como colecciones cooperativas de objetos cada uno de los cuales representa una instancias 
    de alguna clase y cuyas clases son todos los miembros de una jerarquía d clases unidades mediante relaciones de 
    herencia" Graby Booch. TMY CUCD USB LED O este resumen tiene ciertos errores gramaticale
    """
    
    # Inicializar el TextSummarizer
    logger.info("🔧 Inicializando TextSummarizer...")
    summarizer = TextSummarizer()
    
    try:
        # 1. PROBAR LIMPIEZA DIRECTA DEL MÉTODO
        logger.info("\n" + "="*50)
        logger.info("🧹 PROBANDO LIMPIEZA DIRECTA")
        logger.info("="*50)
        
        # Simular texto de resumen con artefactos
        dirty_summary = "La POO es un método de implementación para organizar programas TMY CUCD USB LED O ET"
        cleaned = summarizer._clean_summary_text(dirty_summary, problematic_text)
        logger.info(f"📝 TEXTO SUCIO: {dirty_summary}")
        logger.info(f"✨ TEXTO LIMPIO: {cleaned}")
        
        # 2. PROBAR GENERACIÓN DE RESUMEN COMPLETA
        logger.info("\n" + "="*50)
        logger.info("📝 PROBANDO RESUMEN COMPLETO CON LIMPIEZA")
        logger.info("="*50)
        
        summary_result = summarizer.generate_summary(problematic_text)
        logger.info(f"✅ RESUMEN GENERADO Y LIMPIO:")
        logger.info(f"📄 Contenido: {summary_result.get('summary', 'ERROR')}")
        logger.info(f"🔧 Modelo: {summary_result.get('model_name', 'DESCONOCIDO')}")
        
        # 3. PROBAR EXTRACCIÓN DE ENTIDADES (CON ETIQUETAS EN ESPAÑOL)
        logger.info("\n" + "="*50)
        logger.info("🏷️ PROBANDO ENTIDADES EN ESPAÑOL")
        logger.info("="*50)
        
        entities = summarizer.extract_entities(problematic_text)
        logger.info("✅ ENTIDADES EXTRAÍDAS:")
        for entity_type, entity_list in entities.items():
            logger.info(f"  📍 {entity_type}: {entity_list}")
        
        # 4. PROBAR ANÁLISIS DE SENTIMIENTO CON NUEVOS MODELOS
        logger.info("\n" + "="*50)
        logger.info("😊 PROBANDO ANÁLISIS DE SENTIMIENTO")
        logger.info("="*50)
        
        try:
            sentiment = summarizer.analyze_sentiment(problematic_text)
            logger.info(f"✅ SENTIMIENTO DETECTADO: {sentiment}")
        except Exception as e:
            logger.warning(f"⚠️ Análisis de sentimiento falló: {e}")
        
        # 5. VALIDACIÓN FINAL
        logger.info("\n" + "="*50)
        logger.info("🎯 VALIDACIÓN FINAL")
        logger.info("="*50)
        
        final_summary = summary_result.get('summary', '')
        
        # Verificar que no contenga artefactos
        artifacts_found = []
        if "TMY" in final_summary:
            artifacts_found.append("TMY")
        if "CUCD" in final_summary:
            artifacts_found.append("CUCD") 
        if "USB LED O" in final_summary:
            artifacts_found.append("USB LED O")
        if "17:02/1955" in final_summary:
            artifacts_found.append("fechas extrañas")
            
        if artifacts_found:
            logger.error(f"❌ FALLO: Todavía contiene artefactos: {artifacts_found}")
            return False
        else:
            logger.info("✅ ÉXITO: Resumen limpio sin artefactos")
            
        logger.info("\n🎉 ¡TODAS LAS PRUEBAS DE LIMPIEZA EXITOSAS!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante las pruebas: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_summary_cleaning()
    sys.exit(0 if success else 1)
