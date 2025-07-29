"""
Modelo para archivos subidos al sistema.
"""

import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..extensions import db

class File(db.Model):
    """Modelo para archivos subidos al sistema."""
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    mimetype = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)  # Tamaño en bytes
    user_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed = Column(Boolean, default=False)  # Indica si el archivo ha sido procesado por OCR/IA
    processing_status = db.Column(db.String(255), default='pending') # pending, processing, completed, failed
    extract_text = Column(Text)  # Texto extraído del archivo (si es OCR)
    thumbnail_path = Column(String(255))  # Ruta a miniatura (si es imagen)
    file_metadata = Column(db.JSON)  # JSON con metadatos adicionales
    
    # Relaciones
    user = relationship("User", backref="files")
    notes = relationship('Note', back_populates='file', cascade='all, delete-orphan') # Relación con las notas
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para APIs."""
        # Log temporal para debugging
        import logging
        logging.info(f"[DEBUG] to_dict() para archivo {self.id}: extract_text len={len(self.extract_text) if self.extract_text else 0}, status={self.processing_status}")
        
        result = {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'mimetype': self.mimetype,
            'size': self.size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed': self.processed,
            'processing_status': self.processing_status,
            'has_thumbnail': bool(self.thumbnail_path),
            'has_text': bool(self.extract_text),
            'extract_text': self.extract_text,
            'file_metadata': self.file_metadata,
            'user_id': self.user_id
        }
        
        logging.info(f"[DEBUG] to_dict() resultado: extract_text incluido = {'extract_text' in result}")
        return result
