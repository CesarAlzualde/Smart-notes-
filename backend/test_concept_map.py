#!/usr/bin/env python3
"""
Script de prueba para verificar la generación de mapas conceptuales.
"""

import requests
import json
import sys
import os

# Agregar la carpeta del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_health():
    """Probar el health endpoint"""
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("✅ Backend está funcionando")
            data = response.json()
            print(f"   Servicios disponibles: {', '.join(data.get('services', []))}")
            return True
        else:
            print(f"❌ Backend health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def login_user():
    """Login de usuario para obtener token JWT"""
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ Login exitoso")
            return token
        else:
            print(f"❌ Login falló: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_concept_map_generation(token, note_id=1):
    """Probar la generación de mapa conceptual"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Datos para generar el mapa
    map_data = {
        "note_id": note_id
    }
    
    try:
        print(f"🔄 Intentando generar mapa conceptual para nota {note_id}...")
        response = requests.post(
            "http://localhost:5000/api/graph/generate-from-note", 
            json=map_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mapa conceptual generado exitosamente!")
            print(f"   ID del mapa: {data.get('concept_map_id')}")
            print(f"   Nodos creados: {data.get('stats', {}).get('nodes_created', 0)}")
            print(f"   Relaciones creadas: {data.get('stats', {}).get('edges_created', 0)}")
            return data
        else:
            print(f"❌ Error generando mapa: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en solicitud: {e}")
        return None

def test_get_user_maps(token):
    """Obtener mapas del usuario"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:5000/api/graph/visualization", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mapas encontrados: {len(data.get('maps', []))}")
            for map_info in data.get('maps', [])[:3]:  # Mostrar solo los primeros 3
                print(f"   - {map_info.get('name', 'Sin nombre')} (ID: {map_info.get('id')})")
            return data
        else:
            print(f"❌ Error obteniendo mapas: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en solicitud: {e}")
        return None

def main():
    print("🚀 Iniciando pruebas de mapas conceptuales...")
    print("=" * 50)
    
    # 1. Verificar backend
    if not test_backend_health():
        print("❌ Backend no está disponible. Asegúrate de que esté ejecutándose.")
        return
    
    # 2. Login
    token = login_user()
    if not token:
        print("❌ No se pudo obtener token de autenticación.")
        print("   Verifica que existe un usuario con email: test@example.com")
        return
    
    # 3. Obtener mapas existentes
    print("\n📊 Obteniendo mapas existentes...")
    test_get_user_maps(token)
    
    # 4. Generar nuevo mapa conceptual
    print("\n🧠 Probando generación de mapa conceptual...")
    result = test_concept_map_generation(token, note_id=1)
    
    if result:
        print("\n🎉 ¡Prueba completada exitosamente!")
    else:
        print("\n❌ La generación de mapas falló.")
        print("   Verifica que existe una nota con ID=1 para tu usuario.")

if __name__ == "__main__":
    main()
