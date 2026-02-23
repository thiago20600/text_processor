## 🚀 GUÍA DE INICIO RÁPIDO

### Instalación en 5 minutos

#### **Paso 1: Obtener clave API (3 min)**

Ve a [console.groq.com](https://console.groq.com) y:
1. Crea una cuenta gratuita
2. Copia tu API key

#### **Paso 2: Configurar la aplicación (1 min)**

1. Abre `main.py` 
2. Encuentra esta línea (alrededor de la línea 50):
   ```python
   GROQ_API_KEY = "tu_clave_groq_aqui"
   ```
3. Reemplázala con tu clave:
   ```python
   GROQ_API_KEY = "gsk_tu_clave_aqui..."
   ```

#### **Paso 3: Ejecutar (1 min)**

**Windows:**
```bash
venv\Scripts\activate
python main.py
```

**macOS/Linux:**
```bash
source venv/bin/activate
python main.py
```

#### **Paso 4: Usar la aplicación**

Abre tu navegador en:
```
http://localhost:8000
```

✅ ¡Listo! Pega un texto y comienza a procesar.

---

## 💡 Alternativa: Usar Ollama (completamente local)

Si prefieres no usar APIs externas:

1. **Descargar Ollama**: [ollama.ai](https://ollama.ai)
2. **Instalar y ejecutar**:
   ```bash
   ollama pull mistral
   ollama serve
   ```
3. **En otra terminal, edita `main.py`** y comenta Groq:
   ```python
   # response_text = await call_groq_api(prompt)
   response_text = await call_ollama_api(prompt)
   ```
4. **Ejecuta la aplicación**:
   ```bash
   python main.py
   ```

---

## 📁 Estructura del proyecto

```
proyecto/
├── main.py              ← Aplicación principal (edit aquí la API key)
├── requirements.txt     ← Dependencias
├── setup.bat            ← Setup automático (Windows)
├── setup.sh             ← Setup automático (macOS/Linux)
├── templates/
│   └── index.html       ← Interfaz web
└── static/
    ├── style.css        ← Estilos
    └── script.js        ← JavaScript del cliente
```

---

## 🎯 Características principales

✅ **Resúmenes automáticos** - Generados por IA en segundos  
✅ **Puntos clave** - Identifica lo más importante  
✅ **Preguntas de examen** - Para estudiar el contenido  
✅ **Interfaz hermosa** - Diseño responsivo y moderno  
✅ **Copiar resultados** - Un click para copiar al portapapeles  
✅ **Offline disponible** - Usa Ollama para funcionar sin internet  

---

## ⚠️ Solución rápida de problemas

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "Connection refused"**
- Groq: Verifica tu API key y conexión a internet
- Ollama: Asegúrate de ejecutar `ollama serve` en otra terminal

**La aplicación está lenta**
- Si usas Ollama: Necesita más RAM/GPU
- Prueba con un modelo más ligero: `ollama pull neural-chat`

---

## 📖 Más información

Ver [README.md](README.md) para documentación completa, opciones de deployment y personalización.
