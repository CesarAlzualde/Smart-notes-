#!/usr/bin/env python3
"""
Script para probar la generación automática de mapas conceptuales
"""

import sys
import os
import json
import requests

# Añadir el directorio del backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración del servidor
BASE_URL = "http://localhost:5000"

def test_auth_and_generate():
    """Prueba la autenticación y generación de mapas"""
    
    # 1. Login
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print("🔑 Intentando hacer login...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    print(f"Login status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print("Creando usuario de prueba...")
        
        # Crear usuario de prueba
        register_data = {
            "username": "testuser",
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Register status: {register_response.status_code}")
        print(f"Register response: {register_response.text}")
        
        if register_response.status_code not in [200, 201]:
            print("❌ No se pudo crear el usuario")
            return
        
        # Intentar login de nuevo
        print("🔑 Intentando login nuevamente...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ Login falló después de registro")
            return
    
    try:
        response_data = login_response.json()
        token = response_data.get('token') or response_data.get('access_token')
        if not token:
            print(f"❌ No se encontró token en respuesta: {response_data}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login exitoso")
    except Exception as e:
        print(f"❌ Error procesando respuesta de login: {e}")
        return
    
    # 2. Crear una nota de prueba
    note_data = {
        "title": "Historia de la Inteligencia Artificial",
        "content": """La inteligencia artificial (IA) es una rama de la informática que se ocupa de la creación de sistemas que pueden realizar tareas que normalmente requieren inteligencia humana. Su historia se remonta a los años 1950.

Los primeros trabajos en IA se centraron en problemas como el juego y la resolución de problemas lógicos. Alan Turing propuso el famoso Test de Turing en 1950 para evaluar la capacidad de una máquina de exhibir comportamiento inteligente.

En 1956, John McCarthy organizó la conferencia de Dartmouth, donde se acuñó el término "inteligencia artificial". Los participantes incluían a Marvin Minsky, Nathaniel Rochester y Claude Shannon.

Durante las décadas de 1960 y 1970, hubo grandes avances en sistemas expertos y procesamiento de lenguaje natural. Sin embargo, también hubo períodos de "invierno de la IA" debido a expectativas no cumplidas y limitaciones de hardware.

En los años 1980 y 1990, el aprendizaje automático comenzó a ganar prominencia, especialmente con el desarrollo de redes neuronales y algoritmos de retropropagación.

El siglo XXI ha visto explosivos avances en deep learning, especialmente después de 2012 con el éxito de las redes neuronales convolucionales en reconocimiento de imágenes. Hoy en día, la IA se aplica en múltiples campos como visión por computadora, procesamiento de lenguaje natural, robótica y más."""
    }
    
    print("📝 Creando nota de prueba...")
    note_response = requests.post(f"{BASE_URL}/api/notes", json=note_data, headers=headers)
    
    if note_response.status_code not in [200, 201]:
        print(f"❌ Error creando nota: {note_response.status_code}")
        print(note_response.text)
        return
    
    note_id = note_response.json()['id']
    print(f"✅ Nota creada con ID: {note_id}")
    
    # 3. Generar mapa conceptual automático
    generate_data = {
        "note_id": note_id,
        "max_concepts": 10
    }
    
    print("🤖 Generando mapa conceptual con IA...")
    generate_response = requests.post(f"{BASE_URL}/api/graph/auto-generate", json=generate_data, headers=headers)
    
    if generate_response.status_code != 200:
        print(f"❌ Error generando mapa: {generate_response.status_code}")
        print(generate_response.text)
        return
    
    result = generate_response.json()
    print("✅ Mapa conceptual generado exitosamente!")
    print(f"📊 Mapa ID: {result.get('concept_map_id')}")
    print(f"📈 Nodos: {len(result.get('nodes', []))}")
    print(f"🔗 Relaciones: {len(result.get('relations', []))}")
    
    # 4. Verificar que el mapa aparece en la lista de mapas del usuario
    print("📋 Verificando lista de mapas...")
    maps_response = requests.get(f"{BASE_URL}/api/graph/visualization", headers=headers)
    
    if maps_response.status_code == 200:
        maps = maps_response.json()
        print(f"✅ Mapas en lista: {len(maps.get('concept_maps', []))}")
        for map_info in maps.get('concept_maps', []):
            print(f"  - {map_info['name']} (ID: {map_info['id']}, Nodos: {map_info.get('node_count', 0)})")
    else:
        print(f"❌ Error obteniendo mapas: {maps_response.status_code}")
    
    print("\n🎉 Prueba completada!")

if __name__ == "__main__":
    test_auth_and_generate()
