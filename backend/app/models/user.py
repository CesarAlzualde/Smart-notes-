"""
Modelo para usuarios del sistema.
Incluye métodos para autenticación y seguridad.
"""

import datetime
from typing import Dict, Any
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..extensions import db

class User(db.Model):
    """Modelo para usuarios del sistema."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    # Campos para roles y seguridad
    role = Column(String(20), default='student')  # 'admin', 'teacher', 'student'
    security_question = Column(String(255), nullable=True)
    security_answer_hash = Column(String(255), nullable=True)
    recovery_code = Column(String(20), nullable=True)
    recovery_code_expiry = Column(DateTime, nullable=True)
    # Relaciones
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Establece el hash de la contraseña."""
        # Asegurarse de que la contraseña sea una cadena de texto
        if password is None:
            raise ValueError("La contraseña no puede ser None")
        password_str = str(password)
        self.password_hash = pbkdf2_sha256.hash(password_str)
    
    def verify_password(self, password: str) -> bool:
        """Verifica la contraseña contra el hash almacenado."""
        # Asegurarse de que la contraseña sea una cadena de texto
        if password is None or self.password_hash is None:
            return False
        password_str = str(password)
        try:
            return pbkdf2_sha256.verify(password_str, self.password_hash)
        except Exception as e:
            print(f"Error al verificar contraseña: {e}")
            return False
    
    def set_security_answer(self, answer: str) -> None:
        """Almacena el hash de la respuesta de seguridad.
        
        Args:
            answer: La respuesta en texto plano
        """
        if answer:
            self.security_answer_hash = pbkdf2_sha256.hash(answer.lower().strip())
    
    def verify_security_answer(self, answer: str) -> bool:
        """Verifica la respuesta contra el hash almacenado.
        
        Args:
            answer: La respuesta a verificar
            
        Returns:
            bool: True si la respuesta es correcta, False en caso contrario
        """
        if not self.security_answer_hash:
            return False
        return pbkdf2_sha256.verify(answer.lower().strip(), self.security_answer_hash)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para APIs."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'has_security_question': bool(self.security_question)
        }
