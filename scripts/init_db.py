#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos con los usuarios y roles necesarios.
"""

import os
import sys
from flask import Flask

def init_db(app: Flask) -> None:
    """
    Inicializa la base de datos con datos básicos necesarios.
    Crea un usuario administrador si no existe.
    """
    # Agregar la ruta raíz del proyecto al sys.path para poder importar los módulos
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    with app.app_context():
        from backend.app.models import db, User
        
        print("Inicializando base de datos...")
        
        # Verificar si existe usuario administrador
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("Creando usuario administrador...")
            admin = User(
                username='admin',
                email='admin@example.com',
                name='Administrador',
                role='admin',  # Asignando rol de administrador
                is_active=True
            )
            # Usar contraseña segura en producción
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin12345')
            admin.set_password(admin_password)
            
            # Configurar una pregunta de seguridad para el administrador
            admin.security_question = "¿Cuál es el nombre de este sistema?"
            admin.set_security_answer("apuntes")
            
            db.session.add(admin)
            db.session.commit()
            print(f"Usuario administrador creado con éxito. Usuario: admin, Contraseña: {admin_password}")
            print("IMPORTANTE: Cambie esta contraseña inmediatamente en un entorno de producción.")
        else:
            # Asegurarse de que el usuario admin tenga el rol correcto
            if admin.role != 'admin':
                print("Actualizando rol del usuario administrador...")
                admin.role = 'admin'
                db.session.commit()
                print("Rol actualizado correctamente.")
            else:
                print("Usuario administrador ya existe con rol correcto.")
        
        # Aquí podrían añadirse otros usuarios de prueba si es necesario
        
        print("Inicialización de la base de datos completada.")


if __name__ == "__main__":
    # Si se ejecuta directamente, intentamos importar la app
    try:
        from app import app
        init_db(app)
    except ImportError:
        print("Error: No se pudo importar la aplicación Flask.")
        print("Por favor, ejecute este script desde el contexto de la aplicación:")
        print("  from app import app")
        print("  from init_db import init_db")
        print("  init_db(app)")
        sys.exit(1)
