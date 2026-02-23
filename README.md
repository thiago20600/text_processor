# AI Text Processor 📚

Una aplicación web simple y potente que procesa textos usando inteligencia artificial para generar:
- **Resúmenes** concisos del contenido
- **Puntos clave** principales
- **Preguntas de examen** tipo opción múltiple

## Características ✨

- ✅ Interfaz web moderna y responsiva
- ✅ Procesa textos de hasta 10,000 caracteres
- ✅ Genera resúmenes, puntos clave y preguntas
- ✅ Soporte para múltiples APIs de IA (Groq, Ollama)
- ✅ Botón para copiar resultados
- ✅ Feedback visual de carga y errores
- ✅ Totalmente personalizable

## Requisitos previos 📋

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Una clave API de Groq (gratuita) O Ollama instalado localmente

## Instalación 🚀

### 1. Clonar o descargar el proyecto

```bash
cd tu-directorio-del-proyecto
```

### 2. Crear un entorno virtual (recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración 🔧

### Opción 1: Usar Groq (Recomendado - Gratuito)

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta gratuita
3. Copia tu API key
4. Abre `main.py` y reemplaza esta línea:
   ```python
   GROQ_API_KEY = "tu_clave_groq_aqui"  # Reemplazar con tu clave
   ```

### Opción 2: Usar Ollama (Totalmente local)

1. Descarga Ollama desde [ollama.ai](https://ollama.ai)
2. Instálalo y ejecútalo
3. Descarga un modelo:
   ```bash
   ollama pull mistral
   # o llama2, neural-chat, etc.
   ```
4. En `main.py`, comenta las líneas de Groq y descomenta Ollama:
   ```python
   # response_text = await call_groq_api(prompt)
   response_text = await call_ollama_api(prompt)
   ```

## Uso 🎯

### Ejecutar la aplicación

```bash
python main.py
```

O usa uvicorn directamente:

```bash
uvicorn main:app --reload
```

### Acceder a la aplicación

Abre tu navegador y ve a:
```
http://localhost:8000
```

## Estructura del proyecto 📁

```
proyecto/
├── main.py                 # Aplicación FastAPI principal
├── requirements.txt        # Dependencias de Python
├── README.md              # Este archivo
├── templates/
│   └── index.html         # Página principal (HTML)
└── static/
    ├── style.css          # Estilos (CSS)
    └── script.js          # Lógica del cliente (JavaScript)
```

## API Endpoints 🔌

### GET `/`
Retorna la página principal HTML

### POST `/api/process`
Procesa un texto y devuelve resultados

**Request:**
```json
{
    "text": "Tu texto aquí..."
}
```

**Response (éxito):**
```json
{
    "success": true,
    "summary": "Resumen del texto...",
    "key_points": "Puntos clave...",
    "questions": "Preguntas..."
}
```

**Response (error):**
```json
{
    "success": false,
    "error": "Mensaje de error"
}
```

### GET `/health`
Verifica que el servidor está activo

```json
{
    "status": "ok"
}
```

## Deployment 🌐

### Desplegar en Render

1. Sube tu código a GitHub
2. Ve a [render.com](https://render.com)
3. Crea un nuevo "Web Service"
4. Conecta tu repositorio de GitHub
5. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Agrega variables de entorno:
   - `GROQ_API_KEY`: Tu clave de Groq

### Desplegar en Railway

1. Sube tu código a GitHub
2. Ve a [railway.app](https://railway.app)
3. Crea un nuevo proyecto desde GitHub
4. Railway detectará automáticamente Python
5. Agrega la variable de entorno `GROQ_API_KEY`
6. Despliega

### Desplegar en Heroku

```bash
# Instalar Heroku CLI
heroku login
heroku create tu-app-nombre
git push heroku main
```

Asegúrate de configurar las variables de entorno:
```bash
heroku config:set GROQ_API_KEY=tu-clave
```

## Solución de problemas 🔍

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de tener el entorno virtual activado
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Instala las dependencias nuevamente
pip install -r requirements.txt
```

### Error: "Connection refused" en Groq
- Verifica tu conexión a internet
- Confirma que tu API key es correcta
- Revisa el estado de los servidores de Groq

### Error: "Cannot connect to Ollama"
- Asegúrate de que Ollama está corriendo
- Verifica que está en `http://localhost:11434`
- Prueba con: `curl http://localhost:11434/api/tags`

### La aplicación es lenta
- Si usas Ollama: Tu computadora podría no tener suficientes recursos
- Prueba con un modelo más pequeño (neural-chat en lugar de mistral)
- Si usas Groq: Puede estar debido a latencia de red

## Personalización 🎨

### Cambiar modelos de IA

**Para Groq:**
```python
# En main.py, línea ~75
"model": "mixtral-8x7b-32768",  # Cambiar por otro modelo
# Otros: llama2-70b-4096, gpt-3.5-turbo, etc.
```

**Para Ollama:**
```python
# En main.py, línea ~108
"model": "mistral",  # Cambiar por llama2, neural-chat, etc.
```

### Cambiar el prompt
En `main.py`, función `process_text_with_ai()`, modifica el `prompt` variable para cambiar cómo se procesa el texto.

### Personalizar CSS
Abre `static/style.css` y modifica las variables CSS al inicio:
```css
:root {
    --primary-color: #4f46e5;
    --secondary-color: #10b981;
    /* etc... */
}
```

## Seguridad ⚠️

- ⛔ **NO** compartas tu API key en público
- ⛔ **NO** subas archivos `.env` o credenciales a GitHub
- ✅ Usa variables de entorno en producción
- ✅ Implementa rate limiting en producción
- ✅ Valida todos los inputs del usuario

### Ejemplo con variables de entorno

```python
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

```bash
# En tu terminal antes de ejecutar:
export GROQ_API_KEY="tu-clave-aqui"  # macOS/Linux
# o en Windows Powershell:
$env:GROQ_API_KEY="tu-clave-aqui"
```

## Limitaciones actuales ⚠️

- Máximo 10,000 caracteres por texto
- Requiere conexión a internet (para Groq)
- Los modelos de IA tienen un tiempo de respuesta variable
- La calidad de los resultados depende del modelo de IA

## Mejoras futuras 🚀

- [ ] Soporte para múltiples idiomas
- [ ] Guardar histórico de procesos
- [ ] Exportar resultados a PDF
- [ ] Autenticación de usuarios
- [ ] Integración con más APIs de IA
- [ ] Análisis de sentimientos
- [ ] Extracción automática de términos clave
- [ ] Dark mode

## Contribuciones 🤝

¡Las contribuciones son bienvenidas! Siéntete libre de:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia 📄

Este proyecto está disponible bajo la licencia MIT. Siéntete libre de usarlo, modificarlo y distribuirlo.

## Soporte 💬

Si tienes preguntas o problemas:
1. Revisa la sección de "Solución de problemas"
2. Crea un issue en GitHub
3. Consulta la documentación de FastAPI en [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## Recursos útiles 📚

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Groq Console](https://console.groq.com)
- [Ollama Documentation](https://ollama.ai)
- [MDN Web Docs](https://developer.mozilla.org)

---

**¡Hecho con ❤️ usando FastAPI!**

Última actualización: 2024
