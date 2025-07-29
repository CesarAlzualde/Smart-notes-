#!/usr/bin/env python3
"""
Script para crear una nota de prueba en la base de datos.
"""

import sys
import os
import logging

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.note import Note
from app.models.user import User

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_note():
    """Crear una nota de prueba"""
    try:
        app = create_app()
        
        with app.app_context():
            # Buscar el usuario de prueba
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                logger.error("Usuario test@example.com no encontrado. Ejecuta create_test_user.py primero.")
                return None
            
            # Verificar si ya existe una nota
            existing_note = Note.query.filter_by(user_id=user.id).first()
            if existing_note:
                logger.info(f"Ya existe una nota (ID: {existing_note.id}) para el usuario {user.username}")
                return existing_note
            
            # Crear nueva nota
            note_content = """
            **Inteligencia Artificial y Machine Learning**
            
            La inteligencia artificial (IA) es una rama de las ciencias de la computación que se centra en crear sistemas capaces de realizar tareas que típicamente requieren inteligencia humana. Algunos conceptos clave incluyen:
            
            **Machine Learning:**
            - Aprendizaje supervisado: algoritmos que aprenden de datos etiquetados
            - Aprendizaje no supervisado: encuentran patrones en datos sin etiquetas
            - Redes neuronales: modelos inspirados en el cerebro humano
            
            **Aplicaciones:**
            - Procesamiento de lenguaje natural (NLP)
            - Visión por computadora
            - Sistemas de recomendación
            - Vehículos autónomos
            
            **Conceptos importantes:**
            - Big Data: manejo de grandes volúmenes de información
            - Deep Learning: subcampo del ML con redes neuronales profundas
            - Algoritmos de optimización
            - Ética en IA: consideraciones sobre sesgo y privacidad
            
            La IA está transformando industrias como la medicina, educación, finanzas y tecnología, creando nuevas oportunidades y desafíos.
            """
            
            note = Note(
                title="Introducción a la Inteligencia Artificial",
                content=note_content,
                user_id=user.id
            )
            
            db.session.add(note)
            db.session.commit()
            
            logger.info(f"✅ Nota creada exitosamente (ID: {note.id}) para usuario {user.username}")
            return note
            
    except Exception as e:
        logger.error(f"Error creando nota de prueba: {e}")
        return None

if __name__ == "__main__":
    logger.info("Creando nota de prueba...")
    note = create_test_note()
    if note:
        logger.info("Proceso completado.")
    else:
        logger.error("Fallo en la creación de la nota.")
