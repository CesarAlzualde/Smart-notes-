#!/usr/bin/env python3
"""
Script para verificar la configuración de Google Vision API
"""

import os
import sys
import json
from pathlib import Path

def test_google_vision_credentials():
    """Verificar credenciales de Google Vision API"""
    print("🔍 VERIFICACIÓN GOOGLE VISION API")
    print("=" * 50)
    
    # Rutas posibles para credenciales
    base_path = Path(__file__).parent.parent
    backend_path = Path(__file__).parent
    possible_paths = [
        backend_path / "config" / "google-vision-key.json",  # Esta es la correcta
        base_path / "credentials" / "google-vision-key.json",
        base_path / "backend" / "credentials" / "google-vision-key.json",
        base_path / "config" / "google-vision-key.json",
    ]
    
    print("🔎 Buscando archivo de credenciales...")
    credentials_found = False
    credentials_path = None
    
    for path in possible_paths:
        print(f"   Verificando: {path}")
        if path.exists():
            print(f"   ✅ Encontrado en: {path}")
            credentials_found = True
            credentials_path = path
            break
        else:
            print(f"   ❌ No encontrado")
    
    if not credentials_found:
        print("\n❌ CREDENCIALES NO ENCONTRADAS")
        print("\n📋 PASOS PARA CONFIGURAR:")
        print("1. Ve a: https://console.cloud.google.com/")
        print("2. Crea un proyecto o selecciona uno existente")
        print("3. Habilita 'Cloud Vision API'")
        print("4. Crea credenciales de 'Cuenta de servicio'")
        print("5. Descarga el archivo JSON")
        print("6. Renómbralo a 'google-vision-key.json'")
        print(f"7. Colócalo en: {base_path}/credentials/")
        return False
    
    # Verificar contenido del archivo
    print(f"\n🔍 Verificando contenido del archivo...")
    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Faltan campos requeridos: {missing_fields}")
            return False
        
        print("✅ Archivo de credenciales válido")
        print(f"   Proyecto: {creds.get('project_id')}")
        print(f"   Email de servicio: {creds.get('client_email')}")
        
        # Probar importación de biblioteca
        print(f"\n🧪 Probando importación de Google Vision...")
        try:
            from google.cloud import vision
            print("✅ Biblioteca google-cloud-vision disponible")
            
            # Configurar credenciales y probar cliente
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
            client = vision.ImageAnnotatorClient()
            print("✅ Cliente Vision API inicializado correctamente")
            
        except ImportError:
            print("❌ Biblioteca google-cloud-vision no instalada")
            print("   Ejecuta: pip install google-cloud-vision")
            return False
        except Exception as e:
            print(f"❌ Error al inicializar cliente: {e}")
            return False
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Archivo de credenciales no es JSON válido")
        return False
    except Exception as e:
        print(f"❌ Error al leer credenciales: {e}")
        return False

def main():
    """Función principal"""
    success = test_google_vision_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 GOOGLE VISION API CONFIGURADO CORRECTAMENTE")
        print("✅ Listo para OCR avanzado")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("🛠️  Sigue los pasos anteriores para configurar")
    
    return success

if __name__ == "__main__":
    main()
