"""
Script Simplificado para Iniciar la Aplicación (Backend + Frontend)
Sin dependencias de Redis/Celery para funcionamiento offline.
"""

import os
import sys
import subprocess
import threading
import time
import signal
import functools

# --- Configuración de Rutas y Comandos ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "auth-frontend")

# Determinar ejecutables según el SO
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")
    NPM_CMD = "npm.cmd"
else:
    VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "bin", "python")
    NPM_CMD = "npm"

# Comandos para cada servicio
BACKEND_CMD = [VENV_PYTHON, "run.py"]
FRONTEND_CMD = [NPM_CMD, "run", "dev"]

# --- Gestión de Procesos ---
processes = []

def run_command(cmd, cwd, name):
    """Ejecuta un comando, captura su salida y la muestra con un prefijo."""
    print(f"[{name}] Iniciando comando: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        processes.append(process)

        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.strip()}")

    except FileNotFoundError:
        print(f"[{name}] Error: El comando '{cmd[0]}' no se encontró.")
    except Exception as e:
        print(f"[{name}] Error al ejecutar el comando: {e}")

def start_service(cmd, cwd, name):
    """Inicia un servicio en un hilo separado."""
    thread = threading.Thread(target=run_command, args=(cmd, cwd, name))
    thread.daemon = True
    thread.start()
    return thread

def cleanup_processes():
    """Detiene todos los procesos iniciados."""
    print("\nDeteniendo todos los procesos...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    # Esperar a que terminen
    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

def signal_handler(sig, frame):
    """Manejador para Ctrl+C."""
    cleanup_processes()
    sys.exit(0)

def main():
    """Función principal que inicia backend y frontend."""
    # Configurar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=== Iniciando Aplicación Apuntes 2.0 (Modo Offline) ===")

    try:
        # Iniciar servicios en hilos
        start_service(BACKEND_CMD, BACKEND_DIR, "Backend")
        time.sleep(2)  # Dar tiempo al backend para iniciar
        start_service(FRONTEND_CMD, FRONTEND_DIR, "Frontend")

        print("\n===== SERVIDORES INICIADOS =====")
        print(f"  - Backend:   http://localhost:5000")
        print(f"  - Frontend:  http://localhost:5173")
        print("\nPresiona Ctrl+C para detener todos los servicios.\n")

        # Mantener el script principal vivo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass  # La señal ya fue manejada
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main()
