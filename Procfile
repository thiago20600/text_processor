# Configuración para deploy en Heroku, Railway, Render
# Compatible con Linux/Docker

web: gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --config gunicorn_config.py
