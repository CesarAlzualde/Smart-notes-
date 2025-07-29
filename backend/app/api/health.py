"""
Health check API para verificar el estado de los componentes del sistema.
"""
import logging
import os
from flask import Blueprint, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Intentar importar Neo4j si está disponible
try:
    from neo4j import GraphDatabase
    neo4j_available = True
except ImportError:
    neo4j_available = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para health checks
health_bp = Blueprint('health', __name__)

# Flag para indicar si la base de datos ya se inicializó
db_initialized = False

# Variables de conexión Neo4j - Cargadas desde variables de entorno
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
NEO4J_TIMEOUT = float(os.environ.get("NEO4J_TIMEOUT", "5.0"))  # timeout en segundos
NEO4J_DISABLED = os.environ.get("NEO4J_DISABLED", "False").lower() == "true"

# Contador de intentos de conexión a Neo4j (para limitar mensajes de error)
_neo4j_connection_attempts = 0

@health_bp.route('/init-db', methods=['GET'])
def init_db():
    """
    Endpoint para inicializar la base de datos.
    Crea todas las tablas necesarias si no existen.
    """
    global db_initialized
    try:
        if not db_initialized:
            logger.info("Intentando inicializar la base de datos...")
            db.create_all()
            db_initialized = True
            logger.info("Base de datos inicializada correctamente")
            return jsonify({"status": "success", "message": "Base de datos inicializada correctamente"})
        else:
            return jsonify({"status": "success", "message": "Base de datos ya inicializada previamente"})
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@health_bp.route('', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado de los componentes del sistema.
    Devuelve un resumen del estado de los servicios principales.
    """
    health_data = {
        "status": "ok",
        "services": {
            "api": "available",
            "database": "unknown",
            "neo4j": "unknown",
            "summarizer": "unknown",  
            "classifier": "unknown"   
        }
    }
    
    # Verificar modelos si están disponibles
    from ..services.text_summarizer import TextSummarizer
    from ..services.topic_classifier import NlpAnalyser

    summarizer_status = "unavailable"
    classifier_status = "unavailable"
    
    try:
        # Verificar status de TextSummarizer
        summarizer = current_app.config.get('SUMMARIZER')
        if summarizer and hasattr(summarizer, 'get_model_status'):
            summarizer_status = "available"
    except Exception as e:
        if "errors" not in health_data:
            health_data["errors"] = {}
        health_data["errors"]["summarizer"] = str(e)
        
    try:
        # Verificar status de NlpAnalyser
        classifier = current_app.config.get('CLASSIFIER')
        if classifier and hasattr(classifier, 'get_model_status'):
            classifier_status = "available"
    except Exception as e:
        if "errors" not in health_data:
            health_data["errors"] = {}
        health_data["errors"]["classifier"] = str(e)
        
    # Actualizar estado de los modelos
    health_data["services"]["summarizer"] = summarizer_status
    health_data["services"]["classifier"] = classifier_status
    
    # Si alguno de los servicios críticos no está disponible, cambiar el estado general
    if "unavailable" in [health_data["services"]["database"], health_data["services"]["api"]]:
        health_data["status"] = "degraded"
    
    # Verificar conexión a Neo4j bajo demanda
    try:
        # Solo intentar conectar si hay una contraseña configurada
        if NEO4J_PASSWORD:
            driver = get_neo4j_driver()
            if driver is not None:
                health_data["services"]["neo4j"] = "available"
            else:
                health_data["services"]["neo4j"] = "unavailable"
        else:
            health_data["services"]["neo4j"] = "unconfigured"
            if "errors" not in health_data:
                health_data["errors"] = {}
            health_data["errors"]["neo4j"] = "No hay contraseña configurada para Neo4j"
    except Exception as e:
        health_data["services"]["neo4j"] = "unavailable"
        if "errors" not in health_data:
            health_data["errors"] = {}
        health_data["errors"]["neo4j"] = str(e)
    
    # Verificar conexión a PostgreSQL
    try:
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        health_data["services"]["database"] = "available"
    except SQLAlchemyError as e:
        health_data["services"]["database"] = "unavailable"
        if "errors" not in health_data:
            health_data["errors"] = {}
        health_data["errors"]["database"] = str(e)
    
    return jsonify(health_data), 200 if health_data["status"] == "ok" else 207  # 207 Multi-Status

def get_neo4j_driver():
    """Obtiene una conexión a Neo4j o devuelve None si no está disponible.
    
    La función ha sido mejorada para reducir los mensajes de error repetitivos
    y para manejar mejor los casos en que Neo4j no está disponible.
    """
    global neo4j_available, _neo4j_connection_attempts

    # Si Neo4j está deshabilitado explícitamente, no intentar conectar
    if NEO4J_DISABLED:
        return None
    
    # Solo registrar un mensaje cada 10 intentos después del primer fallo
    log_this_attempt = (_neo4j_connection_attempts % 10 == 0)
    
    try:
        # Intentar conectar con timeout configurado
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=NEO4J_TIMEOUT  # Usando el timeout configurado
        )
        # Prueba rápida de conexión
        with driver.session() as session:
            session.run("RETURN 1 AS result")
            
        # Si llegamos aquí, la conexión fue exitosa
        if not neo4j_available:
            current_app.logger.info("✓ Conexión a Neo4j establecida correctamente")
            
        neo4j_available = True
        _neo4j_connection_attempts = 0  # Reiniciar contador de intentos
        return driver
        
    except Exception as e:
        # Incrementar contador de intentos
        _neo4j_connection_attempts += 1
        
        # Solo registrar mensajes de advertencia periódicamente
        if log_this_attempt:
            current_app.logger.warning(f"No se pudo conectar a Neo4j (intento #{_neo4j_connection_attempts}): {e}")
            
        neo4j_available = False
        return None

def register_blueprint(app):
    """Registra el blueprint en la aplicación Flask."""
    app.register_blueprint(health_bp)
