# Instrucciones para desplegar en Railway

Este proyecto puede ser desplegado en Railway.app

## Pasos:

1. Crear cuenta en railway.app
2. Conectar tu repositorio GitHub
3. Railway detectará automáticamente Python
4. Agregar variable de entorno:
   - Key: GROQ_API_KEY
   - Value: tu-clave-aqui

## Variables de entorno desde archivo

Si tienes un .env local, cópialo en el dashboard de Railway.

## Verificar deployment

Una vez desplegado, Railway te dará una URL pública.
Tu app estará disponible en: https://tu-app.railway.app

## Problemas comunes

Si falla el build:
- Asegúrate que requirements.txt está actualizado
- Verifica que Python 3.8+ está especificado
