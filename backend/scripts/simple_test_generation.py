#!/usr/bin/env python3
"""
Script simple para probar la generación automática de mapas conceptuales
"""

import sys
import os
import json
import requests
import time

# Configuración del servidor
BASE_URL = "http://localhost:5000"

def simple_test():
    """Prueba simple y directa"""
    
    print("🔍 Probando conexión al servidor...")
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Health check: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # Login directo con datos conocidos
    print("🔑 Haciendo login...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.text}")
            return
        
        # Extraer token
        response_data = login_response.json()
        token = response_data.get('access_token')
        if not token:
            print(f"❌ No hay token en respuesta")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login exitoso")
        
        # Usar una nota existente en lugar de crear una nueva
        print("📋 Obteniendo lista de notas...")
        notes_response = requests.get(f"{BASE_URL}/api/notes", headers=headers, timeout=10)
        
        if notes_response.status_code != 200:
            print(f"❌ Error obteniendo notas: {notes_response.status_code}")
            print(notes_response.text)
            return
        
        notes_data = notes_response.json()
        notes = notes_data.get('notes', [])
        
        if not notes:
            print("⚠️ No hay notas disponibles, creando una...")
            # Crear nota simple
            note_data = {
                "title": "Test IA Map",
                "content": "La inteligencia artificial incluye machine learning, deep learning, procesamiento de lenguaje natural, visión por computadora y robótica. Estos campos están interconectados."
            }
            
            create_response = requests.post(f"{BASE_URL}/api/notes", json=note_data, headers=headers, timeout=10)
            if create_response.status_code not in [200, 201]:
                print(f"❌ Error creando nota: {create_response.status_code}")
                print(create_response.text)
                return
            
            note_id = create_response.json()['id']
            print(f"✅ Nota creada: {note_id}")
        else:
            note_id = notes[0]['id']
            print(f"✅ Usando nota existente: {note_id}")
        
        # Probar generación de mapa conceptual
        print("🤖 Generando mapa conceptual...")
        generate_data = {
            "note_id": note_id,
            "max_concepts": 5
        }
        
        generate_response = requests.post(f"{BASE_URL}/api/graph/generate-from-note", json=generate_data, headers=headers, timeout=30)
        
        print(f"Generate status: {generate_response.status_code}")
        
        if generate_response.status_code != 200:
            print(f"❌ Error generando mapa: {generate_response.text}")
            return
        
        result = generate_response.json()
        print("✅ Mapa conceptual generado!")
        print(f"📊 ID: {result.get('concept_map_id')}")
        print(f"📈 Nodos: {len(result.get('nodes', []))}")
        print(f"🔗 Relaciones: {len(result.get('relations', []))}")
        
        # Verificar en la lista
        print("📋 Verificando mapas disponibles...")
        maps_response = requests.get(f"{BASE_URL}/api/graph/visualization", headers=headers, timeout=60)
        
        if maps_response.status_code == 200:
            response_data = maps_response.json()
            maps_list = response_data.get('recent_maps', [])
            print(f"✅ Total mapas: {len(maps_list)}")
        else:
            print(f"\n❌ Error al obtener mapas: {maps_response.status_code}")
            print(f"Respuesta del servidor: {maps_response.text}\n")
        
        print("🎉 ¡Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
