"""
Servicio para procesamiento OCR (Reconocimiento Óptico de Caracteres).
Permite extraer texto de imágenes y documentos PDF utilizando:
1. Tesseract OCR (implementación básica)
2. Google Vision OCR (implementación avanzada, requiere credenciales API)

Este módulo unifica las interfaces de ambos motores OCR y proporciona
un servicio integrado para la aplicación con manejo de fallos y alternativas.
"""

import os
import sys
import logging
import tempfile
import subprocess
import numpy as np
import pytesseract
import cv2
from PIL import Image
import platform
import pytesseract
import pdf2image
import io
import numpy as np

# No importamos Google Vision directamente aquí para evitar bloquear la inicialización
# Se importará bajo demanda cuando sea necesario
GOOGLE_VISION_AVAILABLE = None  # Se determinará en tiempo de ejecución
    
# Función de compatibilidad para google_vision_ocr requerida por analysis.py
def google_vision_ocr(image_path, language='es'):
    """
    Realiza OCR usando Google Vision API.
    
    Args:
        image_path: Ruta a la imagen
        language: Código de idioma (no usado directamente en Vision API pero para compatibilidad)
        
    Returns:
        str: Texto extraído de la imagen
    """
    try:
        # Comprobar disponibilidad de Google Vision bajo demanda
        vision_available = _check_google_vision_available()
        if not vision_available:
            logger.warning("Google Vision no está disponible. Usando OCRProcessor como alternativa.")
            ocr = OCRProcessor(lang=language)
            return ocr.process_file(image_path)
            
        # Importar módulos aquí para evitar bloquear la inicialización
        from google.cloud import vision
        from google.oauth2 import service_account
            
        # Buscar credenciales
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or DEFAULT_CREDENTIALS_PATH
        
        if not os.path.isfile(credentials_path):
            # Buscar en ruta alternativa
            alt_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "credentials", 
                "google-vision-key.json"
            )
            
            if os.path.isfile(alt_path):
                credentials_path = alt_path
            else:
                logger.error(f"No se encontró archivo de credenciales en {credentials_path} ni {alt_path}")
                return ""
        
        # Inicializar cliente
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = vision.ImageAnnotatorClient(credentials=credentials)
        
        # Leer imagen
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
            
        image = vision.Image(content=content)
        
        # Detectar texto
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            logger.error(f"Error en Google Vision API: {response.error.message}")
            return ""
            
        # Extraer texto completo
        text = response.full_text_annotation.text
        return text
        
    except Exception as e:
        logger.error(f"Error en Google Vision OCR: {e}")
        return ""
        
# Función de compatibilidad para extract_text_for_whiteboard requerida por analysis.py
def extract_text_for_whiteboard(image_path, lang='es'):
    """
    Extrae texto optimizado para pizarras o contenido manuscrito.
    
    Args:
        image_path: Ruta a la imagen
        lang: Idioma para OCR
        
    Returns:
        str: Texto extraído de la imagen
    """
    try:
        # Preferir Google Vision si está disponible (mejor para pizarras)
        # Comprobamos bajo demanda para evitar importaciones tempranas
        if _check_google_vision_available():
            return google_vision_ocr(image_path, lang)
        else:
            # Usar Tesseract con configuración específica para pizarras
            try:
                import cv2
                # Leer imagen
                img = cv2.imread(image_path)
                # Convertir a escala de grises
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Aplicar umbral adaptativo
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                # Aplicar OCR
                ocr = OCRProcessor(lang=lang)
                # Guardar imagen preprocesada temporalmente
                tmp_path = f"{image_path}_preprocessed.jpg"
                cv2.imwrite(tmp_path, thresh)
                text = ocr.process_file(tmp_path)
                # Limpiar
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                return text
            except Exception as e:
                logger.error(f"Error en preprocesamiento de pizarra: {e}")
                # Fallback a OCR normal
                ocr = OCRProcessor(lang=lang)
                return ocr.process_file(image_path)
    except Exception as e:
        logger.error(f"Error en extract_text_for_whiteboard: {e}")
        return ""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de rutas para Tesseract en Windows
if platform.system() == 'Windows':
    # Rutas comunes de instalación de Tesseract en Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
        r'C:\Users\cesar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
        r'C:\Users\cesar\AppData\Local\Tesseract-OCR\tesseract.exe'
    ]
    
    # Buscar el ejecutable de Tesseract
    tesseract_path = None
    for path in possible_paths:
        if os.path.isfile(path):
            tesseract_path = path
            tessdata_path = os.path.join(os.path.dirname(path), 'tessdata')
            break
    
    # Configurar Tesseract si se encontró
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configurar variable de entorno TESSDATA_PREFIX
        tessdata_dir = os.path.join(os.path.dirname(tesseract_path), 'tessdata')
        os.environ['TESSDATA_PREFIX'] = tessdata_dir
        
        logger.info(f"Tesseract configurado en: {tesseract_path}")
        logger.info(f"TESSDATA_PREFIX configurado en: {tessdata_dir}")
        
        # Verificar si existen los archivos de idioma
        required_langs = ['eng', 'es', 'spa']
        for lang in required_langs:
            lang_file = os.path.join(tessdata_dir, f"{lang}.traineddata")
            if os.path.isfile(lang_file):
                logger.info(f"El archivo de datos del idioma {lang} existe en {lang_file}")
            else:
                logger.warning(f"No se encontró el archivo de datos del idioma {lang} en {lang_file}")
    else:
        logger.warning("No se pudo encontrar Tesseract en las rutas predeterminadas")

# Variables globales para evitar verificaciones repetidas
GOOGLE_VISION_AVAILABLE = None
GOOGLE_VISION_ERROR_REASON = None  # Para almacenar el motivo específico del error
TESSERACT_AVAILABLE = None
def resource_path(relative_path):
    """ Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # No estamos en un paquete, la ruta es relativa al directorio del proyecto
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

DEFAULT_CREDENTIALS_PATH = resource_path(os.path.join("config", "google-vision-key.json"))

def _check_tesseract_available():
    """
    Verifica si Tesseract está disponible en el sistema
    
    Returns:
        bool: True si Tesseract está disponible, False en caso contrario
    """
    global TESSERACT_AVAILABLE
    
    if TESSERACT_AVAILABLE is not None:
        return TESSERACT_AVAILABLE
        
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract disponible, versión: {version}")
        TESSERACT_AVAILABLE = True
    except Exception as e:
        logger.warning(f"Tesseract no disponible: {e}")
        TESSERACT_AVAILABLE = False
        
    return TESSERACT_AVAILABLE

def _check_google_vision_available(force_check=False):
    """
    Comprueba si Google Vision está disponible sin bloquear la inicialización de la app.
    Se usa para lazy loading de las dependencias de Google Vision.
    
    Args:
        force_check: Si True, fuerza una nueva comprobación incluso si ya se ha comprobado antes
    
    Returns:
        bool: True si Google Vision está disponible, False en caso contrario
    """
    global GOOGLE_VISION_AVAILABLE
    
    # Si ya se ha comprobado y no se fuerza, devolver el resultado cacheado
    if GOOGLE_VISION_AVAILABLE is not None and not force_check:
        return GOOGLE_VISION_AVAILABLE
    
    # Inicializar con error genérico
    error_reason = "Desconocido"
    
    try:
        # Intentar importar las dependencias de Google Vision
        from google.cloud import vision
        from google.oauth2 import service_account
        import google.api_core.exceptions
        
        # Verificar si el archivo de credenciales existe
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        logger.info(f"Comprobando credenciales en: {credentials_path}")
        
        if not credentials_path or not os.path.isfile(credentials_path):
            # Buscar en rutas alternativas
            alt_paths = [
                DEFAULT_CREDENTIALS_PATH,
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "credentials", 
                    "google-vision-key.json"
                ),
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "config", 
                    "google-vision-key.json"
                )
            ]
            
            for alt_path in alt_paths:
                logger.info(f"Buscando credenciales en ruta alternativa: {alt_path}")
                if os.path.isfile(alt_path):
                    credentials_path = alt_path
                    # Establecer la variable de entorno para el proceso actual
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                    logger.info(f"Variable de entorno GOOGLE_APPLICATION_CREDENTIALS establecida a: {credentials_path}")
                    break
            
            if not credentials_path or not os.path.isfile(credentials_path):
                error_reason = "No se encontró archivo de credenciales para Google Vision API"
                logger.warning(error_reason)
                GOOGLE_VISION_AVAILABLE = False
                return False
        
        # Verificar que podemos cargar las credenciales y hacer una prueba real
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = vision.ImageAnnotatorClient(credentials=credentials)
            
            # Crear una imagen mínima válida para la prueba
            # Un píxel negro en formato PNG
            one_pixel_image = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63600802000000050001b2d5065f0000000049454e44ae426082')
            
            image = vision.Image(content=one_pixel_image)
            
            try:
                # Intento mínimo para verificar la conectividad
                features = [{'type_': vision.Feature.Type.TEXT_DETECTION}]
                response = client.annotate_image({'image': image, 'features': features})
                
                # Si llegamos aquí, la API está habilitada y las credenciales son correctas
                logger.info("Conexión a Google Vision API verificada correctamente")
                GOOGLE_VISION_AVAILABLE = True
                
            except google.api_core.exceptions.PermissionDenied as e:
                # Error 403 - Credenciales o permisos incorrectos
                error_reason = f"Error 403: La API Vision no está habilitada o faltan permisos: {str(e)}"
                logger.error(error_reason)
                GOOGLE_VISION_AVAILABLE = False
                
            except Exception as e:
                error_reason = f"Error al probar conectividad con Google Vision API: {str(e)}"
                logger.error(error_reason)
                GOOGLE_VISION_AVAILABLE = False
            
        except Exception as e:
            error_reason = f"Error al cargar credenciales de Google Vision: {str(e)}"
            logger.error(error_reason)
            GOOGLE_VISION_AVAILABLE = False
            
    except ImportError as e:
        error_reason = f"Google Vision API no está disponible (módulos no instalados): {str(e)}"
        logger.warning(error_reason)
        GOOGLE_VISION_AVAILABLE = False
    
    # Almacenar el motivo del error para poder mostrarlo en la interfaz
    if not GOOGLE_VISION_AVAILABLE:
        global GOOGLE_VISION_ERROR_REASON
        GOOGLE_VISION_ERROR_REASON = error_reason
    
    return GOOGLE_VISION_AVAILABLE

# Función unificada para procesar OCR (requerida por analysis.py)
def process_ocr(filepath, engine='auto', is_whiteboard=False, lang='es'):
    """
    Procesa un archivo con OCR utilizando el motor especificado.
    
    Args:
        filepath: Ruta al archivo
        engine: Motor OCR ('tesseract', 'google_vision', 'auto')
        is_whiteboard: Si es una imagen de pizarra/whiteboard
        lang: Idioma para OCR
        
    Returns:
        dict: Resultado con claves 'success', 'text', 'engine_used', 'error'
    """
    try:
        # Forzar verificación de disponibilidad para obtener estado actualizado
        google_available = _check_google_vision_available(force_check=True)
        tesseract_available = _check_tesseract_available()
        
        # Log detallado para diagnóstico
        logger.info(f"Procesando OCR con motor={engine}, whiteboard={is_whiteboard}, google_disponible={google_available}, tesseract_disponible={tesseract_available}")
        
        # Determinar motor a usar
        use_google = False
        if engine == 'google':
            if google_available:
                use_google = True
                logger.info("Usando Google Vision API (seleccionado explícitamente)")
            else:
                logger.warning("Se solicitó Google Vision pero no está disponible, usando alternativa")
        elif engine == 'google_vision':
            if google_available:
                use_google = True
                logger.info("Usando Google Vision API (seleccionado explícitamente)")
            else:
                logger.warning("Se solicitó Google Vision pero no está disponible, usando alternativa")
        elif engine == 'auto' and is_whiteboard and google_available:
            use_google = True
            logger.info("Usando Google Vision API (selección automática para whiteboard)")
            
        # Extraer texto según el motor seleccionado
        if use_google:
            logger.info(f"Extrayendo texto con Google Vision: {filepath}")
            text = google_vision_ocr(filepath, lang)
            engine_used = 'google_vision'
        elif is_whiteboard:
            logger.info(f"Extrayendo texto con Tesseract optimizado para whiteboard: {filepath}")
            text = extract_text_for_whiteboard(filepath, lang)
            engine_used = 'tesseract_optimized'
        else:
            logger.info(f"Extrayendo texto con Tesseract estándar: {filepath}")
            ocr = OCRProcessor(lang=lang)
            text = ocr.process_file(filepath)
            engine_used = 'tesseract'
            
        logger.info(f"OCR completado con motor {engine_used}, longitud del texto: {len(text) if text else 0}")
            
        return {
            'success': bool(text),
            'text': text,
            'engine_used': engine_used,
            'error': None
        }
        
    except Exception as e:
        logger.error(f"Error en process_ocr: {e}")
        return {
            'success': False,
            'text': '',
            'engine_used': None,
            'error': str(e)
        }

class OCRProcessor:
    """
    Procesador OCR para extraer texto de imágenes y documentos PDF.
    
    Utiliza Tesseract OCR para imágenes y pdf2image + Tesseract para PDFs.
    """
    
    def __init__(self, lang='es'):
        """
        Inicializa el procesador OCR.
        
        Args:
            lang (str): Idioma para OCR (por defecto 'es' para español)
        """
        # Mapeo de códigos de idioma a los códigos que usa Tesseract
        lang_map = {
            'es': 'spa',  # Español (es) a Spanish/Español (spa) en Tesseract
        }
        
        # Si el idioma está en el mapeo, usamos la versión correcta para Tesseract
        self.lang = lang_map.get(lang, lang)
        
        # Verificar si el idioma solicitado tiene archivos de entrenamiento disponibles
        # Si es Windows, verificar si existe el archivo de idioma
        if platform.system() == 'Windows' and 'TESSDATA_PREFIX' in os.environ:
            tessdata_dir = os.environ['TESSDATA_PREFIX']
            # Primero verificamos el idioma mapeado (ej: 'spa' para 'es')
            requested_lang_file = os.path.join(tessdata_dir, f"{self.lang}.traineddata")
            
            # Si no existe el idioma solicitado pero existe inglés, usar inglés
            if not os.path.isfile(requested_lang_file):
                eng_lang_file = os.path.join(tessdata_dir, "eng.traineddata")
                if os.path.isfile(eng_lang_file):
                    logger.warning(f"No se encontró el archivo para idioma '{lang}', usando 'eng' como alternativa")
                    self.lang = 'eng'
        
        self.supported_image_types = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        self.supported_types = self.supported_image_types + ['.pdf']
        
    def is_supported_filetype(self, filename):
        """
        Verifica si el tipo de archivo es soportado.
        
        Args:
            filename (str): Nombre del archivo a verificar
            
        Returns:
            bool: True si es soportado, False en caso contrario
        """
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_types
        
    def process_file(self, filepath):
        """
        Procesa un archivo y extrae su texto.
        
        Args:
            filepath (str): Ruta al archivo a procesar
            
        Returns:
            str: Texto extraído del archivo
        """
        if not os.path.exists(filepath):
            logger.error(f"Archivo no encontrado: {filepath}")
            return ""
            
        try:
            ext = os.path.splitext(filepath.lower())[1]
            
            # Procesar según tipo de archivo
            if ext == '.pdf':
                return self._process_pdf(filepath)
            elif ext in self.supported_image_types:
                return self._process_image(filepath)
            else:
                logger.error(f"Tipo de archivo no soportado: {ext}")
                return ""
                
        except Exception as e:
            logger.error(f"Error al procesar archivo: {e}")
            return ""
            
    def _process_image(self, image_path):
        """
        Procesa una imagen con OCR.
        
        Args:
            image_path (str): Ruta a la imagen
            
        Returns:
            str: Texto extraído de la imagen
        """
        try:
            # Verificar si Tesseract está disponible
            if _check_tesseract_available():
                logger.info(f"Procesando imagen con Tesseract: {image_path}")
                # Abrir imagen con PIL
                with Image.open(image_path) as img:
                    # Aplicar preprocesamiento básico
                    img = self._preprocess_image(img)
                    
                    # Realizar OCR
                    text = pytesseract.image_to_string(img, lang=self.lang)
                    logger.info(f"Extracción con Tesseract completada: {len(text)} caracteres")
                    return text.strip()
            else:
                # Modo simulado para desarrollo/pruebas
                logger.warning("Utilizando modo simulado para OCR (Tesseract no disponible)")
                return self._simulate_ocr(image_path)
            
        except Exception as e:
            logger.error(f"Error en OCR de imagen: {e}")
            return ""

    def _process_pdf(self, pdf_path):
        """
        Procesa un documento PDF con OCR.
        
        Args:
            pdf_path (str): Ruta al PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            try:
                images = pdf2image.convert_from_path(
                    pdf_path, 
                    dpi=300,
                    fmt="jpeg",
                    output_folder=tempfile.gettempdir()
                )
                extracted_text = []
                for i, img in enumerate(images):
                    img = self._preprocess_image(img)
                    text = pytesseract.image_to_string(img, lang=self.lang)
                    extracted_text.append(text)
                    img.close()
                return "\n\n".join(extracted_text).strip()
            except Exception as e:
                logger.info(f"Error en proceso normal de PDF: {e}. Utilizando modo simulado.")
                return self._simulate_ocr(pdf_path, is_pdf=True)
        except Exception as e:
            logger.error(f"Error en OCR de PDF: {e}")
            return ""

    def _preprocess_image(self, img):
        """
        Preprocesa una imagen para mejorar resultados OCR.
        
        Args:
            img (PIL.Image): Imagen a preprocesar
            
        Returns:
            PIL.Image: Imagen preprocesada
        """
        try:
            if img.mode != 'L':
                img = img.convert('L')
            return img
        except Exception as e:
            logger.error(f"Error en preprocesamiento de imagen: {e}")
            return img

    def _simulate_ocr(self, file_path, is_pdf=False):
        """
        Simula procesamiento OCR para desarrollo cuando Tesseract no está disponible.
        
        Args:
            file_path (str): Ruta al archivo
            is_pdf (bool): Si el archivo es PDF
            
        Returns:
            str: Texto simulado
        """
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        if is_pdf:
            return (
                f"[OCR SIMULADO para PDF: {filename}]\n\n"
                f"Este es un texto simulado para un documento PDF de {file_size} bytes.\n"
                "En un entorno de producción, este texto sería extraído mediante OCR real.\n\n"
                "El documento contiene información importante sobre el tema tratado.\n"
                "Los puntos principales incluyen:\n"
                "- Primer punto de información relevante\n"
                "- Segundo punto con datos adicionales\n"
                "- Conclusiones y recomendaciones\n\n"
                "Para habilitar OCR real, instale Tesseract y las dependencias necesarias."
            )
        else:
            return (
                f"[OCR SIMULADO para imagen: {filename}]\n\n"
                f"Este es un texto simulado para una imagen de {file_size} bytes.\n"
                "En un entorno de producción, este texto sería extraído mediante OCR real.\n\n"
                "La imagen contiene texto que sería procesado por Tesseract OCR.\n"
                "Para habilitar OCR real, instale Tesseract y configure el path adecuadamente."
            )
    
    def is_google_vision_available(self, force_check=False):
        """
        Verifica si Google Vision API está disponible y configurado correctamente.
        Implementa lazy loading para evitar bloquear la inicialización.
        
        Args:
            force_check (bool): Si es True, fuerza una nueva verificación ignorando resultados en caché
        
        Returns:
            bool: True si Google Vision está disponible, False en caso contrario
        """
        # Primer paso: verificar si el módulo está disponible
        if not _check_google_vision_available(force_check=force_check):
            return False
            
        try:
            # Importar de forma diferida dentro del método
            from google.cloud import vision
            from google.oauth2 import service_account
            
            # Verificar si el archivo de credenciales existe
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            
            # Si no está en variable de entorno, buscar en rutas predeterminadas
            if not credentials_path or not os.path.isfile(credentials_path):
                # Buscar en la ruta por defecto
                credentials_path = DEFAULT_CREDENTIALS_PATH
                
                # Si no existe, probar ruta alternativa
                if not os.path.isfile(credentials_path):
                    alt_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "credentials", 
                        "google-vision-key.json"
                    )
                    
                    if os.path.isfile(alt_path):
                        credentials_path = alt_path
                    else:
                        logger.warning("No se encontró archivo de credenciales para Google Vision API")
                        return False
            
            # Simplemente verificar que el archivo existe y es accesible, no crear un cliente
            # Esto acelera la verificación y evita operaciones de red durante el inicio
            if os.path.isfile(credentials_path) and os.access(credentials_path, os.R_OK):
                # Intentar cargar el archivo de credenciales sin crear cliente
                try:
                    service_account.Credentials.from_service_account_file(credentials_path)
                    return True
                except Exception as e:
                    logger.error(f"Error al cargar credenciales de Google Vision: {e}")
                    return False
            else:
                logger.warning(f"Archivo de credenciales no accesible: {credentials_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad de Google Vision: {e}")
            return False

    def generate_thumbnail(self, image_path, size=(200, 200)):
        """
        Genera una miniatura para una imagen.
        
        Args:
            image_path (str): Ruta a la imagen
            size (tuple): Tamaño de la miniatura (ancho, alto)
            
        Returns:
            str: Ruta a la miniatura generada o None si falla
        """
        try:
            # Verificar que el archivo existe
            if not os.path.isfile(image_path):
                logger.error(f"Archivo de imagen no encontrado: {image_path}")
                return None
                
            # Crear directorio de miniaturas si no existe
            thumbnails_dir = os.path.join(os.path.dirname(image_path), "thumbnails")
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Generar nombre para la miniatura
            filename = os.path.basename(image_path)
            thumbnail_path = os.path.join(thumbnails_dir, f"thumb_{filename}")
            
            # Crear miniatura con PIL
            with Image.open(image_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path, "JPEG")
                
            return thumbnail_path
        except Exception as e:
            logger.error(f"Error al generar miniatura: {e}")
            return None


class GoogleVisionOCR:
    """Clase para manejar la extracción de texto de imágenes y PDFs usando Google Cloud Vision API.
    Ofrece mayor precisión que Tesseract, especialmente con pizarras, tableros y texto manuscrito.
    Implementa lazy loading para no bloquear la inicialización de la aplicación.
    """
    
    def __init__(self, credentials_path=None):
        """Inicializa el cliente de Google Vision con lazy loading."""
        # Si no se proporciona ruta, usar la predeterminada
        if not credentials_path:
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or DEFAULT_CREDENTIALS_PATH
            
            # Si no existe, buscar en rutas alternativas
            if not os.path.isfile(credentials_path):
                alt_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "credentials", 
                    "google-vision-key.json"
                )
                
                if os.path.isfile(alt_path):
                    credentials_path = alt_path
        
        self.credentials_path = credentials_path
        self.client = None
        # No inicializamos el cliente en el constructor para evitar bloquear la app
        
    def _init_client(self):
        """Inicializa el cliente de Google Vision API bajo demanda (lazy loading)."""
        # No importamos los módulos hasta que sea necesario
        if not _check_google_vision_available():
            logger.error("Google Vision no está disponible como librería")
            return False
            
        try:
            # Importamos aquí para implementar lazy loading
            from google.cloud import vision
            from google.oauth2 import service_account
            
            credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
            self.client = vision.ImageAnnotatorClient(credentials=credentials)
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Google Vision API: {e}")
            return False
    def extract_text_from_image(self, image_path: str):
        """
        Extrae texto de una imagen usando Google Cloud Vision API.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Texto extraído
        """
        try:
            # Inicializar cliente si aún no se ha hecho
            if self.client is None and not self._init_client():
                return ""
            
            # Importamos aquí para implementar lazy loading
            from google.cloud import vision
                
            # Leer imagen
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
                
            image = vision.Image(content=content)
            
            # Detectar texto
            response = self.client.document_text_detection(image=image)
            
            # Extraer texto completo
            if response.error.message:
                raise Exception(f"Error en Google Vision API: {response.error.message}")
                
            text = response.full_text_annotation.text
            
            return text
            
        except Exception as e:
            logger.error(f"Error al extraer texto con Google Vision API: {e}")
            return ""
            
    def image_to_text(self, file_path: str):
        """
        Convierte una imagen o un PDF a texto.
        
        Args:
            file_path: Ruta al archivo (imagen o PDF)
            
        Returns:
            Texto extraído
            
        Raises:
            ValueError: Si el archivo no existe o no es un tipo compatible
            RuntimeError: Si falla el proceso de OCR
        """
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise ValueError(f"Archivo no encontrado: {file_path}")
            
        ext = os.path.splitext(file_path.lower())[1]
        
        # Procesar según tipo de archivo
        if ext == '.pdf':
            # Convertir PDF a imágenes y procesar cada página
            try:
                images = pdf2image.convert_from_path(
                    file_path, 
                    dpi=300,
                    fmt="jpeg",
                    output_folder=tempfile.gettempdir()
                )
                
                extracted_text_parts = []
                for i, image in enumerate(images):
                    # Guardar imagen temporalmente
                    temp_image_path = os.path.join(tempfile.gettempdir(), f"page_{i}.jpg")
                    image.save(temp_image_path, "JPEG")
                    
                    # Extraer texto
                    page_text = self.extract_text_from_image(temp_image_path)
                    extracted_text_parts.append(f"===== PÁGINA {i+1} =====\n\n{page_text}")
                    
                    # Eliminar archivo temporal
                    os.remove(temp_image_path)
                    
                return "\n\n".join(extracted_text_parts)
                
            except Exception as e:
                raise RuntimeError(f"Error al procesar PDF con Google Vision: {e}")
                
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif']:
            # Procesar imagen directamente
            text = self.extract_text_from_image(file_path)
            if not text:
                raise RuntimeError("No se pudo extraer texto de la imagen")
            return text
            
        else:
            raise ValueError(f"Tipo de archivo no soportado: {ext}")
