"""
Script de prueba para verificar la generación de mapas conceptuales jerárquicos
con datos persistentes desde analysis_cache y estructura organizada por categorías
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configurar el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_hierarchical_map")

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_session
from app.models.note import Note
from app.services.enhanced_concept_map_service import EnhancedConceptMapService

def test_hierarchical_map_generation():
    """Prueba la generación de mapas conceptuales con estructura jerárquica"""
    
    map_service = EnhancedConceptMapService()
    
    # Usar get_session como context manager con 'with'
    with get_session() as session:
        try:
            # Buscar una nota que tenga analysis_cache para probar
            note = session.query(Note).filter(
                Note.analysis_cache.isnot(None)
            ).first()
            
            if not note:
                logger.error("No se encontró ninguna nota con análisis en caché.")
                return False
                
            logger.info(f"Usando nota ID {note.id}: '{note.title}' para prueba")
            
            if hasattr(note, 'analysis_cache') and note.analysis_cache:
                logger.info(f"La nota tiene analysis_cache: {json.dumps(note.analysis_cache)[:200]}...")
                if 'keywords' in note.analysis_cache:
                    logger.info(f"Keywords encontradas: {note.analysis_cache['keywords'][:5]}")
                if 'entities' in note.analysis_cache:
                    for entity_type, entities in note.analysis_cache['entities'].items():
                        logger.info(f"Entidades tipo {entity_type}: {entities[:3]}")
            else:
                logger.warning("La nota no tiene analysis_cache apropiadamente estructurado")
            
            # Generar mapa conceptual con estructura jerárquica
            logger.info("Generando mapa conceptual jerárquico...")
            start_time = datetime.now()
            map_id = map_service.generate_and_save_map(note.id, note.user_id)
            end_time = datetime.now()
            
            if map_id:
                duration = (end_time - start_time).total_seconds()
                logger.info(f"✅ Mapa conceptual creado exitosamente con ID: {map_id}")
                logger.info(f"⏱️ Tiempo de generación: {duration:.2f} segundos")
                
                # Recuperar el mapa para verificar su estructura
                concept_map = map_service.get_concept_map_by_id(map_id, note.user_id)
                
                if concept_map:
                    # Analizar la estructura jerárquica
                    nodes = concept_map.get('nodes', [])
                    edges = concept_map.get('edges', [])
                    
                    # Contar nodos por tipo
                    node_types = {}
                    for node in nodes:
                        node_type = node.get('type')
                        if node_type not in node_types:
                            node_types[node_type] = 0
                        node_types[node_type] += 1
                    
                    logger.info(f"📊 Estructura del mapa conceptual:")
                    logger.info(f"   - Total de nodos: {len(nodes)}")
                    logger.info(f"   - Total de conexiones: {len(edges)}")
                    logger.info(f"   - Tipos de nodos: {node_types}")
                    
                    # Verificar categorías y jerarquía
                    categories = [n for n in nodes if n.get('type') == 'category']
                    logger.info(f"   - Nodos categoría: {len(categories)}")
                    
                    for cat in categories:
                        # Contar conexiones desde esta categoría
                        cat_edges = [e for e in edges if e.get('source') == cat.get('id')]
                        logger.info(f"   - Categoría '{cat.get('label')}' tiene {len(cat_edges)} conexiones")
                    
                    return True
                else:
                    logger.error("No se pudo recuperar el mapa conceptual")
                    return False
            else:
                logger.error("No se pudo generar el mapa conceptual")
                return False
                
        except Exception as e:
            logger.error(f"Error durante la prueba: {str(e)}")
            return False
            
    # No es necesario session.close() al usar with

if __name__ == "__main__":
    logger.info("Iniciando prueba de generación de mapas conceptuales jerárquicos...")
    result = test_hierarchical_map_generation()
    
    if result:
        logger.info("✅ Prueba completada exitosamente")
    else:
        logger.error("❌ Prueba fallida")
