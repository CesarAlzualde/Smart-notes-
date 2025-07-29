import os 
os.environ['FLASK_ENV'] = 'production' 
os.environ['DATA_DIR'] = r'C:\ProgramData\Apuntes2.0' 
# Asegurar que el directorio de datos existe 
if not os.path.exists(os.environ['DATA_DIR']): 
    try: 
        os.makedirs(os.environ['DATA_DIR']) 
        os.makedirs(os.path.join(os.environ['DATA_DIR'], 'database')) 
        os.makedirs(os.path.join(os.environ['DATA_DIR'], 'uploads')) 
    except: 
        pass 
# Configurar DB para producción 
os.environ['DATABASE_URL'] = f"sqlite:///{os.environ['DATA_DIR']}/database/app.db" 
