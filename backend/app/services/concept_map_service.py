"""
Servicio para la generación y gestión de mapas conceptuales.
Utiliza la información extraída de textos para crear grafos visuales.
"""

import logging
import uuid
from datetime import datetime

from .neo4j_service import neo4j_service

class ConceptMapService:
    """
    Servicio para gestionar mapas conceptuales en Neo4j.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_concept_map(self, text="", note_ids=None, user_id=None):
        """
        Genera un mapa conceptual a partir de texto o notas existentes.
        
        Args:
            text (str): Texto para analizar y generar mapa.
            note_ids (list): Lista de IDs de notas para incluir.
            user_id (int): ID del usuario que solicita el mapa.
            
        Returns:
            dict: Mapa conceptual generado o error.
        """
        try:
            self.logger.info(f"Generando mapa conceptual para usuario {user_id} con {len(note_ids) if note_ids else 0} notas")
            
            # Este es un mapa conceptual simplificado generado automáticamente
            # En una implementación real, aquí se analizaría el texto o se extraerían
            # conceptos de las notas usando NLP
            
            map_data = {
                "id": str(uuid.uuid4()),
                "name": f"Mapa generado {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "nodes": [],
                "edges": []
            }
            
            # Generar algunos conceptos de ejemplo
            # En una implementación real, estos vendrían del análisis del texto
            sample_concepts = [
                {"id": "c1", "label": "Concepto Principal", "type": "main", "weight": 1.5},
                {"id": "c2", "label": "Idea Secundaria", "type": "secondary", "weight": 1.0},
                {"id": "c3", "label": "Ejemplo Concreto", "type": "example", "weight": 0.8},
                {"id": "c4", "label": "Argumento", "type": "argument", "weight": 1.2},
                {"id": "c5", "label": "Conclusión", "type": "conclusion", "weight": 1.3}
            ]
            
            # Generar algunas relaciones de ejemplo
            sample_relations = [
                {"source": "c1", "target": "c2", "label": "incluye", "weight": 1.0},
                {"source": "c2", "target": "c3", "label": "ilustrado por", "weight": 0.9},
                {"source": "c1", "target": "c4", "label": "apoyado por", "weight": 1.1},
                {"source": "c4", "target": "c5", "label": "lleva a", "weight": 1.0},
                {"source": "c1", "target": "c5", "label": "concluye con", "weight": 1.2}
            ]
            
            map_data["nodes"] = sample_concepts
            map_data["edges"] = sample_relations
            
            return map_data
            
        except Exception as e:
            self.logger.error(f"Error al generar mapa conceptual: {e}")
            return {"error": str(e)}
    
    def create_concept_map(self, name, concepts, relations, user_id=None, note_ids=None):
        """
        Crea un nuevo mapa conceptual y lo guarda en Neo4j.
        
        Args:
            name (str): Nombre del mapa conceptual.
            concepts (list): Lista de nodos/conceptos.
            relations (list): Lista de relaciones entre conceptos.
            user_id (int, optional): ID del usuario creador.
            note_ids (list, optional): Lista de IDs de notas asociadas.
            
        Returns:
            dict: Información del mapa creado o error.
        """
        try:
            map_id = str(uuid.uuid4())
            
            # Crear nodo del mapa
            create_map_query = """
            CREATE (m:ConceptMap {
                id: $id,
                name: $name,
                created_at: $created_at,
                user_id: $user_id,
                concept_count: $concept_count,
                relation_count: $relation_count
            })
            RETURN m
            """
            
            map_params = {
                'id': map_id,
                'name': name,
                'created_at': datetime.now().isoformat(),
                'user_id': user_id,
                'concept_count': len(concepts),
                'relation_count': len(relations)
            }
            
            neo4j_service.execute_query(create_map_query, map_params)
            
            # Crear conceptos
            for concept in concepts:
                create_concept_query = """
                CREATE (c:Concept {
                    id: $id,
                    label: $label,
                    type: $type,
                    weight: $weight,
                    map_id: $map_id
                })
                """
                
                params = {
                    'id': concept['id'],
                    'label': concept['label'],
                    'type': concept.get('type', 'concept'),
                    'weight': concept.get('weight', 1.0),
                    'map_id': map_id
                }
                
                # Agregar propiedades adicionales si existen
                for key in concept:
                    if key not in ['id', 'label', 'type', 'weight']:
                        params[key] = concept[key]
                
                neo4j_service.execute_query(create_concept_query, params)
            
            # Crear relaciones
            for relation in relations:
                create_relation_query = """
                MATCH (source:Concept {id: $source_id, map_id: $map_id})
                MATCH (target:Concept {id: $target_id, map_id: $map_id})
                CREATE (source)-[r:RELATES_TO {
                    label: $label,
                    weight: $weight,
                    map_id: $map_id
                }]->(target)
                """
                
                neo4j_service.execute_query(create_relation_query, {
                    'source_id': relation['source'],
                    'target_id': relation['target'],
                    'label': relation['label'],
                    'weight': relation['weight'],
                    'map_id': map_id
                })
            
            # Vincular a notas si existen IDs de notas
            if note_ids:
                for note_id in note_ids:
                    link_note_query = """
                    MATCH (m:ConceptMap {id: $map_id})
                    CREATE (m)-[r:BASED_ON]->(n:NoteReference {note_id: $note_id})
                    """
                    
                    neo4j_service.execute_query(link_note_query, {
                        'map_id': map_id,
                        'note_id': note_id
                    })
            
            return {
                'id': map_id,
                "name": name,
                'concept_count': len(concepts),
                'relation_count': len(relations)
            }
            
        except Exception as e:
            self.logger.error(f"Error al guardar mapa conceptual en Neo4j: {e}")
            return {"error": str(e)}
    
    def get_concept_map(self, map_id):
        """
        Recupera un mapa conceptual completo desde Neo4j.
        
        Args:
            map_id (str): ID del mapa conceptual.
            
        Returns:
            dict: Mapa conceptual con nodos y relaciones.
        """
        try:
            # Consultar datos del mapa
            map_query = """
            MATCH (m:ConceptMap {id: $map_id})
            RETURN m
            """
            
            map_result = neo4j_service.execute_query(map_query, {'map_id': map_id})
            
            if not map_result:
                return {"error": f"No se encontró mapa conceptual con ID: {map_id}"}
            
            map_info = map_result[0]['m']
            
            # Obtener conceptos
            concepts_query = """
            MATCH (c:Concept {map_id: $map_id})
            RETURN c
            """
            
            concepts_result = neo4j_service.execute_query(concepts_query, {'map_id': map_id})
            concepts = [record['c'] for record in concepts_result]
            
            # Obtener relaciones
            relations_query = """
            MATCH (source:Concept {map_id: $map_id})-[r:RELATES_TO]->(target:Concept {map_id: $map_id})
            RETURN source.id as source, target.id as target, r.label as label, r.weight as weight
            """
            
            relations_result = neo4j_service.execute_query(relations_query, {'map_id': map_id})
            relations = [record for record in relations_result]
            
            # Obtener notas vinculadas
            notes_query = """
            MATCH (m:ConceptMap {id: $map_id})-[:BASED_ON]->(n:NoteReference)
            RETURN n.note_id as note_id
            """
            
            notes_result = neo4j_service.execute_query(notes_query, {'map_id': map_id})
            note_ids = [record['note_id'] for record in notes_result]
            
            return {
                'id': map_id,
                'name': map_info.get('name', 'Mapa conceptual sin nombre'),
                'user_id': map_info.get('user_id'),
                'created_at': map_info.get('created_at'),
                'concepts': concepts,
                'relations': relations,
                'note_ids': note_ids,
                'concept_count': len(concepts),
                'relation_count': len(relations)
            }
            
        except Exception as e:
            self.logger.error(f"Error al recuperar mapa conceptual: {e}")
            return {"error": str(e)}
    
    def get_user_concept_maps(self, user_id):
        """
        Obtiene una lista de todos los mapas conceptuales de un usuario.
        
        Args:
            user_id (int): ID del usuario.
            
        Returns:
            list: Lista de mapas conceptuales resumidos.
        """
        try:
            query = """
            MATCH (m:ConceptMap {user_id: $user_id})
            RETURN m.id as id, m.name as name, m.created_at as created_at,
                   m.concept_count as concept_count, m.relation_count as relation_count
            ORDER BY m.created_at DESC
            """
            
            result = neo4j_service.execute_query(query, {'user_id': user_id})
            
            if not result:
                return []
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error al obtener mapas conceptuales del usuario: {e}")
            return {"error": str(e)}
    
    def delete_concept_map(self, map_id, user_id):
        """
        Elimina un mapa conceptual y todos sus conceptos y relaciones.
        
        Args:
            map_id (str): ID del mapa conceptual.
            user_id (int): ID del usuario para verificar propiedad.
            
        Returns:
            dict: Resultado de la operación.
        """
        try:
            # Verificar que el mapa pertenece al usuario
            check_query = """
            MATCH (m:ConceptMap {id: $map_id, user_id: $user_id})
            RETURN m
            """
            
            check_result = neo4j_service.execute_query(check_query, {
                'map_id': map_id,
                'user_id': user_id
            })
            
            if not check_result:
                return {"error": "No tienes permiso para eliminar este mapa o no existe"}
            
            # Eliminar relaciones
            delete_relations_query = """
            MATCH ()-[r:RELATES_TO {map_id: $map_id}]->()
            DELETE r
            """
            
            neo4j_service.execute_query(delete_relations_query, {'map_id': map_id})
            
            # Eliminar referencias a notas
            delete_note_refs_query = """
            MATCH (m:ConceptMap {id: $map_id})-[:BASED_ON]->(n:NoteReference)
            DETACH DELETE n
            """
            
            neo4j_service.execute_query(delete_note_refs_query, {'map_id': map_id})
            
            # Eliminar conceptos
            delete_concepts_query = """
            MATCH (c:Concept {map_id: $map_id})
            DELETE c
            """
            
            neo4j_service.execute_query(delete_concepts_query, {'map_id': map_id})
            
            # Eliminar mapa
            delete_map_query = """
            MATCH (m:ConceptMap {id: $map_id})
            DELETE m
            """
            
            neo4j_service.execute_query(delete_map_query, {'map_id': map_id})
            
            return {"success": True, "message": "Mapa conceptual eliminado correctamente"}
            
        except Exception as e:
            self.logger.error(f"Error al eliminar mapa conceptual: {e}")
            return {"error": str(e)}

    def save_concept_map(self, user_id, data):
        """
        Interfaz para el método create_concept_map utilizado en la API.
        
        Args:
            user_id (int): ID del usuario que guarda el mapa.
            data (dict): Datos del mapa conceptual (nombre, conceptos, relaciones).
            
        Returns:
            dict: Información del mapa guardado o error.
        """
        try:
            self.logger.info(f"Guardando mapa conceptual para usuario {user_id}")
            
            # Validar datos requeridos
            if not data.get('name') or not data.get('concepts') or not data.get('relations'):
                return {"error": "Faltan datos requeridos (nombre, conceptos, relaciones)"}
                
            # Extraer datos del mapa
            name = data.get('name')
            concepts = data.get('concepts', [])
            relations = data.get('relations', [])
            note_ids = data.get('note_ids', [])
            
            # Crear mapa conceptual
            result = self.create_concept_map(
                name=name,
                concepts=concepts,
                relations=relations,
                user_id=user_id,
                note_ids=note_ids
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al guardar mapa conceptual: {e}")
            return {"error": str(e)}

# Instancia global para usar en la aplicación
concept_map_service = ConceptMapService()
