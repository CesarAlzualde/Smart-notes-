import json
import logging
import os
from neo4j import GraphDatabase, exceptions

class Neo4jService:
    """
    Servicio para gestionar la conexion y las operaciones con la base de datos Neo4j.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jService, cls).__new__(cls)
            cls._instance._driver = None
            try:
                # Cargar configuracion desde db_config.json
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'db_config.json')
                with open(config_path) as config_file:
                    config = json.load(config_file)['neo4j']
                
                uri = config['uri']
                user = config['user']
                password = config['password']
                
                cls._instance._driver = GraphDatabase.driver(uri, auth=(user, password))
                logging.info("Conexion con Neo4j establecida exitosamente.")
            except FileNotFoundError:
                logging.error("El archivo de configuracion 'db_config.json' no se encontro.")
            except exceptions.AuthError:
                logging.error("Error de autenticacion con Neo4j. Revisa las credenciales.")
            except Exception as e:
                logging.error(f"No se pudo conectar a Neo4j: {e}")
        return cls._instance

    def close(self):
        """Cierra la conexion con la base de datos."""
        if self._driver is not None:
            self._driver.close()
            logging.info("Conexion con Neo4j cerrada.")

    def execute_query(self, query, parameters=None):
        """
        Ejecuta una consulta Cypher en la base de datos.

        :param query: La consulta Cypher a ejecutar.
        :param parameters: Un diccionario de parametros para la consulta.
        :return: Una lista de resultados o None si hay un error.
        """
        if self._driver is None:
            logging.error("No hay driver de Neo4j disponible. La consulta no se puede ejecutar.")
            return None
            
        with self._driver.session() as session:
            try:
                result = session.run(query, parameters)
                # Convertir los resultados a un formato de lista de diccionarios
                return [record.data() for record in result]
            except exceptions.ServiceUnavailable:
                logging.error("El servicio de Neo4j no esta disponible.")
                return None
            except Exception as e:
                logging.error(f"Error al ejecutar la consulta Cypher: {e}")
                return None

# Singleton instance para ser usada en la aplicacion
neo4j_service = Neo4jService()

