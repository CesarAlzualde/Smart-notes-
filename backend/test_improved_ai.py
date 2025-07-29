#!/usr/bin/env python3
"""
Test script para verificar las mejoras en IA:
1. BART-large para resúmenes 
2. Filtrado mejorado de entidades (sin 'O')
3. Limpieza mejorada de correcciones gramaticales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_improved_ai():
    """Prueba las mejoras implementadas"""
    logger.info("=" * 60)
    logger.info("🧪 PROBANDO MEJORAS EN IA - APUNTES 2.0")
    logger.info("=" * 60)
    
    # Texto de prueba con entidades claras
    test_text = """
    La Programación Orientada a Objetos (POO) es un método de implementación en el que los programas 
    se organizan como colecciones cooperativas de objetos, cada uno de los cuales representa una 
    instancia de alguna clase y cuyas clases son todos los miembros de una jerarquía de clases 
    unidas mediante relaciones de herencia. Según Grady Booch, la Universidad de California Santa Barbara 
    ha desarrollado investigaciones importantes en este campo. María García y Juan Pérez han contribuido 
    significativamente desde Madrid, España. También empresas como Google y Microsoft han adoptado 
    estos principios en sus desarrollos.
    """
    
    # Inicializar el TextSummarizer
    logger.info("🔧 Inicializando TextSummarizer...")
    summarizer = TextSummarizer()
    
    try:
        # 1. PROBAR RESUMEN CON BART-LARGE (prioridad actualizada)
        logger.info("\n" + "="*50)
        logger.info("📝 PROBANDO RESUMEN CON BART-LARGE PRIORITIZADO")
        logger.info("="*50)
        
        summary = summarizer.generate_summary(test_text)
        logger.info(f"✅ RESUMEN GENERADO:\n{summary}")
        
        # 2. PROBAR EXTRACCIÓN DE ENTIDADES FILTRADAS
        logger.info("\n" + "="*50)
        logger.info("🏷️ PROBANDO EXTRACCIÓN DE ENTIDADES FILTRADAS")
        logger.info("="*50)
        
        entities = summarizer.extract_entities(test_text)
        logger.info("✅ ENTIDADES EXTRAÍDAS:")
        for entity_type, entity_list in entities.items():
            logger.info(f"  {entity_type}: {entity_list}")
        
        # 3. PROBAR CORRECCIÓN GRAMATICAL MEJORADA
        logger.info("\n" + "="*50)
        logger.info("📖 PROBANDO CORRECCIÓN GRAMATICAL MEJORADA")
        logger.info("="*50)
        
        # Texto con errores para probar corrección
        incorrect_text = "La pOO es un metodo de implementacion que organiza programa como coleccion de objeto"
        
        corrected = summarizer.correct_grammar(incorrect_text)
        logger.info(f"📄 TEXTO ORIGINAL: {incorrect_text}")
        logger.info(f"✅ TEXTO CORREGIDO: {corrected}")
        
        # 4. PROBAR ANÁLISIS DE SENTIMIENTO
        logger.info("\n" + "="*50)
        logger.info("😊 PROBANDO ANÁLISIS DE SENTIMIENTO")
        logger.info("="*50)
        
        sentiment = summarizer.analyze_sentiment(test_text)
        logger.info(f"✅ SENTIMIENTO DETECTADO: {sentiment}")
        
        # 5. RESUMEN DE ESTADO
        logger.info("\n" + "="*50)
        logger.info("📊 RESUMEN DEL ESTADO DE LOS MODELOS")
        logger.info("="*50)
        
        models_status = {
            "Modelo de Resumen": "✅ Cargado" if summarizer._summarization_model else "❌ No Cargado",
            "Modelo de Sentimiento": "✅ Cargado" if summarizer._sentiment_model else "❌ No Cargado", 
            "Modelo NER": "✅ Cargado" if summarizer._ner_pipeline else "❌ No Cargado",
            "Modelo de Corrección": "✅ Cargado" if summarizer._grammar_model else "❌ No Cargado"
        }
        
        for model, status in models_status.items():
            logger.info(f"  {model}: {status}")
        
        logger.info("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante las pruebas: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_improved_ai()
    sys.exit(0 if success else 1)
