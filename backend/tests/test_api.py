"""
Pruebas para los endpoints principales de la API.
Verifica el funcionamiento de los endpoints de notas, archivos y etiquetas.
"""
import json
import os
import io
from werkzeug.datastructures import FileStorage

def test_get_notes_unauthorized(client):
    """Prueba obtener notas sin autenticación."""
    response = client.get('/api/notes')
    assert response.status_code == 401

def test_get_notes_empty(client, auth_token):
    """Prueba obtener notas cuando no hay ninguna."""
    response = client.get('/api/notes', 
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'notes' in data
    assert len(data['notes']) == 0

def test_create_note(client, auth_token):
    """Prueba crear una nota."""
    response = client.post('/api/notes',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Nota de prueba',
            'content': 'Contenido de prueba',
            'tags': ['test', 'prueba']
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert 'title' in data
    assert data['title'] == 'Nota de prueba'

def test_get_notes_after_creation(client, auth_token):
    """Prueba obtener notas después de crear una."""
    # Primero crear una nota
    client.post('/api/notes',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Nota de prueba',
            'content': 'Contenido de prueba',
            'tags': ['test', 'prueba']
        }
    )
    
    # Luego obtener las notas
    response = client.get('/api/notes', 
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'notes' in data
    assert len(data['notes']) > 0
    assert data['notes'][0]['title'] == 'Nota de prueba'

def test_upload_file_without_token(client):
    """Prueba subir un archivo sin autenticación."""
    data = {
        'file': (io.BytesIO(b"test file content"), 'test.txt')
    }
    response = client.post('/api/files', 
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 401

def test_upload_file(client, auth_token, app):
    """Prueba subir un archivo."""
    data = {}
    data['file'] = FileStorage(
        stream=io.BytesIO(b"test file content"),
        filename='test.txt',
        content_type='text/plain',
    )
    
    response = client.post('/api/files',
        headers={'Authorization': f'Bearer {auth_token}'},
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert 'filename' in data
    assert data['filename'] == 'test.txt'

    # Verificar que el archivo fue creado en el sistema de archivos
    # (Solo si no estamos usando mocks)
    upload_path = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_path):
        file_path = os.path.join(upload_path, data['id'])
        assert os.path.exists(file_path)

def test_get_tags(client, auth_token):
    """Prueba obtener etiquetas."""
    # Primero crear una nota con etiquetas
    client.post('/api/notes',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Nota con etiquetas',
            'content': 'Contenido de prueba',
            'tags': ['test', 'api', 'etiquetas']
        }
    )
    
    # Luego obtener las etiquetas
    response = client.get('/api/tags',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tags' in data
    # Verificar que al menos las etiquetas que creamos existan
    tag_names = [tag['name'] for tag in data['tags']]
    assert 'test' in tag_names
    assert 'api' in tag_names
    assert 'etiquetas' in tag_names
