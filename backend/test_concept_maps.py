"""
Script de prueba para el módulo de mapas conceptuales
Prueba directamente el EnhancedConceptMapService sin servidor web
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

def test_neo4j_connection():
    """Prueba la conexión a Neo4j usando la función del health.py"""
    try:
        from app.api.health import get_neo4j_driver
        
        print("=== PRUEBA DE CONEXIÓN NEO4J ===")
        driver = get_neo4j_driver()
        
        if driver is None:
            print("✗ No se pudo obtener driver de Neo4j")
            return False
        
        # Probar consulta básica
        with driver.session() as session:
            result = session.run("RETURN 'Conexión exitosa' AS message")
            record = result.single()
            if record:
                print(f"✓ {record['message']}")
                return True
            else:
                print("✗ No se recibió respuesta de Neo4j")
                return False
                
    except Exception as e:
        print(f"✗ Error probando Neo4j: {str(e)}")
        return False

def test_enhanced_service(app):
    """Prueba el EnhancedConceptMapService"""
    try:
        from app.services.enhanced_concept_map_service import EnhancedConceptMapService
        from app.database import get_session
        from app.models.note import Note
        
        print("\n=== PRUEBA DE ENHANCED SERVICE ===")
        
        with app.app_context():
            # Crear instancia del servicio
            service = EnhancedConceptMapService()
            print("✓ Servicio creado correctamente")
            
            # Buscar una nota existente para probar
            with get_session() as session:
                note = session.query(Note).first()
                if not note:
                    print("✗ No hay notas en la base de datos para probar")
                    return False
                    
                print(f"✓ Usando nota: {note.title} (ID: {note.id})")
                
                # Probar generación de mapa conceptual
                try:
                    concept_map = service.generate_automatic_map_from_note(note.id)
                    print(f"✓ Mapa conceptual generado: {concept_map.name}")
                    print(f"  - Nodos: {len(concept_map.nodes)}")
                    print(f"  - Conexiones: {len(concept_map.edges)}")
                    
                    # Probar conversión a formato API
                    api_format = service.convert_to_api_format(concept_map)
                    print("✓ Convertido a formato API correctamente")
                    
                    # Probar guardado en Neo4j
                    try:
                        service.save_concept_map(concept_map, note.id)
                        print("✓ Mapa guardado en Neo4j")
                        
                        # Probar recuperación por ID
                        retrieved = service.get_concept_map_by_id(concept_map.id, note.user_id)
                        if retrieved and not retrieved.get('error'):
                            print("✓ Mapa recuperado correctamente desde Neo4j")
                            return True
                        else:
                            print(f"✗ Error recuperando mapa: {retrieved.get('error') if retrieved else 'Sin respuesta'}")
                            return False
                            
                    except Exception as e:
                        print(f"✗ Error guardando/recuperando mapa: {str(e)}")
                        return False
                        
                except Exception as e:
                    print(f"✗ Error generando mapa conceptual: {str(e)}")
                    return False
                
    except Exception as e:
        print(f"✗ Error probando Enhanced Service: {str(e)}")
        return False

def test_database_connection(app):
    """Prueba la conexión a la base de datos principal"""
    try:
        from app.database import get_session
        from app.models.note import Note
        
        print("\n=== PRUEBA DE BASE DE DATOS ===")
        
        with app.app_context():
            with get_session() as session:
                count = session.query(Note).count()
                print(f"✓ Conexión a PostgreSQL exitosa - {count} notas encontradas")
                return True
            
    except Exception as e:
        print(f"✗ Error conectando a base de datos: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL MÓDULO DE MAPAS CONCEPTUALES")
    print("=" * 60)
    
    # Crear aplicación Flask para contexto
    try:
        from app import create_app
        app = create_app()
        print("✓ Aplicación Flask creada correctamente")
    except Exception as e:
        print(f"✗ Error creando aplicación Flask: {str(e)}")
        return False
    
    # Prueba 1: Base de datos
    db_ok = test_database_connection(app)
    
    # Prueba 2: Neo4j
    neo4j_ok = test_neo4j_connection()
    
    # Prueba 3: Enhanced Service (solo si las anteriores pasan)
    service_ok = False
    if db_ok and neo4j_ok:
        service_ok = test_enhanced_service(app)
    else:
        print("\n⚠️  Saltando prueba de Enhanced Service debido a fallos previos")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  Base de datos PostgreSQL: {'✓ OK' if db_ok else '✗ FALLO'}")
    print(f"  Conexión Neo4j: {'✓ OK' if neo4j_ok else '✗ FALLO'}")
    print(f"  Enhanced Service: {'✓ OK' if service_ok else '✗ FALLO'}")
    
    if db_ok and neo4j_ok and service_ok:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - El módulo de mapas conceptuales está funcionando")
        return True
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - Revisar errores anteriores")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Error fatal: {str(e)}")
        sys.exit(1)
