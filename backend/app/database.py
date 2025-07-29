"""
Módulo para gestión de sesiones de base de datos SQLAlchemy.
Proporciona utilidades para manejar sesiones DB fuera del contexto de solicitud.
"""
import contextlib
from typing import Generator
from sqlalchemy.orm import Session

from .extensions import db

@contextlib.contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Obtiene una sesión de base de datos y la gestiona como un context manager.
    
    Uso:
        with get_session() as session:
            result = session.query(Model).filter(Model.id == 1).first()
    
    Returns:
        Generator[Session]: Sesión de SQLAlchemy administrada por context manager.
    """
    session = db.session
    try:
        # Establecer savepoint para posible rollback
        session.begin_nested()
        yield session
        # Confirmar la transacción si no hay excepciones
        session.commit()
    except Exception as e:
        # Hacer rollback en caso de excepción
        session.rollback()
        raise e
    finally:
        # Cerrar sesión (aunque en Flask-SQLAlchemy esto es manejado por la extensión)
        # En caso de contextos independientes, descomentar: session.close()
        pass
