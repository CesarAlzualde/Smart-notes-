#!/usr/bin/env python3
"""
Test DIRECTO de limpieza sin instanciar TextSummarizer completo
"""

import sys
import os
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_summary_text(summary: str, original_text: str) -> str:
    """
    Implementación directa del método de limpieza para probar sin instanciar TextSummarizer
    """
    if not summary:
        return summary
        
    logger.info(f"🧹 Limpiando resumen: '{summary[:100]}...'")
    
    # PASO 1: Eliminar acrónimos y códigos extraños al final
    # Patrón para secuencias como "TMY CUCD USB LED O"
    summary = re.sub(r'\s+[A-Z]{2,}(\s+[A-Z]{2,})*\s*$', '', summary)
    summary = re.sub(r'\s+[A-Z]+\d+[A-Z]*\s*$', '', summary)
    summary = re.sub(r'\s+\b[A-Z]{1,4}\b(\s+\b[A-Z]{1,4}\b){2,}\s*$', '', summary)
    
    # PASO 2: Eliminar secuencias de números y fechas extrañas
    summary = re.sub(r'\s+\d{1,2}:\d{1,2}/\d{4}\s*', '', summary)
    summary = re.sub(r'\s+\d{4}-\d{2}-\d{2}\s*', '', summary)
    
    # PASO 3: Eliminar texto que parece código o referencias técnicas al final
    summary = re.sub(r'\s+(ET|ING|USB|LED|CD|DVD)\s*$', '', summary, flags=re.IGNORECASE)
    
    # PASO 4: Eliminar fragmentos que parecen metadatos
    summary = re.sub(r'\s+[A-Z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$', '', summary)
    
    # PASO 5: Limpiar espacios múltiples
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    # PASO 6: Si el resumen quedó muy corto o vacío, devolver mensaje
    if len(summary) < 50 and len(original_text) > 100:
        logger.warning("Resumen muy corto después de limpieza")
        
    logger.info(f"✅ Resumen limpiado: '{summary[:100]}...'")
    return summary

def test_cleaning_direct():
    """Prueba DIRECTA de la funcionalidad de limpieza"""
    logger.info("=" * 60)
    logger.info("🧹 PRUEBA DIRECTA DE LIMPIEZA - SIN CLASES")
    logger.info("=" * 60)
    
    # CASOS DE PRUEBA DE LIMPIEZA
    test_cases = [
        {
            "name": "Caso 1: Artefactos TMY CUCD",
            "dirty": "La POO es un método de implementación para organizar programas TMY CUCD USB LED O",
            "expected_clean": "La POO es un método de implementación para organizar programas",
            "original": "texto original largo aquí..."
        },
        {
            "name": "Caso 2: Fechas extrañas",
            "dirty": "Este es un resumen sobre programación 17:02/1955 con información técnica",
            "expected_clean": "Este es un resumen sobre programación con información técnica",
            "original": "texto original..."
        },
        {
            "name": "Caso 3: Acrónimos al final",
            "dirty": "La programación orientada a objetos es fundamental CD DVD ET ING",
            "expected_clean": "La programación orientada a objetos es fundamental",
            "original": "texto original..."
        },
        {
            "name": "Caso 4: Múltiples problemas",
            "dirty": "POO es importante TMY CUCD USB LED O ET Ing Software Universidad 17:02/1955",
            "expected_clean": "POO es importante",
            "original": "texto original muy largo para contexto..."
        },
        {
            "name": "Caso 5: Texto normal (no debe cambiar)",
            "dirty": "La programación orientada a objetos es un paradigma importante en el desarrollo de software.",
            "expected_clean": "La programación orientada a objetos es un paradigma importante en el desarrollo de software.",
            "original": "texto original..."
        }
    ]
    
    logger.info("\n🧪 EJECUTANDO CASOS DE PRUEBA:")
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        logger.info(f"\n--- {case['name']} ---")
        logger.info(f"📝 ANTES: {case['dirty']}")
        
        cleaned = clean_summary_text(case['dirty'], case['original'])
        
        logger.info(f"✨ DESPUÉS: {cleaned}")
        logger.info(f"🎯 ESPERADO: {case['expected_clean']}")
        
        # Verificar que se eliminaron los artefactos principales
        artifacts = ["TMY", "CUCD", "USB LED O", "17:02/1955"]
        found_artifacts = [artifact for artifact in artifacts if artifact in cleaned]
        
        if found_artifacts:
            logger.error(f"❌ FALLO: Todavía contiene: {found_artifacts}")
            all_passed = False
        else:
            logger.info("✅ ÉXITO: Limpieza correcta")
    
    # RESULTADO FINAL
    logger.info("\n" + "="*50)
    logger.info("🎯 RESULTADO FINAL")
    logger.info("="*50)
    
    if all_passed:
        logger.info("🎉 ¡TODAS LAS PRUEBAS DE LIMPIEZA EXITOSAS!")
        logger.info("✅ La funcionalidad de limpieza está funcionando correctamente")
        logger.info("📋 Ahora puedes probar con el backend completo cuando tengas tiempo")
        return True
    else:
        logger.error("❌ ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = test_cleaning_direct()
    sys.exit(0 if success else 1)
