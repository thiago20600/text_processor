# Archivo Docker para desplegar en contenedores
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código
COPY . .

# Crear usuario no-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]
