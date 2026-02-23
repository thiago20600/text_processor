# Configuración para deploy en Heroku
# Usar con: heroku create tu-app-nombre
# Luego: git push heroku main

# Procfile especifica cómo ejecutar la app
web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}

# requirements.txt ya está configurado
# Solo agrega las variables de entorno:
# heroku config:set GROQ_API_KEY=tu-clave
