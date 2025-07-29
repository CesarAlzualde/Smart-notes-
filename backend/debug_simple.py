#!/usr/bin/env python3
import os
import sys

# Configurar path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    from app.services.text_summarizer import TextSummarizer
    
    print("1. Creando TextSummarizer...")
    summarizer = TextSummarizer()
    
    print(f"2. MODELS['primary']: {summarizer.MODELS['primary']}")
    print(f"3. Tipo: {type(summarizer.MODELS['primary'])}")
    
    print("4. Verificando cada modelo individual:")
    for i, model in enumerate(summarizer.MODELS['primary']):
        print(f"   - Modelo {i}: '{model}' (tipo: {type(model)})")
    
    print(f"5. Estado del modelo: {summarizer.model_status.loaded}")
    print(f"6. Nombre del modelo cargado: {summarizer.model_status.model_name}")
    
    if summarizer.model_status.error_msg:
        print(f"7. Error: {summarizer.model_status.error_msg}")
    
    print("8. Fin del debug.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
