"""
Script Unificado para Iniciar el Entorno de Desarrollo Completo.

Orquesta el inicio de todos los servicios necesarios:
1. Redis (vía Docker Compose)
2. Backend (Flask, usando run.py)
3. Frontend (Vite)
4. Celery Worker (para tareas asíncronas)

Uso: python run_dev_servers.py
"""

import os
import sys
import subprocess
import threading
import time
import signal
import argparse
import functools

# --- Configuración de Rutas y Comandos ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "auth-frontend")

# Determinar ejecutables según el SO
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")
    NPM_CMD = "npm.cmd"
    DOCKER_COMPOSE_CMD = "docker-compose.exe"
else:
    VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "bin", "python")
    NPM_CMD = "npm"
    DOCKER_COMPOSE_CMD = "docker-compose"

# Comandos para cada servicio
DOCKER_CMD_UP = [DOCKER_COMPOSE_CMD, "up", "-d", "redis"]
DOCKER_CMD_DOWN = [DOCKER_COMPOSE_CMD, "down"]
BACKEND_CMD = [VENV_PYTHON, "run.py"]
FRONTEND_CMD = [NPM_CMD, "run", "dev"]
CELERY_CMD = [VENV_PYTHON, "start_ocr_worker.py"]

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
        print(f"[{name}] Error: El comando '{cmd[0]}' no se encontró. Asegúrate de que esté en tu PATH.")
    except Exception as e:
        print(f"[{name}] Error al ejecutar el comando: {e}")

def start_service(cmd, cwd, name):
    """Inicia un servicio en un hilo separado."""
    thread = threading.Thread(target=run_command, args=(cmd, cwd, name))
    thread.daemon = True
    thread.start()
    return thread

def cleanup_processes(use_docker=True):
    """Detiene todos los procesos iniciados y, opcionalmente, los servicios de Docker."""
    print("\nDeteniendo todos los procesos y servicios...")
    # Detener procesos de subproceso (backend, frontend, celery)
    for p in reversed(processes):
        try:
            p.terminate()
        except Exception:
            pass
    # Esperar a que terminen
    for p in reversed(processes):
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

    # Detener servicios de Docker si se usaron
    if use_docker:
        print("[Docker] Deteniendo servicios de Docker Compose...")
        subprocess.run(DOCKER_CMD_DOWN, cwd=ROOT_DIR, capture_output=True)
        print("[Docker] Servicios detenidos.")

def signal_handler(sig, frame, use_docker=True):
    """Manejador para Ctrl+C que sabe si se usó Docker o no."""
    cleanup_processes(use_docker=use_docker)
    sys.exit(0)

def main():
    """Función principal que orquesta el inicio de todos los servicios."""
    parser = argparse.ArgumentParser(description="Inicia el entorno de desarrollo.")
    parser.add_argument("--no-docker", action="store_true", help="No iniciar Redis con Docker Compose.")
    args = parser.parse_args()

    use_docker = not args.no_docker

    # Configurar el manejador de señales para que sepa si se usó Docker
    handler = functools.partial(signal_handler, use_docker=use_docker)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    print("=== Iniciando Entorno de Desarrollo Completo ===")
    if not use_docker:
        print("\n*** MODO SIN DOCKER ACTIVADO ***")
        print("Asegúrate de que Redis esté corriendo localmente en el puerto 6379.\n")

    try:
        # 1. Iniciar Redis con Docker Compose (si está habilitado)
        if use_docker:
            print("[Docker] Iniciando Redis con Docker Compose...")
            subprocess.run(DOCKER_CMD_UP, cwd=ROOT_DIR, check=True)
            print("[Docker] Redis iniciado.")
            time.sleep(3)  # Dar tiempo a que Redis se estabilice

        # 2. Iniciar servicios en hilos
        start_service(BACKEND_CMD, BACKEND_DIR, "Backend")
        time.sleep(5)  # Dar tiempo al backend para que inicie antes que el worker
        start_service(CELERY_CMD, BACKEND_DIR, "Celery")
        start_service(FRONTEND_CMD, FRONTEND_DIR, "Frontend")

        print("\n===== SERVIDORES INICIADOS =====")
        print(f"  - Backend:   http://localhost:5000")
        print(f"  - Frontend:  http://localhost:5173")
        print(f"  - Celery:    Worker procesando tareas")
        if use_docker:
            print("  - Redis:     Corriendo en Docker")
        else:
            print("  - Redis:     (Se espera que esté corriendo localmente)")
        print("\nPresiona Ctrl+C para detener todos los servicios.\n")

        # Mantener el script principal vivo
        while True:
            time.sleep(1)

    except subprocess.CalledProcessError as e:
        if use_docker:
            print(f"[Docker] Error al iniciar Docker Compose. ¿Está Docker en ejecución? Error: {e}")
    except KeyboardInterrupt:
        pass  # La señal ya fue manejada
    finally:
        cleanup_processes(use_docker=use_docker)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
