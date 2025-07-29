"""
Script para probar el flujo completo de autenticación con solicitudes HTTP reales.
"""
import os
import sys
import requests
import json

def test_authentication_flow():
    """Prueba el flujo completo de autenticación con el servidor en ejecución"""
    
    # Definir la URL base - asumiendo que el servidor está en ejecución en localhost:5000
    BASE_URL = 'http://localhost:5000'
    
    print("1. Probando login con credenciales válidas...")
    login_response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    
    print(f"Código de estado: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = login_response.json()
        print("✅ Login exitoso!")
        print(f"Usuario: {login_data.get('user', {}).get('username')}")
        print(f"Email: {login_data.get('user', {}).get('email')}")
        print(f"Rol: {login_data.get('user', {}).get('role')}")
        
        # Extraer tokens
        access_token = login_data.get('access_token')
        refresh_token = login_data.get('refresh_token')
        
        if access_token and refresh_token:
            print("\n2. Probando endpoint protegido con token de acceso...")
            protected_response = requests.get(
                f'{BASE_URL}/api/auth/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            print(f"Código de estado: {protected_response.status_code}")
            if protected_response.status_code == 200:
                print("✅ Acceso a endpoint protegido exitoso!")
                print(f"Datos del usuario: {protected_response.json()}")
            else:
                print(f"❌ Error al acceder al endpoint protegido: {protected_response.text}")
            
            print("\n3. Probando renovación de token...")
            refresh_response = requests.post(
                f'{BASE_URL}/api/auth/refresh',
                headers={'Authorization': f'Bearer {refresh_token}'}
            )
            
            print(f"Código de estado: {refresh_response.status_code}")
            if refresh_response.status_code == 200:
                print("✅ Renovación de token exitosa!")
                new_token = refresh_response.json().get('access_token')
                print(f"Nuevo token obtenido: {new_token[:20]}...")
            else:
                print(f"❌ Error al renovar el token: {refresh_response.text}")
        else:
            print("❌ No se obtuvieron tokens en la respuesta de login")
    else:
        print(f"❌ Login fallido: {login_response.text}")

if __name__ == "__main__":
    print("Iniciando prueba del flujo de autenticación...")
    test_authentication_flow()
    print("\nPrueba finalizada.")
