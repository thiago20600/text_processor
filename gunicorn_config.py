# Configuración de Gunicorn para producción
# Ejecutar con: gunicorn -c gunicorn_config.py main:app

import multiprocessing
import os

# Número de workers (procesos)
workers = 1

# Tipo de worker
worker_class = "uvicorn.workers.UvicornWorker"

# Host y puerto
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Timeout
timeout = 120

# Máximo de requests antes de reiniciar worker
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Procesos
daemon = False

# Reloading en desarrollo (comentar en producción)
# reload = True
