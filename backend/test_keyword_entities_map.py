#!/usr/bin/env python3
"""
Test simplificado para verificar que se utilizan keywords y entidades desde analysis_cache
"""

import sys
import os
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar solo lo necesario para el test
from app.models.note import Note
from app.services.enhanced_concept_map_service import ConceptNode, ConceptEdge

def create_mock_note_with_analysis_cache():
    """Crea un objeto Note con analysis_cache para pruebas"""
    
    # Crear una nota de prueba con análisis
    note = Note(
        id=999,
        title="Nota de prueba para mapas conceptuales",
        content="Este es un contenido de ejemplo para probar la funcionalidad de mapas conceptuales con keywords y entidades.",
        user_id=1
    )
    
    # Simular análisis_cache como lo haría el endpoint real
    note.analysis_cache = {
        "keywords": ["mapas", "conceptuales", "análisis", "keywords", "entidades", "persistencia"],
        "entities": {
            "PER": ["María García", "Juan Pérez"],
            "ORG": ["Universidad Autónoma", "Instituto Nacional"],
            "LOC": ["Madrid", "Barcelona"],
            "OTH": ["Sistema", "Proyecto"]
        },
        "summary": "Resumen de prueba",
        "main_topic": "Mapas conceptuales",
        "sentiment": "neutral",
        "readability": 75.5,
        "stats": {"sentences": 10, "words": 150},
        "analyzed_at": datetime.now().isoformat()
    }
    
    return note

def test_entity_node_creation():
    """Prueba la creación de nodos de entidades usando análisis cache"""
    from app.services.enhanced_concept_map_service import EnhancedConceptMapService
    
    # Crear servicio y nota mock
    service = EnhancedConceptMapService()
    note = create_mock_note_with_analysis_cache()
    
    # Probar creación de nodos de entidades
    logger.info("Probando creación de nodos de entidades...")
    entity_nodes = service._create_entity_nodes(note)
    
    # Verificar resultados
    logger.info(f"✅ Total de nodos de entidades creados: {len(entity_nodes)}")
    
    # Agrupar por tipo
    entity_types = {}
    for node in entity_nodes:
        entity_type = node.properties.get('entity_type', 'desconocido')
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        entity_types[entity_type].append(node.label)
    
    # Mostrar resultados por tipo
    for entity_type, entities in entity_types.items():
        logger.info(f"  - Tipo {entity_type}: {len(entities)} entidades")
        for entity in entities:
            logger.info(f"    • {entity}")
    
    return len(entity_nodes) > 0

def test_keyword_node_creation():
    """Prueba la creación de nodos de keywords usando análisis cache"""
    from app.services.enhanced_concept_map_service import EnhancedConceptMapService
    
    # Crear servicio y nota mock
    service = EnhancedConceptMapService()
    note = create_mock_note_with_analysis_cache()
    
    # Probar creación de nodos de keywords
    logger.info("Probando creación de nodos de keywords...")
    keyword_nodes = service._create_keyword_nodes(note)
    
    # Verificar resultados
    logger.info(f"✅ Total de nodos de keywords creados: {len(keyword_nodes)}")
    
    # Mostrar keywords extraídas
    keywords = [node.label for node in keyword_nodes]
    logger.info(f"  - Keywords: {keywords}")
    
    return len(keyword_nodes) > 0

def main():
    """Función principal de pruebas"""
    logger.info("🧪 Iniciando pruebas de mapas conceptuales con keywords y entidades")
    
    # Probar creación de nodos de entidades
    entities_ok = test_entity_node_creation()
    
    # Probar creación de nodos de keywords
    keywords_ok = test_keyword_node_creation()
    
    # Resultados finales
    if entities_ok and keywords_ok:
        logger.info("✅ PRUEBAS EXITOSAS: Sistema de mapas conceptuales con keywords y entidades persistentes funciona correctamente")
    else:
        logger.error("❌ PRUEBAS FALLIDAS: Revisar logs para más detalles")

if __name__ == "__main__":
    main()
