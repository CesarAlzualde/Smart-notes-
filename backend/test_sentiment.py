#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_sentiment():
    print("🧪 Iniciando prueba de análisis de sentimiento...")
    
    try:
        # Crear instancia del TextSummarizer
        ts = TextSummarizer()
        print("✅ TextSummarizer inicializado correctamente")
        
        # Texto de prueba
        test_text = "Este es un texto de prueba para verificar que el análisis de sentimiento funciona correctamente. Esto es muy positivo y me hace feliz."
        
        print(f"📝 Texto de prueba: {test_text[:100]}...")
        
        # Analizar solo sentimiento
        print("\n🔍 Probando análisis de sentimiento...")
        sentiment = ts.analyze_sentiment(test_text)
        print(f"✅ Sentimiento: {sentiment}")
        
        # Si el sentimiento funciona, probar análisis completo
        if sentiment and 'error' not in sentiment:
            print("\n📊 Probando análisis completo...")
            result = ts.analyze_text(test_text)
            print(f"✅ Resultado completo: {result}")
        else:
            print("❌ Error en análisis de sentimiento, no probando análisis completo")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sentiment()
