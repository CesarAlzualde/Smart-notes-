"""
Funciones de utilidad generales para la aplicación.
"""

import os
from werkzeug.utils import secure_filename
import uuid
from flask import current_app


def allowed_file(filename):
    """
    Verifica si un archivo tiene una extensión permitida.
    
    Args:
        filename (str): Nombre del archivo a verificar
        
    Returns:
        bool: True si la extensión está permitida, False en caso contrario
    """
    if '.' not in filename:
        return False
        
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {
        'image': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
        'spreadsheet': ['xls', 'xlsx', 'csv', 'ods'],
        'presentation': ['ppt', 'pptx', 'odp'],
    })
    
    # Aplanar la lista de extensiones permitidas
    all_allowed = []
    for category in ALLOWED_EXTENSIONS.values():
        all_allowed.extend(category)
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in all_allowed


def save_file(file, user_id=None, category=None):
    """
    Guarda un archivo subido en el directorio correspondiente.
    
    Args:
        file (FileStorage): Objeto archivo de Flask
        user_id (int, optional): ID del usuario propietario del archivo
        category (str, optional): Categoría del archivo para organización
        
    Returns:
        tuple: (filename, filepath, file_size)
    """
    # Generar nombre seguro y único
    original_filename = file.filename
    filename = secure_filename(original_filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Determinar directorio de guardado
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if user_id:
        # Guardar en directorio del usuario
        user_folder = os.path.join(upload_folder, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        
        if category:
            # Guardar en subcarpeta específica
            category_folder = os.path.join(user_folder, category)
            os.makedirs(category_folder, exist_ok=True)
            save_path = os.path.join(category_folder, unique_filename)
        else:
            save_path = os.path.join(user_folder, unique_filename)
    else:
        # Guardar en directorio general
        os.makedirs(upload_folder, exist_ok=True)
        save_path = os.path.join(upload_folder, unique_filename)
    
    # Guardar archivo
    file.save(save_path)
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(save_path)
    
    return unique_filename, save_path, file_size


def get_file_extension(filename):
    """
    Obtiene la extensión de un archivo.
    
    Args:
        filename (str): Nombre del archivo
        
    Returns:
        str: Extensión del archivo sin el punto
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def get_file_category(filename):
    """
    Determina la categoría de un archivo basado en su extensión.
    
    Args:
        filename (str): Nombre del archivo
        
    Returns:
        str: Categoría del archivo (image, document, spreadsheet, presentation, other)
    """
    extension = get_file_extension(filename)
    
    if not extension:
        return 'other'
    
    CATEGORIES = {
        'image': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'tiff'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'md', 'tex'],
        'spreadsheet': ['xls', 'xlsx', 'csv', 'ods', 'tsv'],
        'presentation': ['ppt', 'pptx', 'odp', 'key'],
        'code': ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'ts'],
    }
    
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    
    return 'other'


def format_file_size(size_bytes):
    """
    Formatea un tamaño en bytes a una representación legible.
    
    Args:
        size_bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado con unidad (KB, MB, GB)
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
        
    kb = size_bytes / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
        
    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.1f} MB"
        
    gb = mb / 1024
    return f"{gb:.2f} GB"


def generate_thumbnail(filepath, output_path=None, size=(200, 200)):
    """
    Genera una miniatura para una imagen.
    
    Args:
        filepath (str): Ruta al archivo de imagen
        output_path (str, optional): Ruta donde guardar la miniatura
        size (tuple, optional): Tamaño de la miniatura (ancho, alto)
        
    Returns:
        str: Ruta a la miniatura generada o None si falla
    """
    try:
        from PIL import Image
        
        # Si no se especifica ruta de salida, usar la misma carpeta con sufijo _thumb
        if not output_path:
            filename = os.path.basename(filepath)
            directory = os.path.dirname(filepath)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumb{ext}"
            output_path = os.path.join(directory, thumb_filename)
        
        # Abrir imagen y crear miniatura
        with Image.open(filepath) as img:
            img.thumbnail(size)
            img.save(output_path, quality=85, optimize=True)
        
        return output_path
        
    except Exception as e:
        import logging
        logging.error(f"Error al generar miniatura: {e}")
        return None
