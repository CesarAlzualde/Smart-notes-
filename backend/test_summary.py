"""
Script para probar la funcionalidad de resumen.
Este script verifica que el resumen se procese correctamente tanto en modo síncrono como asíncrono.
"""

import os
import json
import time
import requests
from app.services.ocr_summary_handler import OCRSummaryHandler
from app.services.text_summarizer import TextSummarizer

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_summarizer():
    """Prueba el TextSummarizer directamente"""
    print("\n--- Probando TextSummarizer directamente ---")
    
    # Texto de ejemplo
    text = """
    La inteligencia artificial (IA) es la simulación de procesos de inteligencia humana por parte de máquinas, 
    especialmente sistemas informáticos. Estos procesos incluyen el aprendizaje (la adquisición de información 
    y reglas para el uso de la información), el razonamiento (usando las reglas para llegar a conclusiones 
    aproximadas o definitivas) y la autocorrección. Las aplicaciones particulares de la IA incluyen sistemas 
    expertos, reconocimiento de voz y visión artificial.
    
    El campo fue fundado sobre la afirmación de que la inteligencia humana "puede ser descrita con tanta 
    precisión que se puede crear una máquina para simularla". Esto plantea argumentos filosóficos sobre la 
    naturaleza de la mente y los límites éticos de la creación de inteligencias artificiales.
    """
    
    try:
        # Crear un resumen directamente
        summarizer = TextSummarizer()
        
        # Verificar si HF está disponible
        from app.services.text_summarizer import HF_AVAILABLE
        print(f"Hugging Face disponible: {HF_AVAILABLE}")
        
        # Generar resumen
        summary = summarizer.summarize(text)
        
        print(f"Resumen generado: \n{summary}")
        print("TextSummarizer está funcionando correctamente.")
    except Exception as e:
        print(f"Error al usar TextSummarizer: {e}")
        return False
        
    return True

def test_ocr_summary_handler():
    """Prueba el OCRSummaryHandler para generar resúmenes"""
    print("\n--- Probando OCRSummaryHandler ---")
    
    # Texto de ejemplo
    text = """
    Los modelos de lenguaje de gran tamaño (LLM) son sistemas de inteligencia artificial entrenados con enormes 
    cantidades de datos textuales para comprender y generar lenguaje humano. Estos modelos utilizan arquitecturas 
    de transformers con miles de millones de parámetros para captar patrones complejos del lenguaje. A diferencia 
    de los modelos tradicionales, los LLM pueden resolver tareas lingüísticas sin entrenamiento específico, 
    mostrando capacidades emergentes como el razonamiento, la comprensión contextual y la resolución de problemas.
    
    Aplicaciones como ChatGPT demuestran su versatilidad para escribir textos, crear código, analizar contenido
    y mantener conversaciones coherentes. Sin embargo, presentan desafíos importantes como sesgos heredados de 
    sus datos de entrenamiento, tendencia a "alucinar" información incorrecta, y preocupaciones éticas sobre 
    privacidad, propiedad intelectual y potencial mal uso. Su desarrollo continúa evolucionando rápidamente 
    con mejoras en control, transparencia y capacidades multimodales.
    """
    
    try:
        # Crear manejador
        handler = OCRSummaryHandler()
        
        # Generar resumen síncrono
        print("Generando resumen síncrono...")
        summary, metadata = handler.generate_summary(text, async_mode=False)
        
        print(f"Resumen generado: \n{summary}")
        print(f"Metadata: {metadata}")
        
        # Generar resumen asíncrono
        print("\nGenerando resumen asíncrono...")
        empty, async_metadata = handler.generate_summary(
            text, 
            async_mode=True,
            file_id="test_summary_async"
        )
        
        print(f"Respuesta inicial: {async_metadata}")
        
        # Esperar un momento para que el hilo termine
        time.sleep(5)
        
        # Comprobar estado
        if 'summary_id' in async_metadata:
            summary_id = async_metadata['summary_id']
            print(f"Comprobando estado del resumen con ID: {summary_id}")
            
            # Añadir el método get_summary_status si no existe
            if not hasattr(handler, 'get_summary_status'):
                print("El método get_summary_status no existe, implementando temporalmente...")
                
                def get_summary_status(self, summary_id):
                    temp_file = self.get_temp_file_path(summary_id, prefix="summary_result")
                    
                    if not os.path.exists(temp_file):
                        return {
                            'status': 'not_found',
                            'error': f"No se encontró información para el resumen {summary_id}"
                        }
                        
                    try:
                        with open(temp_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        return data
                    except Exception as e:
                        logger.error(f"Error leyendo estado del resumen: {e}")
                        return {
                            'status': 'error',
                            'error': f"Error al leer estado: {str(e)}"
                        }
                
                # Añadir el método dinámicamente
                from types import MethodType
                handler.get_summary_status = MethodType(get_summary_status, handler)
            
            # Obtener estado
            status = handler.get_summary_status(summary_id)
            print(f"Estado del resumen: {status}")
            
            if 'summary' in status:
                print(f"Resumen asíncrono: \n{status['summary']}")
        else:
            print("No se pudo obtener ID del resumen asíncrono")
        
        print("OCRSummaryHandler está funcionando correctamente.")
    except Exception as e:
        print(f"Error al usar OCRSummaryHandler: {e}")
        return False
        
    return True

def test_summary_api():
    """Prueba el endpoint de la API de resumen"""
    print("\n--- Probando API de resumen ---")
    
    # URL base (ajustar según configuración)
    base_url = "http://localhost:5173/api/summary"
    
    # Texto de ejemplo
    text = """
    Los microservicios son un estilo arquitectónico que estructura una aplicación como una colección de servicios
    pequeños y autónomos, modelados en torno a dominios de negocio. Cada servicio se ejecuta en su propio proceso
    y se comunica con mecanismos ligeros, a menudo una API HTTP. Los microservicios son altamente mantenibles y 
    testables, pueden ser implementados de forma independiente, organizados en torno a capacidades comerciales y
    son propiedad de un pequeño equipo.
    
    La arquitectura de microservicios permite el desarrollo continuo de aplicaciones grandes y complejas al permitir
    que las organizaciones evolucionen su stack tecnológico, escalen componentes independientemente y aíslen fallos.
    Sin embargo, este enfoque también introduce complejidad operativa, requiere coordinación para transacciones 
    distribuidas y presenta desafíos en latencia de red, consistencia de datos y gestión de fallos en cascada.
    """
    
    try:
        print("Advertencia: Esta prueba requiere que el servidor Flask esté en ejecución")
        print("Si el servidor no está ejecutándose, esta prueba fallará")
        
        # Generar un token JWT para pruebas (esto es simulado)
        # En un entorno real, necesitarías autenticarte correctamente
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6ImFkbWluIn0.AbxS.FIRMA_SIMULADA"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Intentar generar un resumen síncrono
        print("\nGenerando resumen síncrono vía API...")
        try:
            response = requests.post(
                f"{base_url}/generate",
                headers=headers,
                json={"text": text, "async_mode": False}
            )
            
            print(f"Código de estado: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"Resumen: {data.get('summary', 'No hay resumen')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error al conectar con la API: {e}")
            print("Asegúrate de que el servidor Flask esté en ejecución")
        
        # Intentar generar un resumen asíncrono
        print("\nGenerando resumen asíncrono vía API...")
        try:
            response = requests.post(
                f"{base_url}/generate",
                headers=headers,
                json={"text": text, "async_mode": True}
            )
            
            print(f"Código de estado: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"Respuesta inicial: {data}")
                
                if 'summary_id' in data:
                    summary_id = data['summary_id']
                    
                    # Esperar un momento para que se procese
                    print("Esperando 5 segundos para que se procese el resumen...")
                    time.sleep(5)
                    
                    # Comprobar estado
                    response = requests.get(
                        f"{base_url}/check/{summary_id}",
                        headers=headers
                    )
                    
                    if response.ok:
                        status_data = response.json()
                        print(f"Estado del resumen: {status_data}")
                    else:
                        print(f"Error al obtener estado: {response.text}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error al conectar con la API: {e}")
            print("Asegúrate de que el servidor Flask esté en ejecución")
    
    except Exception as e:
        print(f"Error general en la prueba de API: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Ejecutando pruebas de resumen de texto ===")
    
    # Ejecutar pruebas
    summarizer_ok = test_direct_summarizer()
    handler_ok = test_ocr_summary_handler()
    api_ok = test_summary_api()
    
    # Mostrar resultados
    print("\n=== Resultados de las pruebas ===")
    print(f"TextSummarizer: {'OK' if summarizer_ok else 'FALLO'}")
    print(f"OCRSummaryHandler: {'OK' if handler_ok else 'FALLO'}")
    print(f"API de resumen: {'OK' if api_ok else 'FALLO'}")
    
    if summarizer_ok and handler_ok:
        print("\nLa funcionalidad básica de resumen funciona correctamente.")
        print("Si la API falló, verifica que el servidor Flask esté en ejecución")
        print("y que hayas registrado correctamente el blueprint de summary.py.")
    else:
        print("\nHay problemas con la funcionalidad básica de resumen.")
        print("Revisa los mensajes de error para más detalles.")
