"""
API para gestionar el estado de tareas asíncronas.
"""

import logging
from flask import Blueprint, jsonify, request, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
try:
    from celery.result import AsyncResult
except ModuleNotFoundError:
    # Si Celery no está instalado, creamos una clase dummy para evitar que la app se caiga.
    # Las tareas asíncronas no funcionarán, pero el resto de la app sí.
    class AsyncResult:
        def __init__(self, task_id, app=None):
            self.id = task_id
            self.status = 'FAILURE'
            self.result = 'Celery is not installed or configured properly.'
            self._info = {'error': 'Celery not available'}

        def ready(self): 
            return True

        def successful(self):
            return False
            
        @property
        def info(self):
            return self._info
from ..models.file import File
from ..extensions import db


# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para rutas de tareas
tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks/<task_id>/status', methods=['GET'])
@jwt_required()
def check_task_status(task_id):
    """
    Verifica el estado de una tarea Celery por su ID
    """
    try:
        task_result = AsyncResult(task_id, app=current_app.celery)
        
        # Verificar que el usuario tiene acceso a esta tarea
        user_id = get_jwt_identity()
        
        # Opcionalmente, verificar si el usuario tiene permiso para ver esta tarea.
        # Esto requiere que el task_id esté asociado a un recurso del usuario.
        # Ejemplo: file = File.query.filter_by(task_id=task_id).first()
        # if file and file.user_id != int(get_jwt_identity()):
        #     return jsonify({"error": "No tienes permiso para acceder a esta tarea"}), 403

        status = task_result.status
        response = {
            "task_id": task_id,
            "status": status,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None,
        }

        if status == 'PROGRESS' and isinstance(task_result.info, dict):
            response['progress'] = task_result.info.get('progress', 0)
            response['status_message'] = task_result.info.get('status', 'Procesando...')
        
        if task_result.ready():
            if task_result.successful():
                response['result'] = task_result.get()
            else:
                # En caso de fallo, el resultado contiene la excepción
                response['error'] = str(task_result.result)

        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error verificando estado de tarea {task_id}: {str(e)}")
        return jsonify({"error": f"Error verificando tarea: {str(e)}"}), 500


@tasks_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    """
    Cancela una tarea en ejecución
    """
    try:
        user_id = get_jwt_identity()
        
        # Verificar si es una tarea asociada a un archivo del usuario
        file = File.query.filter_by(task_id=task_id).first()
        if file and file.user_id != int(user_id):
            return jsonify({"error": "No tienes permiso para cancelar esta tarea"}), 403
        
        # Intentar cancelar la tarea
        celery.control.revoke(task_id, terminate=True)
        
        # Actualizar el estado del archivo si corresponde
        if file:
            file.processing = False
            db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Tarea cancelada correctamente"
        })
        
    except Exception as e:
        logger.error(f"Error cancelando tarea {task_id}: {str(e)}")
        return jsonify({"error": f"Error al cancelar la tarea: {str(e)}"}), 500
