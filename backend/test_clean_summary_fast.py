#!/usr/bin/env python3
"""
Test script RÁPIDO para verificar la limpieza del resumen (sin cargar modelos pesados)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cleaning_only():
    """Prueba SOLO la funcionalidad de limpieza sin cargar modelos"""
    logger.info("=" * 60)
    logger.info("🧹 PRUEBA RÁPIDA DE LIMPIEZA - SIN MODELOS")
    logger.info("=" * 60)
    
    # Crear instancia SIN cargar modelos
    summarizer = TextSummarizer()
    
    # CASOS DE PRUEBA DE LIMPIEZA
    test_cases = [
        {
            "name": "Caso 1: Artefactos TMY CUCD",
            "dirty": "La POO es un método de implementación para organizar programas TMY CUCD USB LED O",
            "original": "texto original largo aquí..."
        },
        {
            "name": "Caso 2: Fechas extrañas",
            "dirty": "Este es un resumen sobre programación 17:02/1955 con información técnica",
            "original": "texto original..."
        },
        {
            "name": "Caso 3: Acrónimos al final",
            "dirty": "La programación orientada a objetos es fundamental CD DVD ET ING",
            "original": "texto original..."
        },
        {
            "name": "Caso 4: Múltiples problemas",
            "dirty": "POO es importante TMY CUCD USB LED O ET Ing Software Universidad 17:02/1955",
            "original": "texto original muy largo para contexto..."
        }
    ]
    
    logger.info("\n🧪 EJECUTANDO CASOS DE PRUEBA:")
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        logger.info(f"\n--- {case['name']} ---")
        logger.info(f"📝 ANTES: {case['dirty']}")
        
        cleaned = summarizer._clean_summary_text(case['dirty'], case['original'])
        
        logger.info(f"✨ DESPUÉS: {cleaned}")
        
        # Verificar que se eliminaron los artefactos
        artifacts = ["TMY", "CUCD", "USB LED O", "17:02/1955", " ET ING", " CD DVD"]
        found_artifacts = [artifact for artifact in artifacts if artifact in cleaned]
        
        if found_artifacts:
            logger.error(f"❌ FALLO: Todavía contiene: {found_artifacts}")
            all_passed = False
        else:
            logger.info("✅ ÉXITO: Limpieza correcta")
    
    # PRUEBA DE POST-PROCESSING EXISTENTE
    logger.info("\n" + "="*50)
    logger.info("🔄 PROBANDO POST_PROCESS_SUMMARY EXISTENTE")
    logger.info("="*50)
    
    messy_text = "La POO... es muy importante, muy importante. La POO es fundamental."
    processed = summarizer.post_process_summary(messy_text)
    logger.info(f"📝 ANTES: {messy_text}")
    logger.info(f"✨ DESPUÉS: {processed}")
    
    # RESULTADO FINAL
    logger.info("\n" + "="*50)
    logger.info("🎯 RESULTADO FINAL")
    logger.info("="*50)
    
    if all_passed:
        logger.info("🎉 ¡TODAS LAS PRUEBAS DE LIMPIEZA EXITOSAS!")
        logger.info("✅ La funcionalidad de limpieza está funcionando correctamente")
        return True
    else:
        logger.error("❌ ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = test_cleaning_only()
    sys.exit(0 if success else 1)
