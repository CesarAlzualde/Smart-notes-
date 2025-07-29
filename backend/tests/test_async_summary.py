"""
Script para probar la funcionalidad de resúmenes asíncronos.
"""

import sys
import os
import json
import time
import uuid

# Añadir directorio padre al path para poder importar módulos de la aplicación
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ocr_summary_handler import OCRSummaryHandler
from app.services.summary_status_helper import get_summary_status, patch_ocr_handler

def test_async_summary():
    """
    Prueba la generación y consulta de resúmenes asíncronos.
    """
    # Asegurar que el método get_summary_status esté disponible
    patch_ocr_handler()
    
    # Inicializar el manejador OCR-Resumen
    handler = OCRSummaryHandler()
    
    # Texto de ejemplo para resumir
    texto_ejemplo = """
    La inteligencia artificial (IA) es un campo de la informática que se centra en desarrollar sistemas
    capaces de realizar tareas que requieren inteligencia humana. Estos sistemas pueden aprender,
    razonar, percibir, y procesar lenguaje natural.
    
    El aprendizaje automático (machine learning) es una rama de la IA que permite a las computadoras
    mejorar a través de la experiencia. En lugar de programar reglas específicas, los sistemas
    de aprendizaje automático identifican patrones en los datos.
    
    El aprendizaje profundo (deep learning) es un subconjunto del machine learning basado en redes
    neuronales artificiales con múltiples capas. Estas redes son particularmente efectivas en
    tareas como reconocimiento de imágenes, procesamiento del lenguaje natural y traducción automática.
    
    La IA tiene aplicaciones en numerosos campos como medicina, finanzas, transporte, educación
    y entretenimiento. A medida que la tecnología avanza, se espera que la IA continúe
    transformando industrias y la sociedad en general.
    """
    
    # Generar un ID único para este resumen
    summary_id = str(uuid.uuid4())
    print(f"ID de resumen generado: {summary_id}")
    
    # Crear un archivo inicial de estado "processing"
    temp_file = handler.get_temp_file_path(summary_id, prefix="summary_result")
    print(f"Archivo temporal que se creará: {temp_file}")
    
    # Guardar estado inicial como "processing"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({
            'status': 'processing',
            'timestamp': time.time(),
            'file_id': summary_id,
        }, f, ensure_ascii=False)
    print("\nCreado archivo de estado inicial 'processing'")
        
    # Iniciar la generación asíncrona del resumen
    print("\nIniciando generación asíncrona del resumen...")
    handler.generate_summary(texto_ejemplo, async_mode=True, file_id=summary_id)
    
    # Consultar el estado periódicamente
    for i in range(20):
        # Esperar un segundo entre consultas
        time.sleep(1)
        
        # Consultar estado
        status = get_summary_status(summary_id)
        print(f"\nEstado después de {i+1} segundos: {status.get('status')}")
        
        # Si está completo o con error, mostrar detalles y salir
        if status.get('status') in ['completed', 'error']:
            print("\nResumen finalizado con estado:", status.get('status'))
            if status.get('status') == 'completed':
                print("\nResumen generado:")
                print("=" * 80)
                print(status.get('summary', 'No hay resumen disponible'))
                print("=" * 80)
            elif status.get('status') == 'error':
                print("\nError:", status.get('error', 'Error desconocido'))
            break

    print("\nPrueba completada.")

if __name__ == "__main__":
    test_async_summary()
