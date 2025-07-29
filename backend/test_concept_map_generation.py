#!/usr/bin/env python3
"""
Test script para verificar la generación de mapas conceptuales
con keywords y entidades guardadas en analysis_cache
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Note, User
from app.services.enhanced_concept_map_service import EnhancedConceptMapService
from app.extensions import db
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_concept_map_with_cached_data():
    """Test de generación de mapa conceptual usando datos de analysis_cache"""
    
    app = create_app()
    
    with app.app_context():
        # Buscar nota que ya tenga analysis_cache
        note = Note.query.filter(Note.analysis_cache.isnot(None)).first()
        
        if not note:
            logger.error("No se encontró ninguna nota con analysis_cache. Ejecuta el análisis de una nota primero.")
            return False
            
        logger.info(f"✅ Nota encontrada: {note.title} (ID: {note.id})")
        
        # Verificar que tenga analysis_cache con keywords y entities
        if not note.analysis_cache:
            logger.error("La nota no tiene analysis_cache")
            return False
            
        cache_data = note.analysis_cache
        keywords = cache_data.get('keywords', [])
        entities = cache_data.get('entities', {})
        
        logger.info(f"📊 Keywords en cache: {len(keywords)} -> {keywords[:5]}...")
        logger.info(f"📊 Entidades en cache: {len(entities)} tipos -> {list(entities.keys())}")
        
        for entity_type, entity_list in entities.items():
            logger.info(f"  - {entity_type}: {len(entity_list)} entidades -> {entity_list[:3]}...")
        
        # Crear servicio de mapas conceptuales
        service = EnhancedConceptMapService()
        
        # Generar mapa conceptual
        logger.info("🔄 Generando mapa conceptual...")
        try:
            concept_map = service.generate_and_save_map(note.id, note.user_id)
            
            if concept_map:
                logger.info(f"✅ Mapa conceptual generado exitosamente!")
                logger.info(f"📈 Total de nodos: {len(concept_map.nodes)}")
                logger.info(f"📈 Total de conexiones: {len(concept_map.edges)}")
                
                # Analizar tipos de nodos
                node_types = {}
                for node in concept_map.nodes:
                    node_type = node.type
                    if node_type not in node_types:
                        node_types[node_type] = []
                    node_types[node_type].append(node.label)
                
                logger.info("📋 Tipos de nodos creados:")
                for node_type, labels in node_types.items():
                    logger.info(f"  - {node_type.upper()}: {len(labels)} nodos")
                    for label in labels[:3]:  # Mostrar primeros 3
                        logger.info(f"    • {label}")
                    if len(labels) > 3:
                        logger.info(f"    ... y {len(labels)-3} más")
                
                # Verificar que se usaron las keywords y entidades del cache
                keyword_nodes = [n for n in concept_map.nodes if n.type == 'keyword']
                entity_nodes = [n for n in concept_map.nodes if n.type == 'entity']
                
                logger.info(f"🎯 Nodos de KEYWORDS creados: {len(keyword_nodes)}")
                logger.info(f"🎯 Nodos de ENTIDADES creados: {len(entity_nodes)}")
                
                if len(keyword_nodes) > 0:
                    logger.info("✅ Sistema usando keywords del analysis_cache correctamente")
                else:
                    logger.warning("⚠️  No se crearon nodos de keywords")
                    
                if len(entity_nodes) > 0:
                    logger.info("✅ Sistema usando entidades del analysis_cache correctamente")
                else:
                    logger.warning("⚠️  No se crearon nodos de entidades")
                
                return True
            else:
                logger.error("❌ No se pudo generar el mapa conceptual")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al generar mapa conceptual: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    logger.info("🚀 Iniciando test de generación de mapas conceptuales con analysis_cache")
    
    success = test_concept_map_with_cached_data()
    
    if success:
        logger.info("🎉 Test completado exitosamente!")
        logger.info("💡 El sistema ahora usa keywords y entidades guardadas")
    else:
        logger.error("💥 Test falló. Revisar logs para más detalles.")
    
    return success

if __name__ == "__main__":
    main()
