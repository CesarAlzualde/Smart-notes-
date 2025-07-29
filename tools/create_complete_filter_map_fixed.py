"""
Script para crear un mapa conceptual completo con ID 'filter' en Neo4j.
Este script crea:
1. Un nodo ConceptMap con todas las propiedades requeridas
2. Varios nodos Concept relacionados
3. Relaciones RELATES_TO entre los conceptos
4. Opcionalmente, relaciones BASED_ON a NoteReference

Versión mejorada que maneja correctamente la eliminación de relaciones existentes.
"""

from neo4j import GraphDatabase
import json
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar configuración de Neo4j
def load_config():
    try:
        config_path = os.path.join("backend", "config", "db_config.json")
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        # Valores por defecto
        return {
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": "password"
            }
        }

def create_complete_filter_map():
    config = load_config()
    neo4j_config = config.get('neo4j', {})
    
    # Conectar a Neo4j
    uri = neo4j_config.get('uri', 'bolt://localhost:7687')
    user = neo4j_config.get('user', 'neo4j')
    password = neo4j_config.get('password', 'password')
    
    logger.info(f"Conectando a Neo4j en {uri}...")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Fecha actual como cadena ISO
        created_at = datetime.now().isoformat() + 'Z'
        
        # Crear nodo ConceptMap y conceptos relacionados
        with driver.session() as session:
            # PASO 1: Buscar y mostrar relaciones existentes para debugging
            result = session.run("""
            MATCH (m:ConceptMap {id: 'filter'})
            OPTIONAL MATCH (m)-[r]-()
            RETURN COUNT(r) as num_relations
            """)
            record = result.single()
            if record and record["num_relations"] > 0:
                logger.info(f"El nodo ConceptMap 'filter' tiene {record['num_relations']} relaciones que necesitan ser eliminadas")
                
            # PASO 2: Eliminar TODAS las relaciones del nodo ConceptMap primero
            result = session.run("""
            MATCH (m:ConceptMap {id: 'filter'})
            OPTIONAL MATCH (m)-[r]-()
            DELETE r
            RETURN COUNT(r) as deleted_relations
            """)
            record = result.single()
            if record:
                logger.info(f"Eliminadas {record['deleted_relations']} relaciones del nodo ConceptMap")
                
            # PASO 3: Eliminar relaciones entre Concept nodos con map_id: 'filter'
            result = session.run("""
            MATCH (c1:Concept {map_id: 'filter'})-[r]-()
            DELETE r
            RETURN COUNT(r) as deleted_concept_relations
            """)
            record = result.single()
            if record:
                logger.info(f"Eliminadas {record['deleted_concept_relations']} relaciones entre nodos Concept")
            
            # PASO 4: Eliminar todos los nodos relacionados
            result = session.run("""
            MATCH (n)
            WHERE n:Concept AND n.map_id = 'filter' OR n:ConceptMap AND n.id = 'filter' OR n:NoteReference AND EXISTS((n)<-[:BASED_ON]-(:ConceptMap {id: 'filter'}))
            DETACH DELETE n
            RETURN COUNT(n) as deleted_nodes
            """)
            record = result.single()
            if record:
                logger.info(f"Eliminados {record['deleted_nodes']} nodos relacionados con el mapa 'filter'")
            
            logger.info("Limpiado cualquier mapa existente con ID 'filter'")
            
            # PASO 5: Crear el nodo ConceptMap con todas las propiedades requeridas
            result = session.run("""
            CREATE (m:ConceptMap {
                id: 'filter', 
                name: 'Filter Concept Map',
                description: 'Map for filtered concepts',
                created_at: $created_at,
                user_id: 1,  // Asumimos usuario con ID 1
                concept_count: 5,
                relation_count: 4
            })
            RETURN m
            """, created_at=created_at)
            
            map_created = result.single() is not None
            logger.info(f"ConceptMap creado: {map_created}")
            
            # PASO 6: Crear nodos Concept
            concepts = [
                {"id": "c1", "label": "Tema Principal", "type": "main", "weight": 1.5},
                {"id": "c2", "label": "Subtema 1", "type": "secondary", "weight": 1.0},
                {"id": "c3", "label": "Subtema 2", "type": "secondary", "weight": 1.0},
                {"id": "c4", "label": "Ejemplo", "type": "example", "weight": 0.8},
                {"id": "c5", "label": "Conclusión", "type": "conclusion", "weight": 1.2}
            ]
            
            for concept in concepts:
                session.run("""
                CREATE (c:Concept {
                    id: $id,
                    label: $label,
                    type: $type,
                    weight: $weight,
                    map_id: 'filter'
                })
                """, id=concept["id"], label=concept["label"], 
                     type=concept["type"], weight=concept["weight"])
            
            logger.info(f"Creados {len(concepts)} conceptos")
            
            # PASO 7: Crear relaciones entre conceptos
            relations = [
                {"source": "c1", "target": "c2", "label": "incluye", "weight": 1.0},
                {"source": "c1", "target": "c3", "label": "contiene", "weight": 1.0},
                {"source": "c2", "target": "c4", "label": "ejemplifica", "weight": 0.9},
                {"source": "c3", "target": "c5", "label": "concluye", "weight": 1.1}
            ]
            
            for rel in relations:
                session.run("""
                MATCH (source:Concept {id: $source_id, map_id: 'filter'})
                MATCH (target:Concept {id: $target_id, map_id: 'filter'})
                CREATE (source)-[r:RELATES_TO {
                    label: $label,
                    weight: $weight,
                    map_id: 'filter'
                }]->(target)
                """, source_id=rel["source"], target_id=rel["target"],
                     label=rel["label"], weight=rel["weight"])
            
            logger.info(f"Creadas {len(relations)} relaciones")
            
            # PASO 8: Verificar que todo se haya creado correctamente
            result = session.run("""
            MATCH (m:ConceptMap {id: 'filter'})
            OPTIONAL MATCH (c:Concept {map_id: 'filter'})
            OPTIONAL MATCH (c1:Concept {map_id: 'filter'})-[r:RELATES_TO]->(c2:Concept {map_id: 'filter'})
            WITH m, count(DISTINCT c) as concepts, count(r) as relations
            RETURN m.id as id, m.name as name, concepts, relations
            """)
            
            record = result.single()
            if record:
                logger.info(f"Mapa '{record['name']}' (ID: {record['id']}) creado con {record['concepts']} conceptos y {record['relations']} relaciones")
            else:
                logger.error("No se pudo verificar la creación del mapa")
            
            # PASO 9: Mostrar las propiedades del nodo ConceptMap
            result = session.run("""
            MATCH (m:ConceptMap {id: 'filter'})
            RETURN properties(m) as props
            """)
            
            record = result.single()
            if record:
                logger.info(f"Propiedades del nodo ConceptMap: {json.dumps(record['props'], indent=2)}")
                
        driver.close()
        logger.info("Conexión a Neo4j cerrada")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creando mapa conceptual: {e}")
        return False

if __name__ == "__main__":
    print("\nEjecutando script para crear un mapa conceptual completo en Neo4j...\n")
    success = create_complete_filter_map()
    print(f"\nScript completado {'con éxito' if success else 'con errores'}.\n")
