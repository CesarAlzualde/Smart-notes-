"""
Inicialización de modelos de base de datos
"""
# Importar modelos para que puedan ser importados desde otros módulos.
from .user import User
from .file import File
from .note import Note, note_tag, note_topic
from .tag import Tag
from .topic import Topic
