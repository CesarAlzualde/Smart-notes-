"""
Script de diagnóstico para probar la conexión a PostgreSQL directamente
"""

import os
import sys
import time
import psycopg2
from dotenv import load_dotenv

# Añadir la raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=== Test de conexión a PostgreSQL ===")

# Cargar variables de entorno
print("Cargando variables de entorno...")
load_dotenv()

# Obtener la URL de la base de datos
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ ERROR: No se encontró DATABASE_URL en las variables de entorno")
    sys.exit(1)

# Mostrar la URL (sin contraseña para seguridad)
db_parts = db_url.split(":")
if len(db_parts) >= 3:
    # postgresql://usuario:contraseña@host:puerto/nombre_db
    censored_url = f"{db_parts[0]}://{db_parts[1].split('@')[0]}:***@{db_parts[2]}"
    print(f"URL de base de datos: {censored_url}")
else:
    print(f"URL de base de datos: {db_url}")

print("\nIntentando conectar a PostgreSQL...")
start_time = time.time()

try:
    # Intentar establecer la conexión
    conn = psycopg2.connect(db_url)
    end_time = time.time()
    
    # Si llegamos aquí, la conexión fue exitosa
    print(f"✅ ÉXITO: Conexión establecida en {end_time - start_time:.2f} segundos")
    
    # Probar una consulta simple
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"Versión de PostgreSQL: {version}")
    
    # Cerrar la conexión
    conn.close()
    print("Conexión cerrada correctamente")
    
except psycopg2.OperationalError as e:
    end_time = time.time()
    print(f"❌ ERROR DE CONEXIÓN después de {end_time - start_time:.2f} segundos: {e}")
    print("\nPosibles soluciones:")
    print("1. Verifica que el servidor PostgreSQL esté en ejecución")
    print("2. Verifica que las credenciales sean correctas")
    print("3. Comprueba que el host y puerto sean accesibles (no bloqueados por firewall)")
    print("4. Verifica que la base de datos 'apuntes' exista")

except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")

print("\n=== Fin del diagnóstico ===")
