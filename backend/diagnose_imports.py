"""
Script de diagnóstico para identificar qué módulos están causando bloqueos en la inicialización.
Este script importa gradualmente diferentes módulos de la aplicación para identificar cuál
está causando que el servidor se bloquee durante el arranque.
"""

import sys
import os
import time

# Añadir el directorio raíz al path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

print("Iniciando diagnóstico de imports...")

# Importaciones básicas de Flask y configuración
print("[1/10] Importando Flask y configuración básica...")
import flask
from flask import Flask
print("✓ Flask importado correctamente")

# Importar SQLAlchemy
print("[2/10] Importando SQLAlchemy...")
from flask_sqlalchemy import SQLAlchemy
print("✓ SQLAlchemy importado correctamente")

# Importar JWT Extended
print("[3/10] Importando JWT Extended...")
from flask_jwt_extended import JWTManager
print("✓ JWT Extended importado correctamente")

# Importar modelos
print("[4/10] Importando modelos...")
try:
    from app.models import db, User
    print("✓ Modelos importados correctamente")
except Exception as e:
    print(f"❌ Error importando modelos: {e}")

# Importar configuración de la app
print("[5/10] Importando configuración de la app...")
try:
    from app import create_app
    print("✓ Configuración de la app importada correctamente")
except Exception as e:
    print(f"❌ Error importando configuración de la app: {e}")

# Importar rutas de autenticación
print("[6/10] Importando rutas de autenticación...")
try:
    from app.auth import routes as auth_routes
    print("✓ Rutas de autenticación importadas correctamente")
except Exception as e:
    print(f"❌ Error importando rutas de autenticación: {e}")

# Importar procesador OCR (problema conocido anteriormente)
print("[7/10] Importando procesador OCR...")
try:
    print("  Importando módulo...")
    from app.services import ocr_processor
    print("  Módulo importado, probando disponibilidad de Google Vision...")
    vision_available = ocr_processor._check_google_vision_available()
    print(f"  ✓ Disponibilidad de Google Vision: {vision_available}")
except Exception as e:
    print(f"❌ Error importando procesador OCR: {e}")

# Importar summarizer de texto (problema conocido anteriormente)
print("[8/10] Importando summarizer de texto...")
try:
    print("  Importando módulo...")
    from app.services import text_summarizer
    print("  Módulo importado correctamente")
    # No crear instancia para evitar cargar modelos
except Exception as e:
    print(f"❌ Error importando summarizer de texto: {e}")

# Importar rutas de la API
print("[9/10] Importando rutas de la API...")
try:
    from app.api import routes as api_routes
    print("✓ Rutas de la API importadas correctamente")
except Exception as e:
    print(f"❌ Error importando rutas de la API: {e}")

# Importar rutas de archivos
print("[10/10] Importando rutas de archivos...")
try:
    from app.files import routes as files_routes
    print("✓ Rutas de archivos importadas correctamente")
except Exception as e:
    print(f"❌ Error importando rutas de archivos: {e}")

print("\nDiagnóstico completado. Si no hay mensajes de error arriba, todos los módulos se importaron correctamente.")
print("Si el script se bloqueó en algún punto, el último mensaje impreso indicará qué módulo está causando el problema.")
