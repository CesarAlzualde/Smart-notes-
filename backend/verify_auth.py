"""
Script simple para verificar la configuración JWT y el flujo de autenticación
"""
import os
import sys
from flask_jwt_extended import create_access_token, decode_token
import datetime
import json

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User

print("Iniciando verificación de autenticación JWT...")

# Crear la aplicación con configuración de testing
app = create_app(test_config=True)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['JWT_SECRET_KEY'] = 'test-key-for-jwt'

with app.app_context():
    # Inicializar la base de datos
    db.create_all()
    
    # Crear usuario de prueba si no existe
    if not User.query.filter_by(email='test@example.com').first():
        user = User(
            username='testuser',
            email='test@example.com',
            name='Test User',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print(f"Usuario de prueba creado: {user.email}")
    else:
        user = User.query.filter_by(email='test@example.com').first()
        print(f"Usuario de prueba existente: {user.email}")
    
    # Generar token
    access_token = create_access_token(
        identity={'id': user.id, 'username': user.username, 'role': user.role},
        expires_delta=datetime.timedelta(hours=1)
    )
    
    print(f"\nToken JWT generado correctamente:")
    print(f"Token: {access_token}")
    
    # Decodificar token
    try:
        decoded = decode_token(access_token)
        print("\nToken decodificado correctamente:")
        print(f"Sub: {decoded['sub']}")
        print(f"Exp: {datetime.datetime.fromtimestamp(decoded['exp']).strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nVerificación exitosa: El sistema JWT está configurado correctamente.")
    except Exception as e:
        print(f"\nError al decodificar token: {str(e)}")
        print("El sistema JWT parece tener problemas de configuración.")
