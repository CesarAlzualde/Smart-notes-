"""
Script de diagnóstico para probar importaciones específicas y localizar
exactamente qué módulo o blueprint está bloqueando la inicialización.
"""

import os
import sys
import time

# Añadir la carpeta raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=== Script de diagnóstico para importaciones de Flask ===")

print("[1] Importando Flask básico...")
import flask
from flask import Flask
print("✓ Flask importado correctamente")

print("[2] Importando extensiones...")
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
print("✓ Extensiones importadas correctamente")

print("[3] Importando modelos...")
try:
    from backend.app.models import db, User
    print("✓ Modelos importados correctamente")
except Exception as e:
    print(f"❌ Error en modelos: {e}")

print("[4] Importando API blueprint...")
try:
    from backend.app.api import api_bp
    print("✓ API blueprint importado correctamente")
except Exception as e:
    print(f"❌ Error en api_bp: {e}")

print("[5] Importando Health blueprint...")
try:
    from backend.app.api.health import health_bp
    print("✓ Health blueprint importado correctamente")
except Exception as e:
    print(f"❌ Error en health_bp: {e}")

print("[6] Importando JWT Test blueprint...")
try:
    from backend.app.api.jwt_test import jwt_test_bp
    print("✓ JWT Test blueprint importado correctamente")
except Exception as e:
    print(f"❌ Error en jwt_test_bp: {e}")

print("[7] Importando Auth blueprint...")
try:
    from backend.app.auth import auth_bp
    print("✓ Auth blueprint importado correctamente")
except Exception as e:
    print(f"❌ Error en auth_bp: {e}")

print("=== Diagnóstico completo ===")
