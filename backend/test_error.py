#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    from app.services.text_summarizer import TextSummarizer
    print("Creando TextSummarizer...")
    ts = TextSummarizer()
    print("TextSummarizer creado.")
    
    # Probar generar un resumen
    print("Probando generar resumen...")
    result = ts.generate_summary("Este es un texto de prueba para resumir.")
    print(f"Resultado: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
