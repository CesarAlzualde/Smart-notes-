"""
Utilidades para validación, manejo de errores y formateo de respuestas.
Este módulo centraliza la lógica de validación y manejo de errores para la API.
"""

import re
from typing import Dict, Any, List, Union, Optional, Tuple, Callable
from functools import wraps
from datetime import datetime
from flask import request, jsonify, Response, g, current_app
import json


# Validación general
def validate_json_data(required_fields: List[str] = None, optional_fields: Dict[str, type] = None) -> Callable:
    """
    Decorador que valida los datos JSON entrantes.
    
    Args:
        required_fields: Lista de campos obligatorios
        optional_fields: Diccionario de campos opcionales con sus tipos esperados
    
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar que hay datos JSON
            if not request.is_json:
                return error_response("Se esperan datos en formato JSON", 400)
            
            data = request.get_json()
            if data is None:
                return error_response("Datos JSON inválidos", 400)
            
            # Validar campos requeridos
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    fields_str = ", ".join(missing_fields)
                    return error_response(f"Faltan campos requeridos: {fields_str}", 400)
            
            # Validar tipos de campos opcionales
            if optional_fields:
                for field, expected_type in optional_fields.items():
                    if field in data and not isinstance(data[field], expected_type):
                        return error_response(
                            f"El campo '{field}' debe ser de tipo {expected_type.__name__}", 
                            400
                        )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_email(email: str) -> bool:
    """
    Valida el formato de un email.
    
    Args:
        email: Dirección de correo a validar
    
    Returns:
        True si el email es válido, False en caso contrario
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valida que una contraseña cumpla con requisitos mínimos.
    
    Args:
        password: Contraseña a validar
    
    Returns:
        Tupla (es_válida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    # Podrían añadirse más validaciones como requerir mayúsculas, números, etc.
    return True, ""


def validate_date_format(date_str: str) -> Tuple[bool, Optional[datetime]]:
    """
    Valida que una cadena tenga formato de fecha ISO 8601.
    
    Args:
        date_str: Cadena de fecha a validar
    
    Returns:
        Tupla (es_válida, objeto_datetime o None)
    """
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True, date_obj
    except (ValueError, TypeError):
        return False, None


# Manejo de errores
def error_response(message: str, status_code: int = 400, errors: List[Dict[str, Any]] = None) -> Response:
    """
    Genera una respuesta de error JSON estandarizada.
    
    Args:
        message: Mensaje principal de error
        status_code: Código HTTP de estado
        errors: Lista opcional de errores detallados
    
    Returns:
        Respuesta Flask con JSON
    """
    response = {
        "error": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code


def success_response(data: Any = None, message: str = "Operación exitosa", status_code: int = 200) -> Response:
    """
    Genera una respuesta de éxito JSON estandarizada.
    
    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje de éxito
        status_code: Código HTTP de estado
    
    Returns:
        Respuesta Flask con JSON
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


# Formateo de datos para paginación
def paginate_response(items: List[Dict[str, Any]], 
                     page: int, 
                     per_page: int, 
                     total: int, 
                     message: str = "Datos obtenidos exitosamente") -> Response:
    """
    Genera una respuesta JSON con paginación.
    
    Args:
        items: Lista de elementos para la página actual
        page: Número de página actual
        per_page: Elementos por página
        total: Total de elementos
        message: Mensaje de éxito
    
    Returns:
        Respuesta Flask con JSON
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    
    pagination = {
        "page": page,
        "per_page": per_page,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    return success_response({
        "items": items,
        "pagination": pagination
    }, message)


# Normalización de datos
def normalize_string(text: str) -> str:
    """
    Normaliza una cadena: elimina espacios adicionales y convierte a minúsculas.
    
    Args:
        text: Texto a normalizar
    
    Returns:
        Texto normalizado
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip().lower()


def normalize_tags(tags: List[str]) -> List[str]:
    """
    Normaliza una lista de etiquetas.
    
    Args:
        tags: Lista de etiquetas
    
    Returns:
        Lista de etiquetas normalizadas y únicas
    """
    if not tags:
        return []
    
    normalized = [normalize_string(tag) for tag in tags]
    # Eliminar vacíos y duplicados
    return list(set(tag for tag in normalized if tag))


# Logging personalizado
def log_activity(activity_type: str, data: Dict[str, Any]) -> None:
    """
    Registra una actividad del sistema.
    
    Args:
        activity_type: Tipo de actividad (ej: 'login', 'note_create')
        data: Datos relacionados con la actividad
    """
    user_id = getattr(g, 'current_user', None)
    user_id = user_id.id if user_id else None
    
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "activity_type": activity_type,
        "user_id": user_id,
        "data": data,
        "ip": request.remote_addr
    }
    
    # En un entorno de producción, esto podría guardarse en la base de datos
    # o en un servicio de logging externo
    current_app.logger.info(json.dumps(log_entry))
