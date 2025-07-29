"""
Comandos CLI personalizados para Flask.
"""

import click
from flask.cli import with_appcontext
from .extensions import db
from .models.user import User

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa la base de datos."""
    click.echo('Inicializando la base de datos...')
    db.create_all()
    click.echo('Base de datos inicializada correctamente!')

@click.command('create-admin')
@with_appcontext
@click.option('--email', default='admin@example.com', help='Email del administrador')
@click.option('--password', default='admin123', help='Contraseña del administrador')
def create_admin_command(email, password):
    """Crea un usuario administrador."""
    try:
        # Verificar si el usuario ya existe
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.set_password(password)
            user.role = 'admin'
            click.echo(f'Usuario administrador actualizado: {email}')
        else:
            # Crear nuevo usuario
            user = User(
                username=email.split('@')[0],
                name="Administrador",
                email=email,
                role='admin',
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            
            click.echo(f'Usuario administrador creado: {email}')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error al crear usuario administrador: {str(e)}')

def register_commands(app):
    """Registra comandos CLI personalizados."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
