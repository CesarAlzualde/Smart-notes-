#!/usr/bin/env python3
"""
Script para reproducir el error específico de lista vs string en model loading
"""
import sys
import os
import logging

# Configurar logging muy detallado
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configurar path
sys.path.insert(0, '.')

def test_model_loading():
    try:
        print("=" * 60)
        print("INICIANDO PRUEBA DETALLADA")
        print("=" * 60)
        
        from app.services.text_summarizer import TextSummarizer
        
        print("1. Creando TextSummarizer...")
        summarizer = TextSummarizer()
        print(f"   ✓ Instancia creada")
        
        print(f"2. Verificando MODELS['primary']:")
        print(f"   - Lista: {summarizer.MODELS['primary']}")
        print(f"   - Tipo: {type(summarizer.MODELS['primary'])}")
        print(f"   - Cantidad: {len(summarizer.MODELS['primary'])}")
        
        print("3. Verificando cada modelo:")
        for i, model in enumerate(summarizer.MODELS['primary']):
            print(f"   - [{i}] '{model}' (tipo: {type(model)})")
        
        print(f"4. Estado inicial del modelo:")
        print(f"   - Cargado: {summarizer.model_status.loaded}")
        print(f"   - Nombre: '{summarizer.model_status.model_name}'")
        print(f"   - Error: '{summarizer.model_status.error_msg}'")
        
        print("5. Intentando generar resumen de prueba...")
        test_text = "Este es un texto de ejemplo para generar un resumen. Tiene múltiples oraciones para verificar el funcionamiento del sistema."
        
        # Aquí es donde típicamente ocurre el error
        result = summarizer.generate_summary(test_text, compression_ratio=0.3)
        print(f"   ✓ Resumen generado: {result}")
        
        print("6. Probando método _generate_summary_with_best_model directamente...")
        try:
            # Este método específicamente itera sobre MODELS['primary']
            best_result = summarizer._generate_summary_with_best_model(test_text, 0.3)
            print(f"   ✓ Best model resultado: {best_result}")
        except Exception as e:
            print(f"   ✗ ERROR en _generate_summary_with_best_model: {e}")
            import traceback
            traceback.print_exc()
        
        print("7. Test completado exitosamente!")
        
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading()
