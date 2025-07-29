import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions

# Añadir el directorio raíz del backend al path para importar módulos de la aplicación
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cargar variables de entorno desde el archivo .env en la raíz del backend
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jMigrator:
    def __init__(self, uri, user, password):
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
            print("Conexión a Neo4j establecida correctamente.")
        except exceptions.AuthError as e:
            print(f"Error de autenticación en Neo4j: {e}. Revisa las credenciales en tu archivo .env.")
            self._driver = None
        except Exception as e:
            print(f"No se pudo conectar a Neo4j: {e}")
            self._driver = None

    def close(self):
        if self._driver is not None:
            self._driver.close()
            print("Conexión a Neo4j cerrada.")

    def migrate_user_ids_to_integer(self):
        if not self._driver:
            return

        with self._driver.session() as session:
            count_query = """
            MATCH (cm:ConceptMap)
            WHERE toString(cm.user_id) = cm.user_id
            RETURN count(cm) AS count
            """
            count_result = session.run(count_query).single()
            count = count_result["count"] if count_result else 0
            print(f"Se encontraron {count} nodos de ConceptMap con user_id como string para migrar.")

            if count == 0:
                print("No se necesita migración.")
                return

            migration_query = """
            MATCH (cm:ConceptMap)
            WHERE toString(cm.user_id) = cm.user_id
            SET cm.user_id = toInteger(cm.user_id)
            RETURN count(cm) AS migrated_count
            """
            migration_result = session.run(migration_query).single()
            migrated_count = migration_result["migrated_count"] if migration_result else 0
            print(f"Se migraron exitosamente {migrated_count} user_ids a enteros.")

if __name__ == "__main__":
    if not NEO4J_PASSWORD:
        print("Error: La variable de entorno NEO4J_PASSWORD no se encontró. Asegúrate de que esté en el archivo .env.")
    else:
        migrator = Neo4jMigrator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        if migrator._driver:
            migrator.migrate_user_ids_to_integer()
            migrator.close()
