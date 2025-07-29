#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear mapas conceptuales de prueba en Neo4j.
Sirve para validar la funcionalidad del backend.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()

# Configuración
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def login_user():
    """Login con usuario de prueba y obtener token JWT"""
    print("\n🔑 Iniciando sesión...")
    
    login_data = {
        "email": "test_new@example.com", 
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login exitoso! Token: {token[:15]}...")
            return token
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error conectando con API: {str(e)}")
        return None

def create_test_map(token, name, tema_principal):
    """Crear mapa conceptual de prueba con conceptos relacionados"""
    if not token:
        print("❌ No se puede crear mapa sin token")
        return None
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generar conceptos y relaciones basados en el tema
    concepts = []
    relations = []
    
    # Definir conceptos principales
    if tema_principal == "Programación":
        concepts = [
            {"id": "prog_1", "label": "Programación", "type": "main", "description": "Arte de crear instrucciones para computadoras"},
            {"id": "prog_2", "label": "Lenguajes", "type": "subtopic", "description": "Diferentes sintaxis para programar"},
            {"id": "prog_3", "label": "Algoritmos", "type": "subtopic", "description": "Secuencias de pasos para resolver problemas"},
            {"id": "prog_4", "label": "Python", "type": "example", "description": "Lenguaje de alto nivel muy popular"},
            {"id": "prog_5", "label": "JavaScript", "type": "example", "description": "Lenguaje de programación web"}
        ]
        
        relations = [
            {"source": "prog_1", "target": "prog_2", "label": "incluye", "weight": 0.9},
            {"source": "prog_1", "target": "prog_3", "label": "utiliza", "weight": 0.85},
            {"source": "prog_2", "target": "prog_4", "label": "ejemplo", "weight": 0.8},
            {"source": "prog_2", "target": "prog_5", "label": "ejemplo", "weight": 0.8},
            {"source": "prog_3", "target": "prog_4", "label": "implementado en", "weight": 0.7},
        ]
    elif tema_principal == "Inteligencia Artificial":
        concepts = [
            {"id": "ia_1", "label": "Inteligencia Artificial", "type": "main", "description": "Simulación de procesos de inteligencia humana por máquinas"},
            {"id": "ia_2", "label": "Machine Learning", "type": "subtopic", "description": "Capacidad de aprender sin programación explícita"},
            {"id": "ia_3", "label": "Redes Neuronales", "type": "subtopic", "description": "Modelos inspirados en el cerebro"},
            {"id": "ia_4", "label": "GPT", "type": "example", "description": "Modelo de lenguaje generativo"},
            {"id": "ia_5", "label": "Visión Computacional", "type": "subtopic", "description": "Permitir a las máquinas ver"}
        ]
        
        relations = [
            {"source": "ia_1", "target": "ia_2", "label": "incluye", "weight": 0.9},
            {"source": "ia_1", "target": "ia_5", "label": "abarca", "weight": 0.85},
            {"source": "ia_2", "target": "ia_3", "label": "utiliza", "weight": 0.8},
            {"source": "ia_3", "target": "ia_4", "label": "ejemplo", "weight": 0.75},
            {"source": "ia_5", "target": "ia_3", "label": "usa", "weight": 0.7},
        ]
    elif tema_principal == "Historia de España":
        concepts = [
            {"id": "esp_1", "label": "Historia de España", "type": "main", "description": "Evolución histórica de España"},
            {"id": "esp_2", "label": "Reino Visigodo", "type": "period", "description": "Siglos V-VIII"},
            {"id": "esp_3", "label": "Al-Andalus", "type": "period", "description": "Período islámico 711-1492"},
            {"id": "esp_4", "label": "Reyes Católicos", "type": "historical", "description": "Isabel y Fernando"},
            {"id": "esp_5", "label": "Guerra Civil", "type": "event", "description": "Conflicto 1936-1939"}
        ]
        
        relations = [
            {"source": "esp_1", "target": "esp_2", "label": "incluye", "weight": 0.8},
            {"source": "esp_1", "target": "esp_3", "label": "comprende", "weight": 0.85},
            {"source": "esp_1", "target": "esp_4", "label": "destaca", "weight": 0.75},
            {"source": "esp_1", "target": "esp_5", "label": "incluye", "weight": 0.7},
            {"source": "esp_3", "target": "esp_4", "label": "finaliza con", "weight": 0.65},
        ]
    
    # Crear el mapa conceptual
    map_data = {
        "name": name,
        "description": f"Mapa conceptual sobre {tema_principal}",
        "concepts": concepts,
        "relations": relations
    }
    
    try:
        print(f"\n🗺️ Creando mapa conceptual: {name}")
        response = requests.post(f"{API_BASE}/graph/save", json=map_data, headers=headers, timeout=15)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ Mapa creado correctamente: ID {result.get('id', 'no disponible')}")
            return result
        else:
            print(f"❌ Error creando mapa: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en la solicitud: {str(e)}")
        return None

def list_user_maps(token):
    """Listar los mapas conceptuales del usuario"""
    if not token:
        return None
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("\n📋 Listando mapas conceptuales...")
        response = requests.get(f"{API_BASE}/graph/visualization", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            maps = data.get('recent_maps', [])
            print(f"✅ Mapas encontrados: {len(maps)}")
            
            for i, map_item in enumerate(maps):
                print(f"  {i+1}. {map_item.get('name', 'Sin nombre')} (ID: {map_item.get('id', 'N/A')})")
                
            # Mostrar estadísticas si están disponibles
            stats = data.get('statistics', {})
            if stats:
                print("\n📊 Estadísticas:")
                print(f"  - Total mapas: {stats.get('total_maps', 'N/A')}")
                print(f"  - Total conceptos: {stats.get('total_concepts', 'N/A')}")
                print(f"  - Total relaciones: {stats.get('total_relations', 'N/A')}")
                
            return maps
        else:
            print(f"❌ Error listando mapas: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en la solicitud: {str(e)}")
        return None

def main():
    """Función principal"""
    print("🧪 CREANDO MAPAS CONCEPTUALES DE PRUEBA")
    print("=" * 50)
    
    # Iniciar sesión
    token = login_user()
    if not token:
        print("❌ No se pudo iniciar sesión. Saliendo...")
        sys.exit(1)
    
    # Crear mapas conceptuales de prueba
    create_test_map(token, "Fundamentos de Programación", "Programación")
    time.sleep(1)  # Pequeña pausa para evitar problemas
    create_test_map(token, "Introducción a la IA", "Inteligencia Artificial")
    time.sleep(1)
    create_test_map(token, "Historia española", "Historia de España")
    
    # Listar mapas creados
    maps = list_user_maps(token)
    
    print("\n✅ PROCESO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
