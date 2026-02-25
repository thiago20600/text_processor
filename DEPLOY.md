# Deploy - AI Text Processor

Guía breve para desplegar la app en producción.

## 1) Variables de entorno obligatorias

Define estas variables en tu plataforma:

- `GROQ_API_KEY`
- `SECRET_KEY`
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

Opcional:

- `TESSERACT_CMD` (solo si necesitas ruta manual de Tesseract)
- `PORT` (normalmente lo inyecta la plataforma)

## 2) Base de datos MySQL

Asegúrate de ejecutar `migrations.sql` en tu base antes de levantar la app.

## 3) Deploy en Render / Railway / Heroku

El proyecto ya incluye:

- `Procfile`
- `gunicorn_config.py` (usa `PORT` dinámico)
- `requirements.txt` con `gunicorn`

Comando de inicio sugerido:

- `gunicorn main:app -k uvicorn.workers.UvicornWorker --config gunicorn_config.py`

## 4) Deploy con Docker

El `Dockerfile` ya instala dependencias OCR de sistema:

- `tesseract-ocr`
- `poppler-utils`

Build y run local:

```bash
docker build -t ai-text-processor .
docker run --env-file .env -p 8000:8000 ai-text-processor
```

## 5) Checklist final

- Variables de entorno cargadas
- DB accesible desde el entorno de deploy
- Migraciones ejecutadas
- Endpoint health responde (`/health`)
- Registro/login funcionando
- Guardado de resumen funcionando

## 6) Post-deploy recomendado

- Rotar credenciales/API keys si alguna fue expuesta
- Activar logs y monitoreo básico
- Ejecutar tests antes de cada release (`pytest -q`)
