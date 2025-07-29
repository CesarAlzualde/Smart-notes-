"""
Script simple para probar la importación de app sin iniciar el servidor
"""

import os
import sys
import time

# Añadir directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Iniciando prueba de importación...")
print(f"Python path: {sys.path}")

try:
    print("Intentando importar backend.app...")
    import backend.app
    print("✓ Importación de backend.app exitosa")
except Exception as e:
    print(f"❌ Error al importar backend.app: {e}")
    import traceback
    traceback.print_exc()

print("Prueba completada.")
