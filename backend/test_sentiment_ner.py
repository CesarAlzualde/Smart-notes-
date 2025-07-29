#!/usr/bin/env python3
"""
Test script para verificar la carga y funcionamiento de modelos de sentimiento y NER
después de las correcciones aplicadas para resolver errores de meta tensor.
"""

import sys
import os

# Agregar el directorio del backend al path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging para ver detalles
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sentiment_and_ner():
    """Prueba los modelos de sentimiento y NER con textos de ejemplo."""
    
    print("=" * 80)
    print("🧪 PRUEBA DE MODELOS DE SENTIMIENTO Y NER")
    print("=" * 80)
    
    try:
        # Inicializar el summarizer (no necesitamos resúmenes, solo NER y sentimiento)
        logger.info("🔄 Inicializando TextSummarizer...")
        summarizer = TextSummarizer()
        
        # Texto de prueba en español
        test_text = """
        María García es una excelente profesora que vive en Madrid. 
        Trabaja en la Universidad Complutense y le encanta enseñar matemáticas.
        Su experiencia es muy positiva y los estudiantes la adoran.
        También colabora con empresas como Google y Microsoft en proyectos de investigación.
        """
        
        print(f"\n📝 Texto de prueba:\n{test_text.strip()}")
        
        # 1. PRUEBA DE ANÁLISIS DE SENTIMIENTO
        print("\n" + "="*50)
        print("🎭 PRUEBA DE ANÁLISIS DE SENTIMIENTO")
        print("="*50)
        
        try:
            sentiment_result = summarizer.analyze_sentiment(test_text)
            print(f"✅ Resultado de sentimiento: {sentiment_result}")
            
            if sentiment_result.get('error'):
                print(f"⚠️  Error en sentimiento: {sentiment_result['error']}")
            else:
                label = sentiment_result.get('label', 'N/A')
                score = sentiment_result.get('score', 0.0)
                print(f"📊 Sentimiento detectado: {label} (confianza: {score:.2f})")
                
        except Exception as e:
            print(f"❌ Error en análisis de sentimiento: {e}")
        
        # 2. PRUEBA DE RECONOCIMIENTO DE ENTIDADES (NER)
        print("\n" + "="*50)
        print("🏷️  PRUEBA DE RECONOCIMIENTO DE ENTIDADES (NER)")
        print("="*50)
        
        try:
            entities_result = summarizer.extract_entities(test_text)
            print(f"✅ Resultado de entidades: {entities_result}")
            
            if entities_result:
                print("📋 Entidades encontradas:")
                for entity_type, entities in entities_result.items():
                    print(f"  • {entity_type}: {entities}")
            else:
                print("⚠️  No se encontraron entidades o hubo un error")
                
        except Exception as e:
            print(f"❌ Error en extracción de entidades: {e}")
        
        # 3. VERIFICACIÓN DE ESTADO DE MODELOS
        print("\n" + "="*50)
        print("📊 ESTADO DE MODELOS CARGADOS")
        print("="*50)
        
        print(f"📈 Modelo de resumen cargado: {summarizer.model_status.loaded}")
        print(f"📈 Nombre del modelo de resumen: {summarizer.model_status.model_name}")
        print(f"🎭 Modelo de sentimiento cargado: {summarizer._sentiment_model is not None}")
        print(f"🏷️  Modelo NER cargado: {summarizer._ner_pipeline is not None}")
        
        # 4. PRUEBA ADICIONAL CON TEXTO CORTO
        print("\n" + "="*50)
        print("🔬 PRUEBA CON TEXTO CORTO")
        print("="*50)
        
        short_text = "Juan está muy feliz hoy."
        print(f"📝 Texto corto: {short_text}")
        
        try:
            sentiment_short = summarizer.analyze_sentiment(short_text)
            print(f"🎭 Sentimiento texto corto: {sentiment_short}")
        except Exception as e:
            print(f"❌ Error con texto corto (sentimiento): {e}")
            
        try:
            entities_short = summarizer.extract_entities(short_text)
            print(f"🏷️  Entidades texto corto: {entities_short}")
        except Exception as e:
            print(f"❌ Error con texto corto (entidades): {e}")
        
    except Exception as e:
        print(f"❌ Error general en la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ PRUEBA COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    test_sentiment_and_ner()
