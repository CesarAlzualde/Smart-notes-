"""
Script para probar la conexión a Neo4j y diagnosticar problemas de autenticación
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

print("Configuración Neo4j:")
print(f"URI: {NEO4J_URI}")
print(f"Usuario: {NEO4J_USER}")
print(f"Contraseña: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else '(vacía)'}")
print()

try:
    from neo4j import GraphDatabase
    print("✓ Driver de Neo4j importado correctamente")
    
    # Intentar conexión
    print(f"Intentando conectar a {NEO4J_URI}...")
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        connection_timeout=10.0
    )
    
    # Probar la conexión
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        if record and record["test"] == 1:
            print("✓ Conexión a Neo4j exitosa!")
        else:
            print("✗ Error: No se pudo obtener resultado de la consulta")
    
    # Verificar versión
    with driver.session() as session:
        result = session.run("CALL dbms.components() YIELD name, versions, edition")
        for record in result:
            print(f"Neo4j {record['name']}: {record['versions'][0]} ({record['edition']})")
    
    driver.close()
    
except ImportError as e:
    print(f"✗ Error importando Neo4j: {e}")
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    print(f"Tipo de error: {type(e).__name__}")
    
    # Diagnosticar problemas comunes
    if "authentication failure" in str(e).lower():
        print("\n🔍 DIAGNÓSTICO: Error de autenticación")
        print("- Verifica que la contraseña sea correcta")
        print("- Verifica que el usuario 'neo4j' existe")
        print("- Considera reiniciar Neo4j Desktop")
    elif "connection refused" in str(e).lower():
        print("\n🔍 DIAGNÓSTICO: Conexión rechazada")
        print("- Verifica que Neo4j esté ejecutándose")
        print("- Verifica que esté escuchando en el puerto 7687")
    elif "timeout" in str(e).lower():
        print("\n🔍 DIAGNÓSTICO: Timeout de conexión")
        print("- Neo4j puede estar sobrecargado o tardando en responder")
