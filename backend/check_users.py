import sys
from app import create_app
from app.models import db, User

def main():
    """Verifica si existen usuarios en la base de datos y crea uno de prueba si es necesario."""
    app = create_app()
    
    with app.app_context():
        print("======= VERIFICACIÓN DE USUARIOS =======")
        sys.stdout.flush()
        
        # Listar usuarios existentes
        users = User.query.all()
        print(f"Usuarios encontrados: {len(users)}")
        sys.stdout.flush()
        
        for user in users:
            print(f"- {user.username} ({user.email})")
            sys.stdout.flush()
            
        # Si no hay usuarios, crear uno de prueba
        if not users:
            print("\nCreando usuario de prueba...")
            sys.stdout.flush()
            
            test_user = User(
                username="admin",
                name="Administrador",
                email="admin@example.com",
                role="admin"
            )
            test_user.set_password("admin123")
            db.session.add(test_user)
            
            try:
                db.session.commit()
                print(f"✓ Usuario creado: admin@example.com (contraseña: admin123)")
                sys.stdout.flush()
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error al crear usuario: {str(e)}")
                sys.stdout.flush()
        else:
            print("\nYa existen usuarios en la base de datos.")
            sys.stdout.flush()
        
        print("=======================================")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
