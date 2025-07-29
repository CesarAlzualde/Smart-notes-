"""
Script de prueba ligero para mapas conceptuales - solo Neo4j
Sin cargar modelos pesados de IA
"""

import os
import sys
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el path para importar la app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_neo4j_basic():
    """Prueba básica de Neo4j sin Flask context"""
    try:
        from app.api.health import get_neo4j_driver
        
        print("=== PRUEBA BÁSICA DE NEO4J ===")
        
        # Obtener configuración
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
        
        print(f"URI: {NEO4J_URI}")
        print(f"Usuario: {NEO4J_USER}")
        print(f"Contraseña: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else '(vacía)'}")
        
        from neo4j import GraphDatabase
        
        # Conexión directa sin usar Flask
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=10.0
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j conectado' AS message")
            record = result.single()
            if record:
                print(f"✓ {record['message']}")
                
                # Limpiar datos de prueba previos
                session.run("MATCH (n:TestNode) DETACH DELETE n")
                print("✓ Limpieza de datos de prueba")
                
                # Crear nodo de prueba
                session.run("""
                    CREATE (n:TestNode {
                        id: 'test-123',
                        name: 'Nodo de Prueba',
                        type: 'test'
                    })
                """)
                print("✓ Nodo de prueba creado")
                
                # Consultar nodo
                result = session.run("MATCH (n:TestNode {id: 'test-123'}) RETURN n")
                record = result.single()
                if record:
                    print("✓ Nodo recuperado correctamente")
                    node = record['n']
                    print(f"  - ID: {node['id']}")
                    print(f"  - Nombre: {node['name']}")
                else:
                    print("✗ No se pudo recuperar el nodo")
                    return False
                
                # Limpiar
                session.run("MATCH (n:TestNode) DETACH DELETE n")
                print("✓ Limpieza final exitosa")
                
                driver.close()
                return True
                
        return False
        
    except Exception as e:
        print(f"✗ Error en prueba Neo4j: {str(e)}")
        return False


def test_concept_map_structure():
    """Prueba la estructura básica del servicio de mapas conceptuales"""
    try:
        print("\n=== PRUEBA DE ESTRUCTURA DE MAPAS CONCEPTUALES ===")
        
        # Importar clases sin inicializar servicios pesados
        from app.services.enhanced_concept_map_service import ConceptNode, ConceptEdge, ConceptMap
        
        # Crear nodo de prueba
        test_node = ConceptNode(
            id="node-1",
            label="Nodo Central",
            type="central",
            properties={"test": True},
            color="#FF6B6B",
            size=20,
            x=0.0,
            y=0.0
        )
        print(f"✓ Nodo creado: {test_node.label}")
        
        # Crear conexión de prueba
        test_edge = ConceptEdge(
            id="edge-1", 
            source="node-1",
            target="node-2",
            label="conecta_con",
            type="connects",
            properties={"strength": 0.8}
        )
        print(f"✓ Conexión creada: {test_edge.label}")
        
        # Crear mapa conceptual
        test_map = ConceptMap(
            id="map-123",
            name="Mapa de Prueba",
            nodes=[test_node],
            edges=[test_edge],
            metadata={"created_by": "test", "version": "1.0"}
        )
        print(f"✓ Mapa conceptual creado: {test_map.name}")
        print(f"  - Nodos: {len(test_map.nodes)}")
        print(f"  - Conexiones: {len(test_map.edges)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en estructura de mapas: {str(e)}")
        return False


def test_neo4j_concept_map_operations():
    """Prueba operaciones básicas de mapas conceptuales en Neo4j"""
    try:
        print("\n=== PRUEBA DE OPERACIONES MAPAS CONCEPTUALES ===")
        
        from neo4j import GraphDatabase
        
        # Configuración Neo4j
        NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
        
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=10.0
        )
        
        with driver.session() as session:
            # Limpiar datos de prueba
            session.run("MATCH (n:TestConceptMap) DETACH DELETE n")
            session.run("MATCH (n:TestConceptNode) DETACH DELETE n")
            print("✓ Limpieza inicial")
            
            # Crear mapa conceptual de prueba
            session.run("""
                CREATE (cm:TestConceptMap {
                    id: 'test-map-123',
                    name: 'Mapa de Prueba Neo4j',
                    created_at: datetime()
                })
            """)
            print("✓ Mapa conceptual creado en Neo4j")
            
            # Crear nodos conceptuales
            session.run("""
                CREATE (n1:TestConceptNode {
                    id: 'node-central',
                    label: 'Idea Central',
                    type: 'central',
                    properties: '{"importance": "high"}',
                    color: '#FF6B6B',
                    size: 20
                })
            """)
            
            session.run("""
                CREATE (n2:TestConceptNode {
                    id: 'node-topic',
                    label: 'Tema Relacionado', 
                    type: 'topic',
                    properties: '{"category": "academic"}',
                    color: '#4ECDC4',
                    size: 15
                })
            """)
            print("✓ Nodos conceptuales creados")
            
            # Conectar mapa con nodos
            session.run("""
                MATCH (cm:TestConceptMap {id: 'test-map-123'})
                MATCH (n1:TestConceptNode {id: 'node-central'})
                MATCH (n2:TestConceptNode {id: 'node-topic'})
                CREATE (cm)-[:CONTAINS]->(n1)
                CREATE (cm)-[:CONTAINS]->(n2)
                CREATE (n1)-[:RELATES_TO {label: 'incluye', type: 'semantic'}]->(n2)
            """)
            print("✓ Relaciones creadas")
            
            # Consultar el mapa completo
            result = session.run("""
                MATCH (cm:TestConceptMap {id: 'test-map-123'})
                OPTIONAL MATCH (cm)-[:CONTAINS]->(node:TestConceptNode)
                OPTIONAL MATCH (node)-[rel:RELATES_TO]->(target:TestConceptNode)
                RETURN cm, 
                       collect(DISTINCT node) as nodes,
                       collect(DISTINCT {rel: rel, source: startNode(rel), target: endNode(rel)}) as relations
            """)
            
            record = result.single()
            if record:
                concept_map = record['cm']
                nodes = record['nodes']
                relations = record['relations']
                
                print(f"✓ Mapa recuperado: {concept_map['name']}")
                print(f"  - Nodos encontrados: {len(nodes)}")
                print(f"  - Relaciones encontradas: {len([r for r in relations if r['rel']])}")
                
                # Mostrar detalles
                for node in nodes:
                    print(f"    * {node['label']} ({node['type']})")
                
            else:
                print("✗ No se pudo recuperar el mapa")
                return False
            
            # Limpiar datos de prueba
            session.run("MATCH (n:TestConceptMap) DETACH DELETE n")
            session.run("MATCH (n:TestConceptNode) DETACH DELETE n")
            print("✓ Limpieza final")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"✗ Error en operaciones Neo4j: {str(e)}")
        return False


def main():
    """Ejecutar pruebas ligeras"""
    print("🧪 PRUEBAS LIGERAS - MÓDULO MAPAS CONCEPTUALES")
    print("=" * 50)
    
    # Prueba 1: Neo4j básico
    neo4j_ok = test_neo4j_basic()
    
    # Prueba 2: Estructura de clases
    structure_ok = test_concept_map_structure()
    
    # Prueba 3: Operaciones Neo4j para mapas conceptuales
    operations_ok = False
    if neo4j_ok:
        operations_ok = test_neo4j_concept_map_operations()
    else:
        print("\n⚠️ Saltando operaciones Neo4j por fallo en conexión básica")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")
    print(f"  Neo4j básico: {'✓ OK' if neo4j_ok else '✗ FALLO'}")
    print(f"  Estructura clases: {'✓ OK' if structure_ok else '✗ FALLO'}")
    print(f"  Operaciones Neo4j: {'✓ OK' if operations_ok else '✗ FALLO'}")
    
    if neo4j_ok and structure_ok and operations_ok:
        print("\n🎉 PRUEBAS BÁSICAS EXITOSAS")
        print("El módulo de mapas conceptuales tiene la infraestructura correcta")
        return True
    else:
        print("\n❌ FALLOS DETECTADOS")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Error fatal: {str(e)}")
        sys.exit(1)
