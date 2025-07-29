#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para añadir datos de ejemplo al grafo Neo4j para la visualización
"""

from knowledge_graph import KnowledgeGraph
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de Neo4j
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

def test_connection():
    """Prueba la conexión a Neo4j"""
    try:
        logging.info(f"Intentando conectar a Neo4j en: {NEO4J_URI}")
        logging.info(f"Usuario: {NEO4J_USER}")
        
        kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        logging.info("✅ Conexión a Neo4j exitosa!")
        return kg
    except Exception as e:
        logging.error(f"❌ Error al conectar a Neo4j: {e}")
        return None

def add_sample_data(kg):
    """Añade datos de muestra al grafo"""
    try:
        # Añadir conceptos principales con categorías
        kg.add_concept('Inteligencia Artificial', {'category': 'technology', 'importance': 'high'})
        logging.info("Añadido concepto: Inteligencia Artificial")
        
        kg.add_concept('Machine Learning', {'category': 'technology', 'importance': 'high'})
        logging.info("Añadido concepto: Machine Learning")
        
        kg.add_concept('Deep Learning', {'category': 'technology', 'importance': 'medium'})
        logging.info("Añadido concepto: Deep Learning")
        
        kg.add_concept('Python', {'category': 'technology', 'importance': 'high'})
        logging.info("Añadido concepto: Python")
        
        kg.add_concept('Neurociencia', {'category': 'science', 'importance': 'medium'})
        logging.info("Añadido concepto: Neurociencia")
        
        kg.add_concept('Estadística', {'category': 'mathematics', 'importance': 'high'})
        logging.info("Añadido concepto: Estadística")
        
        kg.add_concept('Visión por Computadora', {'category': 'technology', 'importance': 'medium'})
        logging.info("Añadido concepto: Visión por Computadora")
        
        kg.add_concept('Historia de la IA', {'category': 'history', 'importance': 'low'})
        logging.info("Añadido concepto: Historia de la IA")
        
        # Añadir relaciones
        kg.add_relation('Machine Learning', 'Inteligencia Artificial', 'ES_PARTE_DE')
        logging.info("Añadida relación: Machine Learning ES_PARTE_DE Inteligencia Artificial")
        
        kg.add_relation('Deep Learning', 'Machine Learning', 'ES_TIPO_DE')
        logging.info("Añadida relación: Deep Learning ES_TIPO_DE Machine Learning")
        
        kg.add_relation('Python', 'Machine Learning', 'SE_USA_EN')
        logging.info("Añadida relación: Python SE_USA_EN Machine Learning")
        
        kg.add_relation('Estadística', 'Machine Learning', 'ES_BASE_DE')
        logging.info("Añadida relación: Estadística ES_BASE_DE Machine Learning")
        
        kg.add_relation('Neurociencia', 'Deep Learning', 'INSPIRA')
        logging.info("Añadida relación: Neurociencia INSPIRA Deep Learning")
        
        kg.add_relation('Visión por Computadora', 'Deep Learning', 'UTILIZA')
        logging.info("Añadida relación: Visión por Computadora UTILIZA Deep Learning")
        
        kg.add_relation('Historia de la IA', 'Inteligencia Artificial', 'CONTEXTUALIZA')
        logging.info("Añadida relación: Historia de la IA CONTEXTUALIZA Inteligencia Artificial")
        
        # Verificar datos añadidos
        concepts = kg.get_all_concepts()
        logging.info(f"Total de conceptos en la base de datos: {len(concepts)}")
        
        # Obtener datos para visualización
        graph_data = kg.get_graph_data()
        logging.info(f"Datos para visualización: {len(graph_data['nodes'])} nodos, {len(graph_data['links'])} enlaces")
        
        return True
    except Exception as e:
        logging.error(f"❌ Error al añadir datos de muestra: {e}")
        return False

if __name__ == "__main__":
    kg = test_connection()
    if kg:
        logging.info("Añadiendo datos de muestra al grafo...")
        add_sample_data(kg)
        kg.close()
        logging.info("✅ Script completado. Ahora puedes visitar http://localhost:8000/graph para ver la visualización.")
    else:
        logging.error("❌ No se pudo completar el script debido a problemas de conexión.")
