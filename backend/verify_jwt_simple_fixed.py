"""
Verificación simple del sistema JWT con contexto de aplicación
"""
import os
import sys
import datetime

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar app
from app import create_app
from flask_jwt_extended import create_access_token, decode_token

print("=== Verificación Simple del JWT ===")

# Verificar variable de entorno JWT_SECRET_KEY
jwt_secret = os.environ.get('JWT_SECRET_KEY')
print(f"1. JWT_SECRET_KEY en variables de entorno: {'✅ Presente' if jwt_secret else '❌ No encontrado'}")

# Crear la aplicación con contexto
app = create_app()

with app.app_context():
    try:
        # Crear un token de prueba
        test_payload = {'user_id': 123, 'username': 'test_user', 'role': 'user'}
        
        token = create_access_token(
            identity=test_payload,
            expires_delta=datetime.timedelta(hours=1)
        )
        print(f"2. Generación de token: ✅ Exitosa")
        print(f"   Token: {token[:30]}...")
        
        # Intentar decodificar el token
        decoded = decode_token(token)
        print(f"3. Decodificación de token: ✅ Exitosa")
        print(f"   Payload: {decoded['sub']}")
        print(f"   Expiración: {datetime.datetime.fromtimestamp(decoded['exp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n✅ RESULTADO: La configuración JWT funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n❌ RESULTADO: Hay problemas con la configuración JWT")
        print("   Asegúrate de que JWT_SECRET_KEY esté configurado correctamente")
