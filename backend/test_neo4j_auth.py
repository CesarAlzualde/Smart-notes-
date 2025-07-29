"""
Probar diferentes combinaciones de credenciales Neo4j
"""

import os
from neo4j import GraphDatabase

def test_credentials():
    """Probar diferentes combinaciones de credenciales"""
    uri = "bolt://localhost:7687"
    
    # Combinaciones comunes de credenciales
    credentials_to_test = [
        ("neo4j", "neo4j"),      # Por defecto
        ("neo4j", ""),           # Sin contraseña  
        ("neo4j", "cesar"),      # La que tenemos en .env
        ("neo4j", "password"),   # Común
        ("neo4j", "admin"),      # Común
    ]
    
    print("🔐 PROBANDO CREDENCIALES NEO4J")
    print("=" * 40)
    
    for user, password in credentials_to_test:
        try:
            print(f"\n🧪 Probando: usuario='{user}', contraseña='{password if password else '(vacía)'}'")
            
            driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                connection_timeout=5.0
            )
            
            with driver.session() as session:
                result = session.run("RETURN 'Éxito' AS status, datetime() AS timestamp")
                record = result.single()
                
                if record:
                    print(f"✅ ¡CREDENCIALES CORRECTAS!")
                    print(f"   Usuario: {user}")
                    print(f"   Contraseña: {password if password else '(vacía)'}")
                    print(f"   Respuesta: {record['status']}")
                    print(f"   Timestamp: {record['timestamp']}")
                    
                    # Obtener información del usuario actual
                    try:
                        result = session.run("CALL dbms.security.showCurrentUser()")
                        user_info = result.single()
                        if user_info:
                            print(f"   Info usuario: {dict(user_info)}")
                    except:
                        pass  # Algunas versiones no tienen este comando
                    
                    driver.close()
                    return user, password
                    
            driver.close()
            
        except Exception as e:
            error_msg = str(e)
            if "Unauthorized" in error_msg:
                print(f"❌ Credenciales incorrectas")
            elif "authentication failure" in error_msg:
                print(f"❌ Fallo de autenticación")
            else:
                print(f"❌ Error: {error_msg}")
    
    print(f"\n💥 Ninguna combinación funcionó")
    return None, None


def test_with_correct_credentials(user, password):
    """Probar operaciones básicas con las credenciales correctas"""
    try:
        print(f"\n🎯 PROBANDO OPERACIONES CON CREDENCIALES CORRECTAS")
        print("=" * 50)
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=(user, password),
            connection_timeout=10.0
        )
        
        with driver.session() as session:
            # Información de la base de datos
            try:
                result = session.run("CALL db.info()")
                db_info = result.single()
                if db_info:
                    print(f"✓ Base de datos: {dict(db_info)}")
            except:
                print("ℹ️ No se pudo obtener info de la BD (normal en algunas versiones)")
            
            # Prueba básica de escritura/lectura
            session.run("MERGE (test:AuthTest {id: 'test-auth', timestamp: datetime()})")
            
            result = session.run("MATCH (test:AuthTest {id: 'test-auth'}) RETURN test.timestamp AS ts")
            record = result.single()
            
            if record:
                print(f"✓ Operación exitosa - Timestamp: {record['ts']}")
                
                # Limpiar
                session.run("MATCH (test:AuthTest {id: 'test-auth'}) DELETE test")
                print("✓ Limpieza exitosa")
                
                driver.close()
                return True
            else:
                print("❌ No se pudo leer el dato creado")
                return False
                
    except Exception as e:
        print(f"❌ Error en operaciones: {str(e)}")
        return False


def update_env_file(user, password):
    """Actualizar archivo .env con las credenciales correctas"""
    try:
        print(f"\n📝 ACTUALIZANDO ARCHIVO .ENV")
        print("=" * 30)
        
        env_path = ".env"
        
        # Leer archivo actual
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Actualizar líneas de Neo4j
        updated_lines = []
        for line in lines:
            if line.startswith("NEO4J_USER="):
                updated_lines.append(f"NEO4J_USER={user}\n")
                print(f"✓ Actualizado NEO4J_USER={user}")
            elif line.startswith("NEO4J_PASSWORD="):
                updated_lines.append(f"NEO4J_PASSWORD={password}\n")
                print(f"✓ Actualizado NEO4J_PASSWORD={password}")
            else:
                updated_lines.append(line)
        
        # Escribir archivo actualizado
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print("✓ Archivo .env actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {str(e)}")
        return False


def main():
    print("🔍 DIAGNÓSTICO CREDENCIALES NEO4J")
    print("=" * 50)
    
    # Paso 1: Encontrar credenciales correctas
    correct_user, correct_password = test_credentials()
    
    if correct_user:
        # Paso 2: Probar operaciones
        operations_ok = test_with_correct_credentials(correct_user, correct_password)
        
        if operations_ok:
            # Paso 3: Actualizar .env
            env_updated = update_env_file(correct_user, correct_password)
            
            print(f"\n🎉 ¡PROBLEMA RESUELTO!")
            print(f"✓ Credenciales correctas: {correct_user} / {correct_password}")
            print(f"✓ Operaciones funcionando")
            if env_updated:
                print(f"✓ Archivo .env actualizado")
            print(f"\n💡 Ahora puedes ejecutar: python test_neo4j_only.py")
            
        else:
            print(f"\n⚠️ Credenciales funcionan pero hay problemas de operación")
    else:
        print(f"\n❌ NO SE ENCONTRARON CREDENCIALES VÁLIDAS")
        print(f"💡 Posibles soluciones:")
        print(f"   1. Reiniciar Neo4j Browser y cambiar contraseña")
        print(f"   2. Resetear Neo4j completamente")
        print(f"   3. Verificar instalación de Neo4j")


if __name__ == "__main__":
    main()
