#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en la corrección gramatical.
Prueba textos que anteriormente generaban prompts en inglés.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_summarizer import TextSummarizer

def test_grammar_correction():
    """Prueba la corrección gramatical con textos problemáticos."""
    
    print("🔧 Inicializando TextSummarizer...")
    summarizer = TextSummarizer()
    
    # Casos de prueba que anteriormente generaban problemas
    test_cases = [
        {
            "name": "Texto con errores básicos",
            "text": "La programacion orientada a objetos es un metodologia que organiza el codigo en clases y objetos"
        },
        {
            "name": "Texto técnico con términos específicos", 
            "text": "El algoritmo de ordenamiento burbuja compara elementos adjacentes y los intercambia si estan en orden incorrecto"
        },
        {
            "name": "Texto corto con error simple",
            "text": "Este es un texto con error gramatical"
        },
        {
            "name": "Texto con múltiples errores",
            "text": "Los desarrolladores deve conocer las mejores practicas para escribir codigo mantenible y eficiente"
        }
    ]
    
    print(f"\n🧪 Ejecutando {len(test_cases)} casos de prueba...\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"--- Caso {i}: {case['name']} ---")
        print(f"📝 Texto original: {case['text']}")
        
        try:
            result = summarizer.correct_grammar(case['text'])
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                corrected = result.get('corrected_text', case['text'])
                print(f"✅ Texto corregido: {corrected}")
                
                # Verificar que no contiene prompts en inglés
                english_indicators = [
                    'correct:', 'fix:', 'improve:', 'grammar:', 'corrected version',
                    'here is the corrected', 'this is the corrected', 'task:', 'instruction:'
                ]
                
                has_english = any(indicator in corrected.lower() for indicator in english_indicators)
                
                if has_english:
                    print("⚠️  ADVERTENCIA: Posible texto en inglés detectado")
                else:
                    print("✅ Limpieza exitosa - sin prompts en inglés")
                
        except Exception as e:
            print(f"❌ Error durante la corrección: {e}")
        
        print()
    
    print("🎯 Prueba de corrección gramatical completada!")

if __name__ == "__main__":
    test_grammar_correction()
