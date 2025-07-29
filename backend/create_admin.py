import sys
from app import create_app
from app.models import db, User

def main():
    """Crea un usuario administrador forzosamente."""
    app = create_app()
    
    with app.app_context():
        print("Creando usuario administrador...")
        
        # Buscar usuario existente
        user = User.query.filter_by(email='admin@example.com').first()
        
        if user:
            print("Usuario admin@example.com ya existe, actualizando contraseña...")
            user.set_password('admin123')
        else:
            print("Creando nuevo usuario admin...")
            user = User(
                username="admin",
                name="Administrador",
                email="admin@example.com",
                role="admin"
            )
            user.set_password('admin123')
            db.session.add(user)
        
        try:
            db.session.commit()
            print("✅ Usuario administrador guardado correctamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al guardar usuario: {str(e)}")
        
        # Verificar que se creó correctamente
        user_check = User.query.filter_by(email='admin@example.com').first()
        print(f"Verificación final - Usuario existe: {user_check is not None}")
        if user_check:
            print(f"Nombre: {user_check.name}")
            print(f"Email: {user_check.email}")
            print(f"Rol: {user_check.role}")

if __name__ == "__main__":
    main()
    print("Script completado.")
