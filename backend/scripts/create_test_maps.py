import os
import json
from neo4j import GraphDatabase
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_neo4j_driver():
    """Crea y retorna una instancia del driver de Neo4j."""
    try:
        # La ruta es relativa a la ubicación del script
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.json')
        with open(config_path) as config_file:
            config = json.load(config_file)['neo4j']
        uri = config['uri']
        user = config['user']
        password = config['password']
        return GraphDatabase.driver(uri, auth=(user, password))
    except Exception as e:
        logger.error(f"No se pudo crear el driver de Neo4j: {e}")
        return None

def create_test_data(driver, user_id, note_id, note_title):
    """Crea un mapa conceptual de prueba en Neo4j."""
    map_id = f"test_map_for_note_{note_id}"
    name = f"Mapa de Prueba: {note_title}"
    now_iso = datetime.utcnow().isoformat()
    metadata_json = json.dumps({'source': 'test_script'})

    with driver.session() as session:
        tx = session.begin_transaction()
        try:
            # Crear un nodo Note de prueba (simulando que viene de PostgreSQL)
            tx.run("MERGE (n:Note {id: $id}) SET n.title = $title, n.user_id = $user_id",
                   id=note_id, title=note_title, user_id=user_id)
            
            # Crear o actualizar el ConceptMap y vincularlo al usuario
            tx.run("""
                MERGE (cm:ConceptMap {id: $map_id})
                ON CREATE SET
                    cm.name = $name,
                    cm.user_id = $user_id,
                    cm.note_id = $note_id,
                    cm.created_at = $now,
                    cm.updated_at = $now,
                    cm.metadata = $metadata,
                    cm.concept_count = 5,  // Valor de prueba
                    cm.relation_count = 4  // Valor de prueba
                ON MATCH SET
                    cm.name = $name,
                    cm.user_id = $user_id,
                    cm.note_id = $note_id,
                    cm.updated_at = $now,
                    cm.concept_count = 5,  // Valor de prueba
                    cm.relation_count = 4  // Valor de prueba
            """, map_id=map_id, name=name, user_id=user_id, note_id=note_id, now=now_iso, metadata=metadata_json)

            # Vincular el mapa a la nota
            tx.run("""
                MATCH (cm:ConceptMap {id: $map_id})
                MATCH (n:Note {id: $note_id})
                MERGE (cm)-[:GENERATED_FROM]->(n)
            """, map_id=map_id, note_id=note_id)

            # Crear nodos conceptuales de prueba
            concepts = [
                {"id": f"{map_id}_concept_1", "name": "Inteligencia Artificial", "x": 200, "y": 150},
                {"id": f"{map_id}_concept_2", "name": "Machine Learning", "x": 400, "y": 100},
                {"id": f"{map_id}_concept_3", "name": "Deep Learning", "x": 600, "y": 150},
                {"id": f"{map_id}_concept_4", "name": "Redes Neuronales", "x": 400, "y": 250},
                {"id": f"{map_id}_concept_5", "name": "Algoritmos", "x": 200, "y": 300}
            ]
            
            for concept in concepts:
                tx.run("""
                    MERGE (node:ConceptNode {id: $id})
                    SET node.name = $name, node.x = $x, node.y = $y, node.type = 'concept'
                """, id=concept["id"], name=concept["name"], x=concept["x"], y=concept["y"])
                
                # Vincular cada nodo al mapa conceptual
                tx.run("""
                    MATCH (cm:ConceptMap {id: $map_id})
                    MATCH (node:ConceptNode {id: $node_id})
                    MERGE (cm)-[:CONTAINS]->(node)
                """, map_id=map_id, node_id=concept["id"])
            
            # Crear relaciones entre nodos
            relations = [
                {"from": f"{map_id}_concept_1", "to": f"{map_id}_concept_2", "type": "includes"},
                {"from": f"{map_id}_concept_2", "to": f"{map_id}_concept_3", "type": "includes"},
                {"from": f"{map_id}_concept_3", "to": f"{map_id}_concept_4", "type": "uses"},
                {"from": f"{map_id}_concept_2", "to": f"{map_id}_concept_5", "type": "uses"}
            ]
            
            for relation in relations:
                tx.run("""
                    MATCH (from:ConceptNode {id: $from_id})
                    MATCH (to:ConceptNode {id: $to_id})
                    MERGE (from)-[:RELATES_TO {type: $rel_type}]->(to)
                """, from_id=relation["from"], to_id=relation["to"], rel_type=relation["type"])

            logger.info(f"Mapa de prueba '{name}' creado con 5 conceptos y 4 relaciones para el usuario {user_id}.")
            tx.commit()
        except Exception as e:
            logger.error(f"Error al crear datos de prueba: {e}")
            tx.rollback()

if __name__ == "__main__":
    # --- IMPORTANTE: CAMBIA ESTOS VALORES --- #
    TEST_USER_ID = 3  # Reemplaza con un user_id válido de tu BD
    TEST_NOTE_ID = 36 # Reemplaza con un note_id válido de tu BD
    TEST_NOTE_TITLE = "Nota de Prueba para Mapa"
    # ----------------------------------------- #

    neo4j_driver = get_neo4j_driver()
    if neo4j_driver:
        create_test_data(neo4j_driver, TEST_USER_ID, TEST_NOTE_ID, TEST_NOTE_TITLE)
        neo4j_driver.close()
        logger.info("Script de prueba finalizado.")
