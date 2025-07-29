import json
import os
from neo4j import GraphDatabase

# Cargar la configuración de Neo4j
config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'db_config.json')
with open(config_path) as config_file:
    config = json.load(config_file)['neo4j']

uri = config['uri']
user = config['user']
password = config['password']

# Conectar a Neo4j
driver = GraphDatabase.driver(uri, auth=(user, password))

# Crear el nodo ConceptMap con id "filter"
with driver.session() as session:
    # Verificar si ya existe
    result = session.run("MATCH (m:ConceptMap {id: 'filter'}) RETURN m")
    if result.single() is None:
        # Crear el nodo si no existe
        session.run("""
        CREATE (m:ConceptMap {
            id: 'filter',
            name: 'Filter Concept Map',
            description: 'Map for filtered view of concepts',
            created_at: datetime()
        })
        RETURN m
        """)
        print("✅ Nodo ConceptMap con id 'filter' creado exitosamente")
    else:
        print("⚠️ El nodo ConceptMap con id 'filter' ya existe")

    # Opcional: Crear algunos nodos Concept y relaciones para pruebas
    session.run("""
    MATCH (m:ConceptMap {id: 'filter'})
    MERGE (c1:Concept {id: 'c1', name: 'Concepto 1', type: 'main'})
    MERGE (c2:Concept {id: 'c2', name: 'Concepto 2', type: 'secondary'})
    MERGE (c3:Concept {id: 'c3', name: 'Concepto 3', type: 'detail'})
    MERGE (m)-[:HAS_NODE]->(c1)
    MERGE (m)-[:HAS_NODE]->(c2)
    MERGE (m)-[:HAS_NODE]->(c3)
    MERGE (c1)-[:RELATED_TO {strength: 0.8}]->(c2)
    MERGE (c2)-[:RELATED_TO {strength: 0.6}]->(c3)
    """)
    print("✅ Nodos Concept y relaciones creados para el mapa 'filter'")

# Cerrar el driver
driver.close()

print("✅ Script completado. Ahora la aplicación debería poder encontrar el mapa conceptual 'filter'.")
