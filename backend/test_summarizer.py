#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el TextSummarizer funciona correctamente
con los modelos de IA después de las correcciones.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_summarizer import TextSummarizer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_summarization():
    """Prueba la funcionalidad de resumen de texto."""
    print("🚀 Iniciando prueba del TextSummarizer...")
    
    # Texto de prueba en español
    test_text = """
    La inteligencia artificial es una tecnología revolucionaria que está transformando múltiples sectores de la sociedad.
    En el ámbito de la medicina, los sistemas de IA pueden ayudar en el diagnóstico temprano de enfermedades, 
    analizando imágenes médicas con una precisión superior a la humana en algunos casos. En el sector financiero,
    los algoritmos de machine learning detectan fraudes y optimizan inversiones. La educación también se beneficia
    de estas tecnologías mediante sistemas de aprendizaje personalizado que se adaptan al ritmo de cada estudiante.
    Sin embargo, es importante considerar las implicaciones éticas y sociales de estas tecnologías, incluyendo
    temas de privacidad, sesgo algorítmico y el impacto en el empleo. El desarrollo responsable de la IA requiere
    una colaboración estrecha entre desarrolladores, reguladores y la sociedad en general.
    """
    
    try:
        # Crear instancia del summarizer
        summarizer = TextSummarizer()
        
        print(f"\n📊 Estado del modelo:")
        print(f"  - Modelo cargado: {summarizer.model_status.loaded}")
        print(f"  - Nombre del modelo: {summarizer.model_name}")
        print(f"  - Dispositivo: {summarizer.device}")
        print(f"  - Modelos disponibles en config: {summarizer.models_config.get('summarization_models', [])}")
        
        # Generar resumen
        print(f"\n📝 Generando resumen...")
        print(f"Texto original ({len(test_text)} caracteres):")
        print(test_text.strip())
        
        result = summarizer.generate_summary(test_text, compression_ratio=0.3)
        
        print(f"\n✅ Resultado del resumen:")
        print(f"  - Resumen: {result.get('summary', 'No disponible')}")
        print(f"  - Modelo usado: {result.get('model_name', 'Desconocido')}")
        print(f"  - Error: {result.get('error', 'Ninguno')}")
        
        # Verificar si contiene tokens problemáticos
        summary_text = result.get('summary', '')
        if '<extra_id_' in summary_text:
            print(f"\n❌ PROBLEMA: El resumen contiene tokens <extra_id_X>!")
        elif 'TMY CUCD USB LED O' in summary_text or len(summary_text.strip()) < 10:
            print(f"\n❌ PROBLEMA: El resumen es de muy baja calidad!")
        else:
            print(f"\n✅ El resumen parece estar bien generado.")
            
        return result
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        logger.exception("Error detallado:")
        return None

def test_model_loading():
    """Prueba específicamente la carga de modelos."""
    print("\n🔧 Probando carga de modelos...")
    
    try:
        summarizer = TextSummarizer()
        
        print(f"\n📋 Información de configuración:")
        print(f"  - AI Config cargado: {bool(summarizer.ai_config)}")
        print(f"  - Models config: {summarizer.models_config}")
        print(f"  - Summarization params: {summarizer.summarization_params}")
        print(f"  - Force Spanish: {getattr(summarizer, 'force_spanish_output', False)}")
        
        return summarizer
        
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        logger.exception("Error detallado:")
        return None

if __name__ == "__main__":
    print("🧪 PRUEBA DEL SISTEMA DE RESUMEN DE IA")
    print("="*50)
    
    # Prueba 1: Carga de modelos
    summarizer = test_model_loading()
    
    if summarizer:
        # Prueba 2: Generación de resumen
        result = test_summarization()
        
        print("\n" + "="*50)
        if result and result.get('summary') and not result.get('error'):
            print("✅ TODAS LAS PRUEBAS PASARON - El sistema está funcionando correctamente")
        else:
            print("❌ ALGUNAS PRUEBAS FALLARON - Revisar logs para más detalles")
    else:
        print("❌ NO SE PUDO INICIALIZAR EL SISTEMA")
