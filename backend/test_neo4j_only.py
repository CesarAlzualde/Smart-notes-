"""
Script de prueba SOLO Neo4j - Sin dependencias de IA
Prueba únicamente la conexión y operaciones básicas en Neo4j
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Cargar variables de entorno
load_dotenv()

def test_neo4j_connection():
    """Prueba conexión básica a Neo4j"""
    try:
        print("=== PRUEBA CONEXIÓN NEO4J ===")
        
        # Configuración desde variables de entorno
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
        
        print(f"URI: {NEO4J_URI}")
        print(f"Usuario: {NEO4J_USER}")
        print(f"Contraseña: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else '(vacía)'}")
        
        # Crear driver
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=10.0
        )
        
        # Probar conexión
        with driver.session() as session:
            result = session.run("RETURN 'Conexión exitosa' AS message, datetime() AS timestamp")
            record = result.single()
            
            if record:
                print(f"✓ {record['message']}")
                print(f"✓ Timestamp: {record['timestamp']}")
                
                # Prueba de escritura/lectura
                session.run("MERGE (test:TestConnection {id: 'test-123', name: 'Prueba Neo4j'})")
                
                result = session.run("MATCH (test:TestConnection {id: 'test-123'}) RETURN test.name AS name")
                record = result.single()
                
                if record:
                    print(f"✓ Escritura/Lectura exitosa: {record['name']}")
                    
                    # Limpiar
                    session.run("MATCH (test:TestConnection {id: 'test-123'}) DELETE test")
                    print("✓ Limpieza exitosa")
                    
                    driver.close()
                    return True
                else:
                    print("✗ Fallo en escritura/lectura")
                    return False
            else:
                print("✗ Sin respuesta del servidor")
                return False
                
    except Exception as e:
        print(f"✗ Error de conexión: {str(e)}")
        return False


def test_concept_map_schema():
    """Prueba crear esquema básico para mapas conceptuales"""
    try:
        print("\n=== PRUEBA ESQUEMA MAPAS CONCEPTUALES ===")
        
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
        
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=10.0
        )
        
        with driver.session() as session:
            # Limpiar datos de prueba previos
            session.run("MATCH (n:TestMap) DETACH DELETE n")
            session.run("MATCH (n:TestNode) DETACH DELETE n")
            print("✓ Limpieza inicial")
            
            # Crear mapa conceptual
            session.run("""
                CREATE (map:TestMap {
                    id: 'map-123',
                    name: 'Mapa de Prueba',
                    user_id: 'user-456',
                    created_at: datetime(),
                    metadata: '{"description": "Prueba de concepto"}'
                })
            """)
            print("✓ Mapa conceptual creado")
            
            # Crear nodos conceptuales
            session.run("""
                CREATE (node1:TestNode {
                    id: 'node-1',
                    label: 'Concepto Central',
                    type: 'central',
                    properties: '{"importance": "high", "color": "#FF6B6B"}',
                    x: 0.5,
                    y: 0.5,
                    size: 20
                })
            """)
            
            session.run("""
                CREATE (node2:TestNode {
                    id: 'node-2', 
                    label: 'Concepto Secundario',
                    type: 'secondary',
                    properties: '{"importance": "medium", "color": "#4ECDC4"}',
                    x: 0.2,
                    y: 0.8,
                    size: 15
                })
            """)
            print("✓ Nodos conceptuales creados")
            
            # Relacionar mapa con nodos
            session.run("""
                MATCH (map:TestMap {id: 'map-123'})
                MATCH (node1:TestNode {id: 'node-1'})
                MATCH (node2:TestNode {id: 'node-2'})
                CREATE (map)-[:CONTAINS]->(node1)
                CREATE (map)-[:CONTAINS]->(node2)
            """)
            print("✓ Relaciones mapa-nodos creadas")
            
            # Crear relación entre nodos
            session.run("""
                MATCH (node1:TestNode {id: 'node-1'})
                MATCH (node2:TestNode {id: 'node-2'})
                CREATE (node1)-[:RELATES_TO {
                    id: 'edge-1',
                    label: 'incluye',
                    type: 'semantic',
                    properties: '{"strength": 0.8}'
                }]->(node2)
            """)
            print("✓ Relación entre nodos creada")
            
            # Consultar estructura completa
            result = session.run("""
                MATCH (map:TestMap {id: 'map-123'})
                OPTIONAL MATCH (map)-[:CONTAINS]->(node:TestNode)
                OPTIONAL MATCH (node)-[rel:RELATES_TO]->(target:TestNode)
                RETURN map,
                       collect(DISTINCT node) as nodes,
                       collect(DISTINCT {
                           id: rel.id,
                           label: rel.label,
                           type: rel.type,
                           source: startNode(rel).id,
                           target: endNode(rel).id,
                           properties: rel.properties
                       }) as edges
            """)
            
            record = result.single()
            if record:
                map_data = record['map']
                nodes = record['nodes']
                edges = [e for e in record['edges'] if e['id']]  # Filtrar nulos
                
                print(f"✓ Mapa recuperado: '{map_data['name']}'")
                print(f"  - ID: {map_data['id']}")
                print(f"  - Usuario: {map_data['user_id']}")
                print(f"  - Nodos: {len(nodes)}")
                print(f"  - Conexiones: {len(edges)}")
                
                # Mostrar nodos
                for node in nodes:
                    print(f"    * Nodo: {node['label']} ({node['type']}) - Pos: ({node['x']}, {node['y']})")
                
                # Mostrar conexiones
                for edge in edges:
                    print(f"    * Conexión: {edge['source']} --[{edge['label']}]--> {edge['target']}")
                
                # Limpiar
                session.run("MATCH (n:TestMap) DETACH DELETE n")
                session.run("MATCH (n:TestNode) DETACH DELETE n")
                print("✓ Limpieza final")
                
                driver.close()
                return True
            else:
                print("✗ No se pudo recuperar el mapa")
                return False
                
    except Exception as e:
        print(f"✗ Error en esquema: {str(e)}")
        return False


def test_concept_map_queries():
    """Prueba consultas típicas para mapas conceptuales"""
    try:
        print("\n=== PRUEBA CONSULTAS MAPAS CONCEPTUALES ===")
        
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
        
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=10.0
        )
        
        with driver.session() as session:
            # Crear datos de prueba múltiples
            session.run("MATCH (n:QueryTest) DETACH DELETE n")
            
            # Crear varios mapas para un usuario
            for i in range(3):
                session.run(f"""
                    CREATE (map:QueryTest {{
                        id: 'map-{i+1}',
                        name: 'Mapa {i+1}',
                        user_id: 'user-123',
                        created_at: datetime(),
                        type: 'ConceptMap'
                    }})
                """)
            print("✓ Datos de prueba creados")
            
            # Consulta 1: Obtener mapas de un usuario
            result = session.run("""
                MATCH (map:QueryTest {user_id: 'user-123', type: 'ConceptMap'})
                RETURN map.id as id, map.name as name, map.created_at as created_at
                ORDER BY map.created_at DESC
            """)
            
            maps = list(result)
            print(f"✓ Consulta mapas usuario: {len(maps)} mapas encontrados")
            for map_record in maps:
                print(f"    - {map_record['name']} ({map_record['id']})")
            
            # Consulta 2: Obtener mapa específico por ID
            result = session.run("""
                MATCH (map:QueryTest {id: 'map-2'})
                RETURN map.id as id, map.name as name
            """)
            
            record = result.single()
            if record:
                print(f"✓ Consulta mapa específico: '{record['name']}' encontrado")
            else:
                print("✗ No se encontró mapa específico")
                return False
            
            # Consulta 3: Contar mapas por usuario
            result = session.run("""
                MATCH (map:QueryTest {user_id: 'user-123'})
                RETURN count(map) as total
            """)
            
            record = result.single()
            if record:
                print(f"✓ Conteo mapas: {record['total']} mapas totales")
            
            # Limpiar
            session.run("MATCH (n:QueryTest) DETACH DELETE n")
            print("✓ Limpieza final")
            
            driver.close()
            return True
            
    except Exception as e:
        print(f"✗ Error en consultas: {str(e)}")
        return False


def main():
    """Ejecutar todas las pruebas de Neo4j"""
    print("🧪 PRUEBAS NEO4J - MAPAS CONCEPTUALES")
    print("=" * 40)
    
    # Prueba 1: Conexión básica
    connection_ok = test_neo4j_connection()
    
    # Prueba 2: Esquema de mapas conceptuales
    schema_ok = False
    if connection_ok:
        schema_ok = test_concept_map_schema()
    else:
        print("\n⚠️ Saltando prueba de esquema por fallo de conexión")
    
    # Prueba 3: Consultas
    queries_ok = False
    if connection_ok:
        queries_ok = test_concept_map_queries()
    else:
        print("\n⚠️ Saltando prueba de consultas por fallo de conexión")
    
    # Resumen
    print("\n" + "=" * 40)
    print("📊 RESUMEN:")
    print(f"  Conexión Neo4j: {'✓ OK' if connection_ok else '✗ FALLO'}")
    print(f"  Esquema mapas: {'✓ OK' if schema_ok else '✗ FALLO'}")
    print(f"  Consultas: {'✓ OK' if queries_ok else '✗ FALLO'}")
    
    if connection_ok and schema_ok and queries_ok:
        print("\n🎉 NEO4J COMPLETAMENTE FUNCIONAL")
        print("✓ Listo para mapas conceptuales")
        return True
    else:
        print("\n❌ PROBLEMAS DETECTADOS EN NEO4J")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Error fatal: {str(e)}")
        exit(1)
