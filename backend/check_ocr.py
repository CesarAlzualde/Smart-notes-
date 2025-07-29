"""
Script para verificar la disponibilidad y configuración correcta del servicio OCR.
Este script comprueba:
1. La instalación de Tesseract OCR
2. La instalación de las bibliotecas de Google Vision
3. La configuración correcta de las credenciales
"""

import sys
import os
import logging
import importlib.util

# Añadir el directorio actual al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging de manera más visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Asegurar que los mensajes vayan a la consola
    ]
)
logger = logging.getLogger(__name__)

def check_tesseract():
    """Verificar instalación de Tesseract OCR."""
    try:
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
        logger.info(f"✅ Tesseract OCR está instalado (versión {tesseract_version})")
        return True
    except Exception as e:
        logger.error(f"❌ Tesseract OCR no está correctamente instalado: {e}")
        logger.info("Para instalar Tesseract OCR:")
        logger.info("  - Windows: Descargar e instalar desde https://github.com/UB-Mannheim/tesseract/wiki")
        logger.info("  - Linux: sudo apt-get install tesseract-ocr")
        logger.info("  - macOS: brew install tesseract")
        return False

def check_google_vision():
    """Verificar instalación y configuración de Google Vision API."""
    # Comprobar si las bibliotecas están instaladas
    vision_installed = importlib.util.find_spec("google.cloud.vision") is not None
    
    if not vision_installed:
        logger.error("❌ Google Cloud Vision no está instalado")
        logger.info("Para instalar Google Cloud Vision: pip install google-cloud-vision")
        return False
    
    # Comprobar si hay credenciales configuradas
    try:
        from google.cloud import vision
        from google.oauth2 import service_account
        
        # Buscar credenciales en variables de entorno
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not credentials_path:
            # Buscar en ubicaciones alternativas
            candidate_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "google-vision-key.json"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials", "google-vision-key.json")
            ]
            
            for path in candidate_paths:
                if os.path.isfile(path):
                    credentials_path = path
                    logger.info(f"✅ Archivo de credenciales encontrado en: {path}")
                    break
        
        if not credentials_path or not os.path.isfile(credentials_path):
            logger.error("❌ No se encontró archivo de credenciales para Google Vision")
            logger.info("Configure GOOGLE_APPLICATION_CREDENTIALS o coloque google-vision-key.json en la carpeta config/ o credentials/")
            return False
        
        # Intentar inicializar cliente para verificar credenciales
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = vision.ImageAnnotatorClient(credentials=credentials)
            logger.info("✅ Google Vision API está correctamente configurado y disponible")
            return True
        except Exception as e:
            logger.error(f"❌ Error al inicializar cliente Google Vision: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error al verificar Google Vision: {e}")
        return False

def check_pdf2image():
    """Verificar instalación de pdf2image."""
    try:
        import pdf2image
        logger.info("✅ pdf2image está instalado")
        
        # Verificar poppler (requerido por pdf2image)
        try:
            # Intenta crear un objeto pdf2image para ver si puede encontrar poppler
            sample_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
            if os.path.exists(sample_pdf):
                # Solo probar si el archivo existe
                pdf2image.convert_from_path(sample_pdf, dpi=72, first_page=1, last_page=1)
            logger.info("✅ poppler está correctamente instalado")
            return True
        except Exception as e:
            logger.warning(f"⚠️ poppler podría no estar correctamente instalado: {e}")
            logger.info("Para instalar poppler:")
            logger.info("  - Windows: Descargar de http://blog.alivate.com.au/poppler-windows/")
            logger.info("  - Linux: sudo apt-get install poppler-utils")
            logger.info("  - macOS: brew install poppler")
            return False
    except Exception as e:
        logger.error(f"❌ pdf2image no está instalado: {e}")
        logger.info("Para instalar pdf2image: pip install pdf2image")
        return False

def check_upload_directory():
    """Verificar que el directorio de subida de archivos existe y tiene permisos."""
    from app import create_app
    
    try:
        # Crear la aplicación para obtener la configuración
        app = create_app()
        
        with app.app_context():
            upload_dir = app.config.get('UPLOAD_FOLDER')
            
            if not upload_dir:
                logger.warning("⚠️ UPLOAD_FOLDER no está configurado en la aplicación")
                return False
                
            if not os.path.exists(upload_dir):
                try:
                    os.makedirs(upload_dir, exist_ok=True)
                    logger.info(f"✅ Directorio de subida creado: {upload_dir}")
                except Exception as e:
                    logger.error(f"❌ No se pudo crear el directorio de subida {upload_dir}: {e}")
                    return False
            
            # Verificar permisos
            test_file = os.path.join(upload_dir, '.test_write_permissions')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info(f"✅ Directorio de subida tiene permisos correctos: {upload_dir}")
                return True
            except Exception as e:
                logger.error(f"❌ El directorio de subida no tiene permisos de escritura: {e}")
                return False
    except Exception as e:
        logger.error(f"❌ Error al verificar directorio de subida: {e}")
        return False

def run_ocr_checks():
    """Ejecutar todas las verificaciones de OCR y devolver un informe."""
    logger.info("Iniciando verificación del sistema OCR...")
    
    results = {
        "tesseract": check_tesseract(),
        "google_vision": check_google_vision(),
        "pdf2image": check_pdf2image(),
        "upload_directory": check_upload_directory()
    }
    
    logger.info("\n=== RESUMEN DE VERIFICACIÓN OCR ===")
    for check, status in results.items():
        icon = "✅" if status else "❌"
        logger.info(f"{icon} {check}")
    
    if all(results.values()):
        logger.info("✅✅✅ Sistema OCR completamente operativo")
    else:
        logger.warning("⚠️ Sistema OCR parcialmente operativo. Revise los mensajes anteriores para solucionar problemas.")
    
    return results

if __name__ == "__main__":
    run_ocr_checks()
