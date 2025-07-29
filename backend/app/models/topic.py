"""
Modelo para tópicos/temas principales de las notas.
"""

import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from ..extensions import db
from .note import note_topic

class Topic(db.Model):
    """Modelo para tópicos/temas principales de las notas."""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relación con notas (muchas notas pueden tener este tema)
    notes = relationship("Note", secondary=note_topic, back_populates="topics")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para APIs."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'note_count': len(self.notes) if self.notes else 0
        }
    
    @classmethod
    def get_or_create(cls, name: str) -> 'Topic':
        """Obtiene un topic existente o crea uno nuevo."""
        topic = cls.query.filter_by(name=name).first()
        if not topic:
            topic = cls(name=name)
            db.session.add(topic)
            # No hacemos commit aquí, se debe hacer desde el contexto que llama
        return topic
