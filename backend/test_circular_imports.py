#!/usr/bin/env python3
"""
Script para resolver el problema de importación circular
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Prueba la importación para detectar problemas circulares"""
    
    logger.info("Probando importación de EnhancedConceptMapService desde app.services...")
    try:
        from app.services.enhanced_concept_map_service import EnhancedConceptMapService
        logger.info("✅ Importación exitosa de EnhancedConceptMapService")
        return True
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        logger.info("✅ Test de importación completado exitosamente")
    else:
        logger.error("❌ Test de importación falló")
