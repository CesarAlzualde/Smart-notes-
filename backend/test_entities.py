#!/usr/bin/env python3
"""
Script para probar la extracción de entidades directamente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.text_summarizer import TextSummarizer

def test_entities():
    print("=" * 50)
    print("PRUEBA DE EXTRACCIÓN DE ENTIDADES")
    print("=" * 50)
    
    # Crear instancia del TextSummarizer
    print("Inicializando TextSummarizer...")
    summarizer = TextSummarizer()
    print("✅ TextSummarizer inicializado correctamente")
    
    # Texto de prueba con entidades claras
    test_text = """
    María García trabaja en Microsoft España desde enero de 2023. 
    Vive en Madrid y colabora frecuentemente con el equipo de Barcelona.
    Su proyecto actual involucra inteligencia artificial y machine learning.
    Anteriormente trabajó en Google y Amazon en Estados Unidos.
    """
    
    print(f"\n📝 Texto de prueba:")
    print(test_text.strip())
    
    print(f"\n🔍 Iniciando extracción de entidades...")
    
    # Probar extracción de entidades
    try:
        entities = summarizer.extract_entities(test_text)
        
        print(f"\n✅ RESULTADO DE EXTRACCIÓN:")
        print(f"Número de tipos de entidad encontrados: {len(entities)}")
        
        if entities:
            for entity_type, entity_list in entities.items():
                print(f"  🏷️  {entity_type}: {entity_list}")
        else:
            print("❌ No se encontraron entidades")
            
    except Exception as e:
        print(f"❌ Error durante extracción: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_entities()
