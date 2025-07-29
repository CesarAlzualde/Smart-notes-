"""
Script para arreglar la instalación de Google Vision API
Instala las versiones compatibles de las dependencias necesarias
"""

import subprocess
import sys
import os

def main():
    print("Instalando Google Vision API con versiones compatibles...")
    
    # Primero desinstalamos las versiones actuales que pueden estar causando conflictos
    dependencies_to_uninstall = [
        "google-cloud-vision",
        "google-api-core",
        "protobuf",
        "googleapis-common-protos"
    ]
    
    for dep in dependencies_to_uninstall:
        print(f"Desinstalando {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", dep])
    
    # Instalamos versiones específicas que son compatibles entre sí
    dependencies = [
        "protobuf==3.20.3",  # Versión estable y compatible
        "google-api-core==2.10.0",
        "googleapis-common-protos==1.56.4",
        "google-cloud-vision==3.1.0"
    ]
    
    # Instalamos las dependencias
    for dep in dependencies:
        print(f"Instalando {dep}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dep],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error instalando {dep}: {result.stderr}")
        else:
            print(f"✅ {dep} instalado correctamente")
    
    print("\n=== Verificando instalación ===")
    try:
        import google.cloud.vision
        print("✅ google.cloud.vision importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando google.cloud.vision: {e}")
    
    try:
        from google.protobuf.internal import builder
        print("✅ google.protobuf.internal.builder importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando google.protobuf.internal.builder: {e}")
    
    print("\nInstalación completada.")
    print("Por favor, reinicia el servidor Flask para que los cambios surtan efecto.")
    print("\nRecuerda que necesitas configurar las credenciales de Google Vision API en backend/.env")
    print("GOOGLE_APPLICATION_CREDENTIALS=ruta/al/archivo/credentials.json")

if __name__ == "__main__":
    main()
