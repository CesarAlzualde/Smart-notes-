"""
Auth Blueprint para las rutas de autenticación
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Importamos las rutas para que sean registradas con el blueprint
from . import routes
