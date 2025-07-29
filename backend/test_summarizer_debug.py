#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("=== DEBUG TextSummarizer ===")

try:
    from app.services.text_summarizer import TextSummarizer
    print("✓ Import OK")
    
    print(f"Modelos: {TextSummarizer.MODELS['primary']}")
    print(f"Tipo: {type(TextSummarizer.MODELS['primary'])}")
    
    print("\n=== Creando instancia ===")
    ts = TextSummarizer()
    print("✓ Instancia creada")
    
    print(f"Estado: {ts.model_status.to_dict()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
