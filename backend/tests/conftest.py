"""
Configuración y fixtures para pruebas con pytest.
Este archivo define los objetos reutilizables para pruebas como la app, cliente HTTP y usuarios.
"""
import pytest
from app import create_app
from app.models import db, User
import os

@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    # Usar base de datos en memoria para las pruebas
    app = create_app({
        'TESTING': True, 
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-key-for-jwt',
        'UPLOAD_FOLDER': os.path.join(os.getcwd(), 'test_uploads')
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente HTTP para pruebas."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Crea un usuario de prueba."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            name='Test User',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    """Crea un usuario administrador de prueba."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            name='Admin User',
            role='admin'
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_token(client, test_user):
    """Obtiene un token de autenticación para el usuario de prueba."""
    response = client.post('/api/auth/login', 
        json={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    data = response.get_json()
    return data['access_token']
