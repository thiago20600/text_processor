## 📝 Tips y Trucos para mejorar tu aplicación

### 1. Seguridad mejorada

**Proteger tu API key:**

En lugar de guardar la clave en el código, usa variables de entorno:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Carga desde archivo .env

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY no está configurada!")
```

Instala python-dotenv:
```bash
pip install python-dotenv
```

### 2. Agregar rate limiting

Protege tu aplicación de abusos:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/process")
@limiter.limit("10/minute")  # 10 solicitudes por minuto
async def process_text(request: Request):
    # ... código
```

### 3. Agregar logging

Para debugging en producción:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/process")
async def process_text(request: Request):
    logger.info(f"Procesando texto de {len(text)} caracteres")
    # ...
    logger.error(f"Error: {str(e)}")
```

### 4. Caché de respuestas

Guarda respuestas para textos iguales:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def process_text_with_ai(text: str) -> dict:
    # ... el código existente
```

### 5. Soporte para múltiples idiomas

Agrega selección de idioma:

```python
async def process_text_with_ai(text: str, language: str = "es") -> dict:
    prompts = {
        "es": "Analiza el siguiente texto...",
        "en": "Analyze the following text...",
    }
    
    prompt = prompts.get(language, prompts["es"])
    # ...
```

### 6. Modo oscuro automático

En `static/style.css`, agrega:

```css
@media (prefers-color-scheme: dark) {
    body {
        background: #0f172a;
        color: #f1f5f9;
    }
    
    .header, .form-section, .result-card {
        background: #1e293b;
    }
}
```

### 7. Exportar a PDF

Agrega esta dependencia:
```bash
pip install reportlab
```

Luego en `main.py`:

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

@app.post("/api/export-pdf")
async def export_pdf(request: Request):
    data = await request.json()
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Escribir contenido
    pdf.drawString(50, 750, "RESUMEN")
    pdf.drawString(50, 730, data.get("summary", ""))
    
    pdf.save()
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf")
```

### 8. WebSocket para actualizaciones en tiempo real

Para actualización en vivo sin recargar la página:

```python
from fastapi import WebSocket

@app.websocket("/ws/process")
async def websocket_process(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        # Procesar en tiempo real
        await websocket.send_json({"status": "procesando"})
```

### 9. Historial de procesos

Guarda en una base de datos:

```bash
pip install sqlalchemy
```

```python
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///./history.db")

class Process(Base):
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True)
    text = Column(String)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
```

### 10. Tests unitarios

Crea `test_main.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_process_text_valid():
    response = client.post("/api/process", json={
        "text": "Este es un texto de prueba con más de 10 caracteres"
    })
    assert response.status_code == 200

def test_process_text_too_short():
    response = client.post("/api/process", json={
        "text": "Corto"
    })
    assert response.status_code == 422 or not response.json()["success"]
```

Ejecutar tests:
```bash
pip install pytest
pytest test_main.py -v
```

### 11. Metricas y monitoreo

Integrar con Sentry para monitoreo en producción:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://tu-dsn-aqui@sentry.io/xxxxx",
    traces_sample_rate=1.0
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    sentry_sdk.capture_exception(exc)
    return {"error": "Error procesando la solicitud"}
```

### 12. Validación mejorada

Usar Pydantic para validación:

```python
from pydantic import BaseModel, Field, validator

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000)
    language: str = "es"
    
    @validator("language")
    def language_must_be_valid(cls, v):
        if v not in ["es", "en", "fr"]:
            raise ValueError("Idioma no soportado")
        return v

@app.post("/api/process")
async def process_text(request: ProcessRequest):
    # request.text, request.language ya están validados
    pass
```

---

## 🎨 Ideas para customización

- Agregar tema personalizado por usuario
- Soporte para múltiples formatos (Markdown, RTF, PDF)
- Análisis de sentimientos del texto
- Extracción automática de entidades (nombres, lugares)
- Traducción automática de resultados
- Integración con Discord/Slack para notificaciones
- API REST pública para integraciones
- Dashboard de estadísticas de uso

---

## 📚 Recursos útiles

- [FastAPI Advanced User Guide](https://fastapi.tiangolo.com/advanced/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Pydantic Validation](https://docs.pydantic.dev)
- [Testing in FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Groq API Documentation](https://console.groq.com/docs)
