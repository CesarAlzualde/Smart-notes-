"""
Modelo para notas del sistema.
Incluye la clase Note y tablas de asociación con etiquetas y tópicos.
"""

import datetime
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..extensions import db
# Tabla de asociación entre notas y etiquetas
note_tag = Table(
    'note_tag',
    db.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Tabla de asociación entre notas y tópicos
note_topic = Table(
    'note_topic',
    db.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), primary_key=True)
)


class Note(db.Model):
    """Modelo para notas del sistema."""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    main_topic = Column(String(100))
    main_topic_score = Column(Float)
    source_type = Column(String(50))  # "text", "image", "pdf"
    image_url = Column(String(255))  # URL o ruta a la miniatura o imagen original
    note_metadata = Column(Text)  # Campo para almacenar metadatos en formato JSON
    analysis_cache = db.Column(db.JSON)  # Para almacenar en caché los resultados del análisis
    embedding = db.Column(db.JSON, nullable=True)  # Para almacenar el vector de embedding semántico formato JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True) # Clave foránea a la tabla de archivos
    
    # Relaciones
    user = relationship("User", back_populates="notes")
    file = relationship("File", back_populates="notes") # Relación con el archivo de origen
    tags = relationship("Tag", secondary=note_tag, back_populates="notes")
    topics = relationship("Topic", secondary=note_topic, back_populates="notes")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para APIs."""
        created_date = self.created_at
        updated_date = self.updated_at

        image_url = self.image_url
        if image_url and not image_url.startswith(('http://', 'https://', '/')):
            image_url = f'/{image_url}'

        metadata_dict = {}
        if self.note_metadata:
            try:
                import json
                metadata_dict = json.loads(self.note_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata_dict = {'raw': self.note_metadata}

        final_dict = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'main_topic': self.main_topic,
            'main_topic_score': self.main_topic_score,
            'source_type': self.source_type,
            'image_url': image_url,
            'metadata': metadata_dict,
            'created_at': created_date.isoformat() if created_date else None,
            'updated_at': updated_date.isoformat() if updated_date else None,
            'created_date': created_date.strftime('%Y-%m-%d') if created_date else None,
            'created_time': created_date.strftime('%H:%M') if created_date else None,
            'created_formatted': created_date.strftime('%d %b %Y, %H:%M') if created_date else None,
            'updated_formatted': updated_date.strftime('%d %b %Y, %H:%M') if updated_date else None,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'tags': [tag.name for tag in self.tags],
            'has_image': bool(image_url),
            'length': len(self.content) if self.content else 0,
        }

        # Añadir campos de IA desde metadata para compatibilidad con el frontend
        final_dict['ai_keywords'] = metadata_dict.get('ai_keywords', [])
        final_dict['ai_sentiment'] = metadata_dict.get('ai_sentiment')
        final_dict['ai_analysis_ready'] = metadata_dict.get('ai_analysis_ready', bool(self.summary))

        return final_dict
    
    def process_with_ai(self, summarizer, classifier) -> None:
        """Procesa la nota con IA para generar resumen y clasificación."""
        # Asegurarse de que haya un resumen y tema por defecto aunque falle la IA
        if not self.summary:
            self.summary = "Resumen no disponible actualmente."
        
        if not self.main_topic:
            self.main_topic = "General"
            self.main_topic_score = 1.0
        
        # Si los modelos no están disponibles, salir temprano
        if not summarizer or not classifier:
            print("Modelos de IA no disponibles, usando valores predeterminados")
            return
            
        try:
            # Generar resumen si el contenido es suficiente
            if len(self.content) > 100:
                summary_result = summarizer.generate_summary(self.content)
                if summary_result and "summary_text" in summary_result:
                    self.summary = summary_result["summary_text"]
                elif summary_result and "error" in summary_result:
                    logging.error(f"Error from summarizer: {summary_result['error']}")
            else:
                self.summary = "Texto demasiado corto para generar un resumen."
            
            # Clasificar el texto
            topics = classifier.classify_text(self.content, top_n=3)
            if topics and len(topics) > 0:
                self.main_topic = topics[0][0]
                self.main_topic_score = float(topics[0][1])
                
                # Agregar etiquetas automáticas basadas en los temas
                from .tag import Tag  # Importación local para evitar ciclo
                for topic_name, score in topics:
                    if score > 0.5:  # Solo agregar temas con score alto
                        tag = Tag.get_or_create(topic_name)
                        if tag not in self.tags:
                            self.tags.append(tag)
                            
        except Exception as e:
            # Log el error pero continuar con valores predeterminados
            logging.error(f"Error al procesar nota con IA: {e}")
            # Ya tenemos valores por defecto configurados al inicio
            # de la función, así que continuamos sin más procesamiento


def add_topics_as_tags(note, topic_names):
    """
    Añade tópicos como etiquetas a la nota.
    
    Args:
        note: Objeto Note al que añadir las etiquetas
        topic_names: Lista de nombres de tópicos a añadir como etiquetas
    """
    from .tag import Tag  # Importación local para evitar ciclo
    
    for topic_name in topic_names:
        # Normalizar nombre del tópico
        normalized_name = topic_name.strip().capitalize()
        if not normalized_name:
            continue
            
        # Buscar o crear la etiqueta
        tag = Tag.get_or_create(normalized_name)
        
        # Añadir solo si no existe ya
        if tag not in note.tags:
            note.tags.append(tag)
    
    # Guardar cambios en la base de datos
    from ..extensions import db
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al guardar etiquetas derivadas de tópicos: {e}")

