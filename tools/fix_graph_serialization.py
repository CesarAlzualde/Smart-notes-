import os
import json
from neo4j import GraphDatabase

# Cargar configuración de Neo4j
with open('backend/config/db_config.json') as f:
    config = json.load(f)['neo4j']

# Conectar a Neo4j
driver = GraphDatabase.driver(config['uri'], auth=(config['user'], config['password']))

def update_map_node():
    """Actualiza el nodo ConceptMap para que no tenga el campo DateTime problemático."""
    with driver.session() as session:
        # Actualizar el nodo para usar un string en lugar de DateTime
        result = session.run("""
        MATCH (m:ConceptMap {id: 'filter'})
        SET m.created_at = toString(m.created_at)
        RETURN m
        """)
        print("ConceptMap actualizado:", result.single() is not None)

        # Mostrar todas las propiedades del nodo
        result = session.run("""
        MATCH (m:ConceptMap {id: 'filter'}) 
        RETURN properties(m) as props
        """)
        record = result.single()
        print("Propiedades del nodo ConceptMap:")
        if record:
            print(json.dumps(dict(record["props"]), indent=2))
        else:
            print("No se encontró el nodo")

if __name__ == "__main__":
    print("Ejecutando script para corregir la serialización del grafo...")
    update_map_node()
    driver.close()
    print("Script completado.")
