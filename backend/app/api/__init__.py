"""
API Blueprint para las rutas de la API
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importamos las rutas para que sean registradas con el blueprint
from . import notes, users, analysis, tags, topics, files, graph
