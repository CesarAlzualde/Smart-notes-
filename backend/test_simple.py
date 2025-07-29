#!/usr/bin/env python3

print("🧪 Iniciando prueba básica...")

try:
    print("📦 Importando TextSummarizer...")
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    
    from app.services.text_summarizer import TextSummarizer
    print("✅ Importación exitosa")
    
    print("🔧 Creando instancia...")
    ts = TextSummarizer()
    print("✅ Instancia creada")
    
    # Probar solo el post-procesamiento
    print("🧹 Probando post-procesamiento...")
    test_summary = "resumir en español: La POO es un método de programación muy importante."
    cleaned = ts.post_process_summary(test_summary)
    print(f"Original: {test_summary}")
    print(f"Limpio: {cleaned}")
    
    print("✅ Prueba completada exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
