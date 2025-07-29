"""
Pruebas para la autenticación de la aplicación.
Incluye pruebas para login, registro, endpoints protegidos y renovación de tokens.
"""
import json
import pytest
import time

def test_login_success(client, test_user):
    """Prueba un inicio de sesión exitoso."""
    response = client.post('/api/auth/login', 
        json={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['username'] == 'testuser'

def test_login_invalid_credentials(client, test_user):
    """Prueba un inicio de sesión fallido."""
    response = client.post('/api/auth/login', 
        json={
            'email': 'test@example.com',
            'password': 'wrong_password'
        }
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_login_missing_fields(client):
    """Prueba un inicio de sesión con campos faltantes."""
    # Sin email
    response = client.post('/api/auth/login', 
        json={'password': 'password123'}
    )
    assert response.status_code == 400
    
    # Sin contraseña
    response = client.post('/api/auth/login', 
        json={'email': 'test@example.com'}
    )
    assert response.status_code == 400

def test_register_success(client):
    """Prueba un registro exitoso."""
    response = client.post('/api/auth/register', 
        json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'name': 'New User'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Usuario registrado correctamente'

def test_register_duplicate(client, test_user):
    """Prueba un registro con email duplicado."""
    response = client.post('/api/auth/register', 
        json={
            'username': 'different',
            'email': 'test@example.com',  # Email ya existente
            'password': 'password123',
            'name': 'Duplicate User'
        }
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_protected_endpoint_without_token(client):
    """Prueba un endpoint protegido sin token."""
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_protected_endpoint_with_token(client, auth_token):
    """Prueba un endpoint protegido con token."""
    response = client.get('/api/auth/me', 
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'test@example.com'

def test_refresh_token(client, test_user):
    """Prueba la renovación de un token."""
    # Primer login para obtener tokens
    login_response = client.post('/api/auth/login', 
        json={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    data = json.loads(login_response.data)
    refresh_token = data['refresh_token']
    
    # Renovar token
    response = client.post('/api/auth/refresh', 
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
