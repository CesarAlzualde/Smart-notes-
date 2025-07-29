#!/usr/bin/env python3
"""
Test simple de limpieza
"""
import re

def clean_summary_text(summary: str) -> str:
    """Limpia el texto del resumen eliminando artefactos y secuencias extrañas."""
    if not summary:
        return summary
        
    print(f"🧹 Limpiando: '{summary}'")
    
    # PASO 1: Eliminar acrónimos al final
    summary = re.sub(r'\s+[A-Z]{2,}(\s+[A-Z]{2,})*\s*$', '', summary)
    summary = re.sub(r'\s+\b[A-Z]{1,4}\b(\s+\b[A-Z]{1,4}\b){2,}\s*$', '', summary)
    
    # PASO 2: Eliminar fechas extrañas
    summary = re.sub(r'\s+\d{1,2}:\d{1,2}/\d{4}\s*', '', summary)
    
    # PASO 3: Eliminar texto técnico al final
    summary = re.sub(r'\s+(ET|ING|USB|LED|CD|DVD)\s*$', '', summary, flags=re.IGNORECASE)
    
    # PASO 4: Limpiar espacios múltiples
    summary = re.sub(r'\s+', ' ', summary).strip()
        
    print(f"✅ Limpiado: '{summary}'")
    return summary

def test_cases():
    """Prueba casos específicos"""
    print("=" * 60)
    print("🧹 PRUEBA DE LIMPIEZA DE RESUMEN")
    print("=" * 60)
    
    cases = [
        {
            "name": "Caso 1",
            "text": "La POO es un método de implementación TMY CUCD USB LED O"
        },
        {
            "name": "Caso 2", 
            "text": "Resumen sobre programación 17:02/1955 con datos"
        },
        {
            "name": "Caso 3",
            "text": "Texto normal sin artefactos para verificar"
        }
    ]
    
    success = True
    
    for case in cases:
        print(f"\n--- {case['name']} ---")
        original = case['text']
        cleaned = clean_summary_text(original)
        
        # Verificar que no tenga artefactos
        has_artifacts = any(artifact in cleaned for artifact in ["TMY", "CUCD", "17:02/1955"])
        
        if has_artifacts:
            print("❌ FALLO: Todavía tiene artefactos")
            success = False
        else:
            print("✅ ÉXITO: Sin artefactos")
    
    print("\n" + "="*50)
    if success:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
    
    return success

if __name__ == "__main__":
    test_cases()
