"""
Servicio para procesar archivos, incluyendo generación de miniaturas y extracción de metadatos.
Este módulo proporciona funcionalidad para trabajar con diferentes tipos de archivos.
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import io
import hashlib
from datetime import datetime

# Configuración para miniaturas
DEFAULT_THUMBNAIL_SIZE = (200, 200)
logger = logging.getLogger(__name__)

class FileProcessor:
    """Clase para procesar archivos y extraer información relevante."""
    
    def __init__(self, upload_folder: str = None):
        """
        Inicializa el procesador de archivos.
        
        Args:
            upload_folder: Carpeta donde se almacenan los archivos subidos
        """
        self.upload_folder = upload_folder
        
    def generate_thumbnail(self, file_path: str, size: Tuple[int, int] = DEFAULT_THUMBNAIL_SIZE) -> Optional[str]:
        """
        Genera una miniatura para un archivo de imagen.
        
        Args:
            file_path: Ruta al archivo original
            size: Tamaño de la miniatura (ancho, alto)
            
        Returns:
            Ruta a la miniatura generada o None si hay error
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"El archivo {file_path} no existe")
                return None
                
            # Verificar que es una imagen
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                logger.debug(f"El archivo {file_path} no es una imagen soportada para miniatura")
                return None
                
            # Crear nombre para la miniatura
            base_path = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            thumbnail_path = os.path.join(base_path, f"{name}_thumb{ext}")
            
            # Generar miniatura
            with Image.open(file_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path)
                
            logger.info(f"Miniatura generada en {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error al generar miniatura para {file_path}: {e}")
            return None
            
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extrae metadatos del archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Diccionario con metadatos
        """
        if not os.path.exists(file_path):
            return {'error': 'Archivo no encontrado'}
            
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Calcular hash MD5 para verificación
            md5_hash = None
            if file_size < 100 * 1024 * 1024:  # Solo para archivos menores a 100MB
                try:
                    with open(file_path, 'rb') as f:
                        md5_hash = hashlib.md5(f.read()).hexdigest()
                except Exception as e:
                    logger.warning(f"No se pudo calcular el hash MD5: {e}")
            
            return {
                'filename': os.path.basename(file_path),
                'size_bytes': file_size,
                'size_human': self._human_readable_size(file_size),
                'created_at': created,
                'modified_at': modified,
                'md5': md5_hash
            }
            
        except Exception as e:
            logger.error(f"Error al obtener metadatos de {file_path}: {e}")
            return {'error': str(e)}
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convierte tamaño en bytes a formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
