"""
Script de diagnóstico para identificar componentes que bloquean el arranque del servidor.
"""
import sys
import os
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir la carpeta raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def probar_componente(nombre, funcion):
    """Ejecuta una función de prueba y mide el tiempo que tarda."""
    logger.info(f"Iniciando prueba de {nombre}...")
    inicio = time.time()
    try:
        funcion()
        fin = time.time()
        logger.info(f"✅ {nombre} inicializado correctamente en {fin - inicio:.2f} segundos")
    except Exception as e:
        logger.error(f"❌ Error al inicializar {nombre}: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Prueba 1: Importar app sin inicializar
def test_import_app():
    from backend.app import create_app
    logger.info("Módulo app importado sin inicializar")

# Prueba 2: Crear app con configuración mínima
def test_create_minimal_app():
    from backend.app import create_app
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    logger.info("App creada con configuración mínima")

# Prueba 3: Importar servicios pero sin crear instancias
def test_import_services():
    import importlib
    
    # Importar servicios clave
    servicios = [
        "backend.app.services.text_summarizer",
        "backend.app.services.file_processor", 
        "backend.app.services.ocr_processor",
    ]
    
    for servicio in servicios:
        try:
            importlib.import_module(servicio)
            logger.info(f"✅ Importación de {servicio} exitosa")
        except Exception as e:
            logger.error(f"❌ Error importando {servicio}: {e}")

# Prueba 4: Crear instancia de TextSummarizer (ahora con lazy loading)
def test_create_summarizer():
    from backend.app.services.text_summarizer import TextSummarizer
    summarizer = TextSummarizer()
    logger.info("✅ Instancia de TextSummarizer creada (no debe cargar modelo)")
    
    # Verificar si el modelo está cargado
    logger.info(f"Estado del modelo: {summarizer.model_status.loaded}")

if __name__ == "__main__":
    logger.info("=== Iniciando diagnóstico de servidor ===")
    
    # Ejecutar pruebas en orden
    probar_componente("Importar app", test_import_app)
    probar_componente("Servicios", test_import_services)
    probar_componente("TextSummarizer", test_create_summarizer)
    probar_componente("Crear app mínima", test_create_minimal_app)
    
    logger.info("=== Diagnóstico completo ===")
