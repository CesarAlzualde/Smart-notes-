"""
API para gestión de archivos.
Proporciona endpoints para subir, descargar y gestionar archivos.
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import os
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models.file import File
from ..models.note import Note
from ..utils.helpers import allowed_file
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar OCR Processor para verificar disponibilidad de Google Vision
from ..services.ocr_processor import OCRProcessor
from ..services.file_processor import FileProcessor, DEFAULT_THUMBNAIL_SIZE
from ..utils.celery_helpers import fallback_to_sync
from ..services.ocr_summary_handler import OCRSummaryHandler

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

@api_bp.route('/files', methods=['GET'])
@jwt_required()
def get_files():
    """Obtiene todos los archivos del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'uploaded_at')
        sort_dir = request.args.get('sort_dir', 'desc')
        mimetype = request.args.get('mimetype')
        processed = request.args.get('processed')
        
        # Construir consulta base
        query = File.query.filter_by(user_id=user_id)
        
        # Aplicar filtros
        if mimetype:
            query = query.filter(File.mimetype.like(f"{mimetype}%"))
            
        if processed is not None:
            processed_bool = processed.lower() == 'true'
            query = query.filter(File.processed == processed_bool)
            
        # Ordenar resultados
        if sort_dir == 'desc':
            query = query.order_by(db.desc(getattr(File, sort_by)))
        else:
            query = query.order_by(getattr(File, sort_by))
            
        # Paginar resultados
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar respuesta
        files = [file.to_dict() for file in pagination.items]
        
        return jsonify({
            'files': files,
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logging.error(f"Error al obtener archivos: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Obtiene detalles de un archivo específico."""
    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not file:
            return jsonify({"error": "Archivo no encontrado"}), 404
            
        return jsonify(file.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Error al obtener archivo {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files', methods=['POST'])
@jwt_required()
def upload_file():
    """Sube un nuevo archivo."""
    try:
        user_id = get_jwt_identity()
        
        # Verificar si hay archivo adjunto y si la solicitud tiene la parte multipart/form-data
        if 'file' not in request.files:
            logging.warning(f"Solicitud de carga sin el campo 'file'. Campos presentes: {request.files.keys()}")
            return jsonify({"error": "No se proporcionó ningún archivo en el campo 'file'"}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
        # Verificar tipo de archivo permitido con mejor manejo de errores
        try:
            if not allowed_file(file.filename):
                extension = os.path.splitext(file.filename)[1].lower() if '.' in file.filename else 'desconocido'
                return jsonify({
                    "error": f"Tipo de archivo no permitido: {extension}", 
                    "allowed_extensions": current_app.config.get('ALLOWED_EXTENSIONS', [])
                }), 400
        except Exception as e:
            logging.error(f"Error al validar tipo de archivo: {e}")
            return jsonify({"error": "Error al validar el tipo de archivo"}), 422
            
        # Verificar tamaño del archivo
        max_size = current_app.config.get('MAX_CONTENT_LENGTH') or 10 * 1024 * 1024  # Por defecto 10MB
        try:
            file.seek(0, os.SEEK_END)
            file_size_check = file.tell()
            file.seek(0)  # Reiniciar el puntero del archivo
            
            if file_size_check and max_size and file_size_check > max_size:
                max_mb = max_size / (1024 * 1024)
                actual_mb = file_size_check / (1024 * 1024)
                return jsonify({
                    "error": f"El archivo excede el tamaño máximo permitido ({actual_mb:.2f}MB > {max_mb:.2f}MB)"
                }), 413  # Payload Too Large
        except Exception as e:
            logging.error(f"Error al verificar tamaño del archivo: {e}")
            # Continuamos en caso de error, confiando en otras validaciones
        
        try:
            # Crear directorio de usuario si no existe
            user_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            
            # Generar nombre seguro y único
            original_filename = file.filename
            filename = secure_filename(original_filename)
            filename = f"{uuid.uuid4().hex}_{filename}"  # Añadir UUID para garantizar unicidad
            
            # Guardar archivo
            filepath = os.path.join(user_folder, filename)
            file.save(filepath)
            
            # Verificar que el archivo se guardó correctamente
            if not os.path.exists(filepath):
                return jsonify({"error": "Error al guardar el archivo"}), 500
                
            # Obtener el tamaño real del archivo guardado
            file_size = os.path.getsize(filepath)
            
            # Validar mimetype
            mimetype = file.content_type
            if not mimetype or mimetype == 'application/octet-stream':
                # Intentar determinar el mimetype por la extensión
                import mimetypes
                guessed_mimetype = mimetypes.guess_type(original_filename)[0]
                if guessed_mimetype:
                    mimetype = guessed_mimetype
            
            # Crear registro en base de datos
            db_file = File(
                user_id=user_id,
                filename=filename,
                original_filename=original_filename,
                filepath=filepath,
                mimetype=mimetype,
                size=file_size,
                processed=False,
                processing_status='pending'
            )
            
            db.session.add(db_file)
            db.session.commit()
            
            # Si es un archivo procesable (imagen, PDF), ponerlo en cola para OCR
            if db_file.mimetype.startswith('image/') or db_file.mimetype == 'application/pdf':
                # Aquí se podría agregar el archivo a una cola de procesamiento
                # Para simplificar, solo cambiamos el estado
                db_file.processing_status = 'queued'
                db.session.commit()
                
            return jsonify(db_file.to_dict()), 201
        except IOError as e:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            logging.error(f"Error de I/O al guardar el archivo: {e}")
            return jsonify({"error": "Error al guardar el archivo en el servidor"}), 500
        
    except ValueError as e:
        db.session.rollback()
        logging.error(f"Error de validación al subir archivo: {e}")
        return jsonify({"error": "Error en el formato o tipo de los datos enviados"}), 422
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al subir archivo: {e}")
        return jsonify({"error": "Error interno del servidor al procesar el archivo"}), 500


@api_bp.route('/files/<int:file_id>/content', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Descarga un archivo."""
    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not file:
            return jsonify({"error": "Archivo no encontrado"}), 404
            
        # Verificar que el archivo existe en disco
        if not os.path.isfile(file.filepath):
            return jsonify({"error": "Archivo no encontrado en el servidor"}), 404
            
        # Enviar archivo
        return send_file(
            file.filepath,
            mimetype=file.mimetype,
            as_attachment=True,
            download_name=file.original_filename
        )
        
    except Exception as e:
        logging.error(f"Error al descargar archivo {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/<int:file_id>/thumbnail', methods=['GET'])
@jwt_required()
def get_thumbnail(file_id):
    """Obtiene la miniatura de un archivo."""
    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not file:
            return jsonify({"error": "Archivo no encontrado"}), 404
            
        # Verificar si existe miniatura
        if not file.thumbnail_path or not os.path.isfile(file.thumbnail_path):
            return jsonify({"error": "Miniatura no disponible"}), 404
            
        # Enviar miniatura
        return send_file(
            file.thumbnail_path,
            mimetype='image/jpeg'
        )
        
    except Exception as e:
        logging.error(f"Error al obtener miniatura {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/<int:file_id>/process', methods=['POST'])
@jwt_required()
def process_file_async(file_id):
    """Inicia el procesamiento asíncrono de un archivo (OCR, etc.)."""
    import threading
    from flask import url_for

    # Importar la función de procesamiento directamente, ya no es una tarea Celery
    from app.tasks.ocr_tasks import process_ocr 

    def run_ocr_in_background(app, file_id, engine, extra_config):
        """Función que se ejecuta en un hilo para procesar el OCR."""
        with app.app_context():
            try:
                logger.info(f"[Thread] Iniciando procesamiento OCR para el archivo {file_id}")
                process_ocr(file_id=file_id, engine=engine, extra_config=extra_config)
                logger.info(f"[Thread] Procesamiento OCR para el archivo {file_id} completado.")
            except Exception as e:
                logger.error(f"[Thread] Error en el procesamiento OCR para el archivo {file_id}: {e}", exc_info=True)
                # Opcional: Actualizar el estado del archivo a 'failed' en la base de datos
                try:
                    file = File.query.get(file_id)
                    if file:
                        file.processing_status = 'failed'
                        db.session.commit()
                except Exception as db_err:
                    logger.error(f"[Thread] No se pudo actualizar el estado del archivo a 'failed': {db_err}")

    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()

        if not file:
            return jsonify({"error": "Archivo no encontrado"}), 404

        # Verificar si ya hay una tarea en curso para este archivo
        if file.processing_status == 'processing':
            logger.info(f"El procesamiento para el archivo {file_id} ya está en curso.")
            return jsonify({"message": "El procesamiento ya está en curso."}), 409

        # Obtener opciones de la solicitud
        data = request.json or {}
        engine = data.get('engine', 'auto')
        is_whiteboard = data.get('isWhiteboard', False)

        # Lanzar el procesamiento en un hilo separado
        logger.info(f"Iniciando hilo de procesamiento para archivo {file_id} con engine {engine}")
        app_context = current_app._get_current_object()
        thread = threading.Thread(
            target=run_ocr_in_background, 
            args=(app_context, file.id, engine, {'is_whiteboard': is_whiteboard})
        )
        thread.start()

        # Actualizar estado en la base de datos
        file.processing_status = 'processing' # Cambiamos a 'processing' directamente
        file.processed = False
        db.session.commit()

        logger.info(f"Hilo para el archivo {file_id} iniciado. Estado guardado en DB.")

        return jsonify({
            "message": "Procesamiento iniciado en segundo plano"
        }), 202

    except Exception as e:
        logger.error(f"Error al iniciar el procesamiento para el archivo {file_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@api_bp.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Elimina un archivo."""
    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not file:
            return jsonify({"error": "Archivo no encontrado"}), 404
            
        # Eliminar archivo físico
        try:
            if os.path.isfile(file.filepath):
                os.remove(file.filepath)
                
            # Eliminar miniatura si existe
            if file.thumbnail_path and os.path.isfile(file.thumbnail_path):
                os.remove(file.thumbnail_path)
        except OSError as e:
            logging.error(f"Error al eliminar archivo físico: {e}")
        
        # Eliminar registro
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({"message": "Archivo eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar archivo {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/check-google-vision-available', methods=['GET'])
def check_google_vision_available():
    """Verifica la disponibilidad de Google Vision API."""
    try:
        # Importar la variable global del error para mostrarla al usuario
        from ..services.ocr_processor import GOOGLE_VISION_ERROR_REASON
        
        # Crear instancia del procesador OCR
        ocr = OCRProcessor()
        
        # Verificar si Google Vision está disponible (forzando una nueva comprobación)
        google_vision_available = ocr.is_google_vision_available(force_check=True)
        
        response = {
            "available": google_vision_available
        }
        
        # Si no está disponible y tenemos un motivo específico, incluirlo en la respuesta
        if not google_vision_available and GOOGLE_VISION_ERROR_REASON:
            response["error_reason"] = GOOGLE_VISION_ERROR_REASON
            response["troubleshooting"] = [
                "1. Asegúrate de que la API Vision está habilitada en Google Cloud Console",
                "2. Verifica que la cuenta de servicio tiene el rol 'Cloud Vision API User'",
                "3. La variable de entorno GOOGLE_APPLICATION_CREDENTIALS debe apuntar al archivo JSON de credenciales",
                "4. El archivo JSON debe ser válido y tener los permisos correctos"
            ]
            logging.warning(f"Google Vision no disponible: {GOOGLE_VISION_ERROR_REASON}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f"Error al verificar disponibilidad de Google Vision: {e}")
        return jsonify({
            "available": False,
            "error": str(e),
            "troubleshooting": [
                "Ha ocurrido un error inesperado al verificar la disponibilidad de Google Vision.",
                "Revisa los logs del servidor para más información."
            ]
        }), 200  # Devolvemos 200 pero con available=False para indicar que no está disponible

# Alias para el endpoint anterior para mantener compatibilidad con el frontend
@api_bp.route('/files/text-google-vision-available', methods=['GET'])
def text_google_vision_available():
    """Alias para check_google_vision_available para mantener compatibilidad con el frontend."""
    return check_google_vision_available()


@api_bp.route('/files/create-note', methods=['POST'])
@jwt_required()
def create_note_from_ocr():
    """Crea una nueva nota a partir del resultado OCR."""
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        
        # Validar datos mínimos
        if not data.get('ocr_result') or not data.get('title'):
            return jsonify({"error": "Se requiere texto OCR y título"}), 400
            
        # Importar el modelo Note aquí para evitar dependencias circulares
        from ..models import Note, Tag
        
        # Extraer el texto y el file_id del resultado OCR
        ocr_data = data['ocr_result']
        note_content = ocr_data.get('text', '')
        
        # Intentar obtener el file_id desde la URL de la miniatura
        file_id = None
        if ocr_data.get('thumbnail_url'):
            try:
                file_id = int(ocr_data['thumbnail_url'].split('/')[3])
            except (IndexError, ValueError):
                logger.warning(f"No se pudo extraer file_id de {ocr_data['thumbnail_url']}")

        # Crear la nota
        note = Note(
            title=data['title'],
            content=note_content,
            user_id=user_id,
            file_id=file_id,  # Asociar el archivo original
            source_type="ocr"  # Marcar como originada de OCR
        )
        
        # Añadir metadatos adicionales si se proporcionan
        import json
        metadata = {}
        
        if data.get('is_whiteboard'):
            metadata['is_whiteboard'] = True
        
        # Convertir los metadatos a formato JSON si hay alguno
        if metadata:
            note.note_metadata = json.dumps(metadata)
            
        if data.get('summary'):
            note.summary = data['summary']
            
        if data.get('main_topic'):
            note.main_topic = data['main_topic']
        
        # Procesar con IA si se solicita explícitamente
        if data.get('process_ai', False) and len(note_content) > 50:
            # Importar los servicios de IA
            from ..api.notes import summarizer, classifier
            note.process_with_ai(summarizer, classifier)
            
        # Agregar etiquetas si se proporcionan
        if 'tags' in data and isinstance(data['tags'], list):
            for tag_name in data['tags']:
                tag = Tag.get_or_create(tag_name)
                note.tags.append(tag)
                
        # Guardar en la base de datos
        db.session.add(note)
        db.session.commit()
        
        logger.info(f"Nota creada desde OCR: ID={note.id}, Título={note.title}")
        
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear nota desde OCR: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/statistics', methods=['GET'])
@jwt_required()
def get_files_statistics():
    """Obtiene estadísticas sobre los archivos del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Estadísticas básicas
        total_files = File.query.filter_by(user_id=user_id).count()
        processed_files = File.query.filter_by(user_id=user_id, processed=True).count()
        
        # Estadísticas por tipo de archivo
        mimetype_stats = db.session.query(
            db.func.substring(File.mimetype, 1, 5).label('mimetype_type'),
            db.func.count(File.id).label('count')
        ).filter_by(user_id=user_id).group_by('mimetype_type').all()
        
        # Formatear tipos de archivo para mejor lectura
        mimetype_dict = {}
        for mime_prefix, count in mimetype_stats:
            if mime_prefix == 'image':
                mimetype_dict['Imágenes'] = count
            elif mime_prefix == 'appli':
                mimetype_dict['Documentos'] = count
            elif mime_prefix == 'text/':
                mimetype_dict['Texto'] = count
            elif mime_prefix == 'video':
                mimetype_dict['Video'] = count
            elif mime_prefix == 'audio':
                mimetype_dict['Audio'] = count
            else:
                mimetype_dict['Otros'] = count
        
        # Estadísticas por mes - usando to_char para PostgreSQL en lugar de date_format (MySQL)
        try:
            # Para PostgreSQL
            month_stats = db.session.query(
                db.func.to_char(File.uploaded_at, 'YYYY-MM').label('month'),
                db.func.count(File.id).label('count')
            ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
        except Exception as e:
            logging.error(f"Error con func.to_char en files: {e}")
            # Si falla, usar una forma alternativa compatible
            from sqlalchemy.sql.expression import extract
            month_stats = db.session.query(
                (extract('year', File.uploaded_at).cast(db.String) + '-' + 
                 extract('month', File.uploaded_at).cast(db.String).concat('00').substr(1,2)
                ).label('month'),
                db.func.count(File.id).label('count')
            ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
        
        monthly_list = [{'month': month, 'count': count} for month, count in month_stats]
        
        return jsonify({
            'total': total_files,
            'processed': processed_files,
            'processing_ratio': processed_files / total_files if total_files > 0 else 0,
            'by_type': mimetype_dict,
            'monthly': monthly_list
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener estadísticas de archivos: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener estadísticas de archivos: {str(e)}",
            "traceback": error_traceback
        }), 500
