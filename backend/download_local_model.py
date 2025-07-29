import os
import logging
from huggingface_hub import snapshot_download

# --- Configuración ---
MODEL_ID = "google/mt5-base"
LOCAL_MODEL_PATH = os.path.join("local_models", MODEL_ID)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_model_snapshot():
    """Descarga un modelo completo usando snapshot_download."""
    logger.info(f"Iniciando descarga del modelo: {MODEL_ID}")
    logger.info(f"Se guardará en: {os.path.abspath(LOCAL_MODEL_PATH)}")

    # Crear el directorio si no existe
    os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)

    try:
        # Descargar todos los archivos del repositorio del modelo
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=LOCAL_MODEL_PATH,
            local_dir_use_symlinks=False,  # Usar False en Windows para evitar problemas
            resume_download=True
        )
        logger.info(f"¡Descarga completada! Modelo guardado en: {LOCAL_MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"Ocurrió un error durante la descarga: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("--- Script de Descarga de Modelo Local ---")
    success = download_model_snapshot()

    if success:
        logger.info("\nEl modelo ha sido descargado exitosamente.")
        logger.info("Por favor, actualiza tu archivo 'ai_config.json' para usar la ruta local:")
        # Formatear la ruta para que sea compatible con JSON (usando diagonales hacia adelante)
        json_compatible_path = LOCAL_MODEL_PATH.replace('\\', '/')
        logger.info(f'  "summarization_model": "{json_compatible_path}",')
        logger.info('  "use_local_model": true')
    else:
        logger.error("\nLa descarga del modelo falló. Revisa los logs para más detalles.")
