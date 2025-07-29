"""
Modelo para etiquetas de notas.
"""

import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from ..extensions import db
from .note import note_tag

class Tag(db.Model):
    """Modelo para etiquetas de notas."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relaciones
    notes = relationship("Note", secondary=note_tag, back_populates="tags")
    
    @classmethod
    def get_or_create(cls, name: str) -> 'Tag':
        """Obtiene una etiqueta existente o crea una nueva."""
        tag = cls.query.filter_by(name=name).first()
        if not tag:
            tag = cls(name=name)
            db.session.add(tag)
            # No hacemos commit aquí, se debe hacer desde el contexto que llama
        return tag
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para APIs."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'note_count': len(self.notes)
        }
