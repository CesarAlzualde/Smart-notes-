#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos desde la raíz del proyecto.
"""

import sys
from backend.run import create_app
from scripts.init_db import init_db

if __name__ == "__main__":
    print("Creando la aplicación Flask...")
    app = create_app()
    
    print("Inicializando la base de datos...")
    init_db(app)
    
    print("Proceso completado.")
