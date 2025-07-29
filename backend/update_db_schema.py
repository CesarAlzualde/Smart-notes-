"""
Script para actualizar el esquema de la base de datos
Agrega el campo note_metadata a la tabla notes
"""
from sqlalchemy import inspect, text
from app import create_app
from app.models import db
from flask import current_app
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database_schema():
    """Actualiza el esquema de la base de datos con el nuevo campo note_metadata"""
    try:
        app = create_app()
        with app.app_context():
            # Verificar si la columna note_metadata ya existe
            inspector = inspect(db.engine)
            note_metadata_exists = False
            for column in inspector.get_columns('notes'):
                if column['name'] == 'note_metadata':
                    note_metadata_exists = True
                    break
            
            # Si la columna note_metadata no existe, agregarla
            if not note_metadata_exists:
                logger.info("Agregando columna note_metadata a la tabla notes...")
                db.session.execute(text("ALTER TABLE notes ADD COLUMN note_metadata TEXT"))
                db.session.commit()
                logger.info("✅ Columna note_metadata agregada correctamente")
            else:
                logger.info("La columna note_metadata ya existe, no es necesario actualizarla")
            
            logger.info("Esquema de la base de datos actualizado correctamente")
            
    except Exception as e:
        logger.error(f"Error actualizando el esquema de la base de datos: {e}")
        raise

if __name__ == "__main__":
    update_database_schema()
