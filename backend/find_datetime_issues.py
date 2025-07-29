import os
import re

def find_datetime_timezone_usage(directory):
    """Busca todas las instancias de datetime.timezone en archivos Python"""
    datetime_issues = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                        # Busca patrones relacionados con datetime.timezone
                        matches = re.findall(r'datetime\.timezone|datetime\.now\(datetime\.timezone\.utc\)', content)
                        if matches:
                            print(f"Encontrado en {file_path}: {len(matches)} instancias")
                            datetime_issues.append((file_path, len(matches)))
                    except Exception as e:
                        print(f"Error leyendo {file_path}: {e}")
    
    return datetime_issues

if __name__ == "__main__":
    print("Buscando problemas de datetime.timezone en el código...")
    backend_dir = '.'  # Directorio actual (backend)
    issues = find_datetime_timezone_usage(backend_dir)
    
    print("\nResumen de archivos con problemas:")
    if issues:
        for file_path, count in issues:
            print(f"- {file_path}: {count} instancias")
        print(f"\nTotal: {len(issues)} archivos afectados")
    else:
        print("No se encontraron problemas de datetime.timezone")
