"""
API para gestión de grafos conceptuales.
Proporciona endpoints para crear y manipular mapas de conceptos.
"""

from flask import Blueprint, request, jsonify
from ..extensions import cache
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from ..extensions import db
from ..models import Note
import json
from dataclasses import asdict
from ..services.concept_map_service import concept_map_service
from ..services.enhanced_concept_map_service import EnhancedConceptMapService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

@api_bp.route('/graph/concepts', methods=['POST'])
@jwt_required()
def generate_concept_map():
    """Genera un mapa conceptual basado en texto proporcionado o notas seleccionadas."""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Se puede generar un mapa a partir de texto directo o de notas existentes
        text_content = data.get('text', '')
        note_ids = data.get('note_ids', [])
        
        # Usar el servicio de mapas conceptuales para generar el grafo
        result = concept_map_service.generate_concept_map(
            text=text_content,
            note_ids=note_ids,
            user_id=user_id
        )
        
        # Verificar si hubo errores
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error al generar mapa conceptual: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/graph/save', methods=['POST'])
@jwt_required()
def save_concept_map():
    """Guarda un mapa conceptual creado o modificado por el usuario."""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Validar datos mínimos
        if not data.get('name') or not data.get('concepts') or not data.get('relations'):
            return jsonify({"error": "Faltan datos requeridos (nombre, conceptos, relaciones)"}), 400
        
        # Usar el servicio para guardar el mapa en Neo4j
        # Este endpoint usa el servicio antiguo, se podría migrar al nuevo si se desea
        result = concept_map_service.save_concept_map(user_id, data)
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
            
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error al guardar mapa conceptual: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/graph/related-notes/<concept>', methods=['GET'])
@jwt_required()
def get_related_notes(concept):
    """Obtiene notas relacionadas con un concepto específico."""
    try:
        user_id = get_jwt_identity()
        
        # Buscar notas que contengan el concepto (búsqueda de texto simple)
        search_term = f"%{concept}%"
        notes = Note.query.filter(
            Note.user_id == user_id,
            db.or_(
                Note.title.ilike(search_term),
                Note.content.ilike(search_term),
                Note.summary.ilike(search_term),
                Note.tags.any(db.text("name ILIKE :term")),
                Note.main_topic.ilike(search_term)
            )
        ).order_by(Note.created_at.desc()).limit(10).all()
        
        # Preparar respuesta
        result = []
        for note in notes:
            note_dict = note.to_dict()
            # Agregar snippet o contexto donde aparece el concepto
            # (Simplificado; una implementación real buscaría el concepto en el texto)
            note_dict["relevance_score"] = 0.85  # Puntuación de relevancia simulada
            result.append(note_dict)
            
        return jsonify({
            "concept": concept,
            "related_notes": result,
            "count": len(result)
        }), 200
        
    except Exception as e:
        logging.error(f"Error al buscar notas relacionadas con concepto '{concept}': {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/graph/expand-concept/<concept>', methods=['GET'])
@jwt_required()
def expand_concept(concept):
    """Expande un concepto generando conceptos relacionados."""
    try:
        # Este es un endpoint para expandir mapas conceptuales
        # Simula la generación de conceptos relacionados mediante IA
        
        concepts = [
            {"id": f"{concept}_sub1", "label": f"Subtema de {concept} 1", "type": "subtopic", "weight": 0.75},
            {"id": f"{concept}_sub2", "label": f"Subtema de {concept} 2", "type": "subtopic", "weight": 0.7},
            {"id": f"{concept}_rel1", "label": f"Concepto relacionado 1", "type": "related", "weight": 0.65},
            {"id": f"{concept}_rel2", "label": f"Concepto relacionado 2", "type": "related", "weight": 0.6},
        ]
        
        relations = [
            {"source": concept, "target": f"{concept}_sub1", "label": "contiene", "weight": 0.8},
            {"source": concept, "target": f"{concept}_sub2", "label": "incluye", "weight": 0.75},
            {"source": concept, "target": f"{concept}_rel1", "label": "relaciona con", "weight": 0.7},
            {"source": concept, "target": f"{concept}_rel2", "label": "asociado a", "weight": 0.65},
        ]
        
        return jsonify({
            "original_concept": concept,
            "related_concepts": concepts,
            "new_relations": relations
        }), 200
        
    except Exception as e:
        logging.error(f"Error al expandir concepto '{concept}': {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/graph/<string:map_id>', methods=['GET'])
@jwt_required()
def get_concept_map(map_id):
    """Obtiene un mapa conceptual específico por su ID."""
    try:
        user_id = get_jwt_identity()

        # Usar el servicio mejorado para obtener el mapa conceptual
        enhanced_service = EnhancedConceptMapService()
        result = enhanced_service.get_concept_map_by_id(map_id, user_id)
        
        if not result or ('error' in result and result['error']):
            error_msg = result.get('error') if result else 'Mapa no encontrado'
            logger.warning(f"No se pudo obtener el mapa conceptual {map_id} para el usuario {user_id}. Razón: {error_msg}")
            # Devolver un grafo vacío para que el frontend no falle con la estructura que espera
            return jsonify({"id": map_id, "name": "Mapa vacío", "concepts": [], "relations": []}), 200
            
        # Adaptar la respuesta para que el frontend reciba 'concepts' y 'relations'
        adapted_result = {
            "id": result.get("id", map_id),
            "name": result.get("name", f"Mapa {map_id}"),
            "concepts": result.get("nodes", []),  # Frontend espera 'concepts'
            "relations": result.get("links", []),  # Frontend espera 'relations'
            "metadata": result.get("metadata", {})
        }
        
        return jsonify(adapted_result), 200
        
    except Exception as e:
        logging.error(f"Error al obtener mapa conceptual: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/graph/maps/<map_id>', methods=['DELETE'])
@jwt_required()
def delete_concept_map(map_id):
    """Elimina un mapa conceptual específico por su ID."""
    try:
        user_id = get_jwt_identity()
        enhanced_service = EnhancedConceptMapService()
        
        success = enhanced_service.delete_concept_map(map_id, user_id)
        
        if success:
            return jsonify({"message": f"Mapa {map_id} eliminado correctamente"}), 200
        else:
            return jsonify({"error": "No se pudo eliminar el mapa. Puede que no exista o no tengas permiso."}), 404
            
    except Exception as e:
        logging.error(f"Error al eliminar mapa conceptual: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/graph/visualization', methods=['GET'])
@jwt_required()
@cache.cached(timeout=1) # Cache muy corta para evitar datos obsoletos
def get_graph_visualization():
    """Obtiene la visualización de gráficos conceptuales guardados por el usuario."""
    try:
        user_id = int(get_jwt_identity())
        
        # Obtener los mapas del usuario desde Neo4j usando el servicio mejorado
        enhanced_service = EnhancedConceptMapService()
        maps = enhanced_service.get_user_concept_maps(user_id)
        
        if isinstance(maps, dict) and "error" in maps:
            return jsonify({"error": maps["error"]}), 500
        
        # Si no hay mapas, devolver un dashboard vacío
        if not maps:
            return jsonify({
                "recent_maps": [],
                "statistics": {
                    "total_maps": 0,
                    "total_concepts": 0,
                    "total_relations": 0,
                    "most_connected_concept": "",
                    "average_concepts_per_map": 0
                },
                "concepts_cloud": []
            }), 200
        
        # Procesar los resultados para el dashboard
        recent_maps = []
        total_concepts = 0
        total_relations = 0
        concept_counts = {}
        
        for map_data in maps:
            # Añadir a mapas recientes
            recent_maps.append({
                "id": map_data.get("id"),
                "name": map_data.get("name"),
                "created_at": map_data.get("created_at"),
                "concept_count": map_data.get("concept_count", 0),
                "relation_count": map_data.get("relation_count", 0),
                # No generamos miniaturas por ahora
                "thumbnail": "" 
            })
            
            # Actualizar estadísticas
            total_concepts += map_data.get("concept_count") or 0
            total_relations += map_data.get("relation_count") or 0
            
        # Limitar a los 5 mapas más recientes
        recent_maps = recent_maps[:5]
        
        # Crear nube de conceptos (se podría expandir con una consulta específica para esto)
        concepts_cloud = []
        
        # Construir el dashboard
        visualization_data = {
            "recent_maps": recent_maps,
            "statistics": {
                "total_maps": len(maps),
                "total_concepts": total_concepts,
                "total_relations": total_relations,
                "most_connected_concept": "",  # Se podría llenar con otra consulta
                "average_concepts_per_map": total_concepts / len(maps) if len(maps) > 0 else 0
            },
            "concepts_cloud": concepts_cloud
        }
        
        return jsonify(visualization_data), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener visualización de grafos: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener visualización de grafos: {str(e)}",
            "traceback": error_traceback
        }), 500


# ==== NUEVOS ENDPOINTS PARA GENERACIÓN AUTOMÁTICA ====

@api_bp.route('/graph/generate-from-note', methods=['POST'])
@jwt_required()
def auto_generate_concept_map_from_note():
    """Genera automáticamente un mapa conceptual desde una nota específica.
    Usa modo básico por defecto para evitar saturación de memoria.
    El frontend puede solicitar análisis completo con IA mediante 'use_ai_analysis=true'.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        note_id = data.get('note_id')
        
        # Parámetro opcional para usar análisis completo con IA
        use_ai_analysis = data.get('use_ai_analysis', False)  # Por defecto: modo básico

        if not note_id:
            return jsonify({"error": "note_id is required"}), 400

        # Verificar que la nota pertenece al usuario
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({"error": "Note not found or not accessible"}), 404
        
        # Log del modo seleccionado
        mode = "IA completo" if use_ai_analysis else "básico (sin IA pesada)"
        logger.info(f"Generando mapa conceptual para nota {note_id} en modo {mode}")
        
        # Usar el servicio mejorado con el modo seleccionado
        enhanced_service = EnhancedConceptMapService()
        map_id = enhanced_service.generate_and_save_map(note_id, user_id, use_ai_analysis)
        
        if map_id is None:
            return jsonify({"error": "No se pudo generar el mapa conceptual"}), 500
            
        # Si tenemos el ID, podemos obtener el mapa completo usando get_concept_map_by_id
        map_data = enhanced_service.get_concept_map_by_id(map_id, user_id)
        
        if not map_data or ('error' in map_data and map_data['error']):
            return jsonify({"error": "Se generó el mapa pero no se pudo recuperar"}), 500
            
        # Devolver respuesta completa con datos del grafo para renderizado inmediato
        return jsonify({
            "message": f"Mapa conceptual generado exitosamente en modo {mode}",
            "concept_map_id": map_id,
            "id": map_id,
            "name": map_data.get("name", f"Mapa conceptual auto-generado"),
            "concepts": map_data.get("nodes", []),  # Frontend espera 'concepts'
            "relations": map_data.get("links", []),  # Frontend espera 'relations'
            "map_data": {
                "id": map_id,
                "name": map_data.get("name", f"Mapa conceptual auto-generado"),
                "concepts": map_data.get("nodes", []),
                "relations": map_data.get("links", [])
            },
            "generation_mode": {
                "ai_analysis_used": use_ai_analysis,
                "mode_description": mode,
                "optimization": "Memoria optimizada" if not use_ai_analysis else "Análisis IA completo"
            },
            "stats": {
                "nodes_created": len(map_data.get("nodes", [])),
                "edges_created": len(map_data.get("links", [])),
                "performance": "Rápido" if not use_ai_analysis else "Completo"
            }
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error in auto-generate: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error auto-generating concept map: {str(e)}")
        return jsonify({"error": f"Failed to generate concept map: {str(e)}"}), 500


@api_bp.route('/graph/neighbors/<node_id>', methods=['GET'])
@jwt_required()
def get_node_neighbors(node_id):
    """Obtiene los nodos vecinos de un nodo específico para expansión dinámica."""
    try:
        user_id = get_jwt_identity()
        depth = request.args.get('depth', 1, type=int)
        
        # Limitar profundidad para evitar consultas muy costosas
        if depth > 3:
            depth = 3
        
        # Simular obtención de vecinos (en implementación real sería desde Neo4j)
        neighbors_data = {
            "nodes": [
                {
                    "id": f"{node_id}_neighbor_1",
                    "label": f"Neighbor 1 of {node_id}",
                    "type": "related",
                    "color": "#42A5F5",
                    "size": 12
                },
                {
                    "id": f"{node_id}_neighbor_2",
                    "label": f"Neighbor 2 of {node_id}",
                    "type": "related",
                    "color": "#66BB6A",
                    "size": 10
                }
            ],
            "links": [
                {
                    "source": node_id,
                    "target": f"{node_id}_neighbor_1",
                    "label": "relates_to",
                    "color": "#757575"
                },
                {
                    "source": node_id,
                    "target": f"{node_id}_neighbor_2",
                    "label": "connects_to",
                    "color": "#757575"
                }
            ]
        }
        
        return jsonify(neighbors_data), 200
        
    except Exception as e:
        logger.error(f"Error getting node neighbors: {str(e)}")
        return jsonify({"error": f"Failed to get neighbors: {str(e)}"}), 500


@api_bp.route('/graph/semantic-analysis', methods=['POST'])
@jwt_required()
def analyze_semantic_relationships():
    """Analiza relaciones semánticas entre múltiples notas para crear un mapa unificado."""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        note_ids = data.get('note_ids', [])
        if not note_ids:
            return jsonify({"error": "No note IDs provided"}), 400
        
        # Verificar que todas las notas pertenecen al usuario
        notes = Note.query.filter(
            Note.id.in_(note_ids),
            Note.user_id == user_id
        ).all()
        
        if len(notes) != len(note_ids):
            return jsonify({"error": "Some notes not found or not accessible"}), 404
        
        # Generar mapa conceptual multi-nota
        enhanced_service = EnhancedConceptMapService()
        
        # Por ahora, generar un mapa simple combinando las notas
        multi_map_data = {
            "id": f"multi_note_{len(note_ids)}",
            "name": f"Combined Map ({len(note_ids)} notes)",
            "nodes": [],
            "edges": [],
            "metadata": {
                "note_count": len(note_ids),
                "note_ids": note_ids,
                "generated_at": "2025-01-09T16:50:33",
                "type": "multi_note_semantic"
            }
        }
        
        # Agregar nodos centrales para cada nota con formato único
        for i, note in enumerate(notes):
            node = {
                "id": f"semantic_note_{note.id}_{i}",  # Formato único para evitar colisiones
                "label": note.title,
                "type": "central",
                "color": "#FF6B6B",
                "size": 18,
                "x": i * 150 - (len(notes) * 75),  # Distribución horizontal
                "y": 0
            }
            multi_map_data["nodes"].append(node)
        
        # Agregar conexiones semánticas entre notas (simplificado)
        for i in range(len(notes) - 1):
            edge = {
                "id": f"semantic_{i}_{i+1}",
                "source": f"semantic_note_{notes[i].id}_{i}",  # ID coincidente con el nodo
                "target": f"semantic_note_{notes[i+1].id}_{i+1}",  # ID coincidente con el nodo
                "label": "semantically_related",
                "color": "#9C27B0",
                "width": 2
            }
            multi_map_data["edges"].append(edge)
        
        return jsonify({
            "message": "Semantic analysis completed",
            "map_data": multi_map_data,
            "analysis_results": {
                "notes_processed": len(notes),
                "semantic_connections_found": len(multi_map_data["edges"]),
                "similarity_score": 0.75  # Placeholder
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in semantic analysis: {str(e)}")
        return jsonify({"error": f"Semantic analysis failed: {str(e)}"}), 500
