# Instrucciones para desplegar en Railway

Este proyecto puede ser desplegado en Railway.app

## ⚠️ IMPORTANTE - Evitar Error "executable 'set' could not be found"

Railway corre en **Linux**, no Windows. NO uses comandos de Windows como `set`. 
Nuestros archivos ya están configurados para Linux.

---

## Pasos de Deployment en Railway:

### 1. Conectar GitHub
- Ir a https://railway.app
- Click en "New Project"
- Selecciona "Deploy from GitHub repo"
- Conecta tu cuenta y selecciona: `thiago20600/text_processor`

### 2. Variables de Entorno
En el dashboard de Railway, agrega:
```
Key: GROQ_API_KEY
Value: gsk_xxxxxxxxxxxxx  (tu clave aquí)
```

### 3. Configuración Automática
Railway detectará automáticamente:
- ✓ Procfile (especifica cómo ejecutar)
- ✓ requirements.txt (instala dependencias)
- ✓ Python 3.x

### 4. Deploy
- Click en "Deploy"
- Railway construirá la imagen Docker
- Tu app estará disponible en unos minutos

---

## Verificar que está corriendo

Una vez desplegado:
1. Railway te dará una URL pública (ej: `https://tu-app.railway.app`)
2. Abre esa URL en el navegador
3. Deberías ver la interfaz de AI Text Processor

---

## En caso de error

Si ves "the executable 'set' could not be found":
- ✅ Ya está solucionado (actualiza el código)
- ✅ Procfile está configurado correctamente
- ✅ render.yaml está configurado para Linux

Si aún tienes problemas:
1. Verifica que GROQ_API_KEY está en variables de entorno
2. Revisa los logs en el dashboard de Railway
3. Asegúrate que requirements.txt tiene todas las dependencias

---

## Estructura de archivos importante

```
requirements.txt        ← Railway lo usa para instalar deps
Procfile               ← Railway lo usa para iniciar app
.env.example           ← Plantilla (NO subir .env real a GitHub)
main.py                ← Código de la app
```

---

## Variables de Entorno Requeridas

| Variable | Valor | Donde |
|----------|-------|-------|
| GROQ_API_KEY | tu-clave-aqui | Dashboard Railway |

Nota: No añadas el .env en Railway, usa las variables en el dashboard.

---

## URL Final

Tu aplicación estará disponible en:
```
https://tu-proyecto.railway.app
```

Comparte este link con quien quieras! 🚀

---

## Solución de Problemas

| Error | Solución |
|-------|----------|
| "executable 'set'" | Ya solucionado ✓ |
| "Module not found" | Verifica requirements.txt |
| "GROQ_API_KEY error" | Agrega en variables de entorno |
| "Port already in use" | Reinicia el deploy |

---

## ¿Quieres desplegar en otro lugar?

- **Render.com** → `render.yaml` ya está configurado
- **Heroku** → `Procfile` funciona
- **Docker/Local** → `docker-compose.yml` disponible

