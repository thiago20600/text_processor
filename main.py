"""
Aplicación FastAPI para procesar textos con IA
Genera resúmenes, puntos clave y preguntas de examen
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import json
from typing import Optional, Dict
import re
from collections import Counter
import os
import logging
from functools import lru_cache
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Text Processor")

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Montar archivos estáticos (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de la API de IA
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Validar que la API key está configurada
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY no está configurada en variables de entorno")
    raise ValueError("GROQ_API_KEY no está configurada. Crea un archivo .env con tu clave.")

logger.info("Aplicación iniciada correctamente")


# Diccionarios de idiomas
LANGUAGE_PROMPTS = {
    "es": "Analiza el siguiente texto y proporciona una respuesta ÚNICAMENTE en formato JSON válido",
    "en": "Analyze the following text and provide ONLY a valid JSON response",
    "fr": "Analysez le texte suivant et fournissez UNIQUEMENT une réponse JSON valide"
}

def create_analysis_prompt(text: str, language: str = "es") -> str:
    """
    Crea un prompt muy específico y estructurado que fuerza JSON como respuesta
    Soporta múltiples idiomas
    """
    lang = language.lower() if language.lower() in LANGUAGE_PROMPTS else "es"
    
    if lang == "es":
        prompt = f"""Analiza el siguiente texto y proporciona una respuesta ÚNICAMENTE en formato JSON válido (sin texto adicional antes o después).

TEXTO A ANALIZAR:
{text}

INSTRUCCIONES:
1. RESUMEN: Redacta un resumen de 2-3 oraciones que capture la esencia del texto sin copiarlo textualmente. Debe ser claro y conciso.
2. PUNTOS_CLAVE: Genera exactamente 3 puntos clave principales. Cada punto debe ser una frase clara y específica (no genérica).
3. PREGUNTAS: Crea exactamente 3 preguntas de examen que evalúen comprensión. Deben ser preguntas concretas basadas en el contenido específico.

RESPONDE ÚNICAMENTE CON ESTE JSON (sin markdown, sin explicaciones):
{{
    "resumen": "Tu resumen aquí (2-3 oraciones)",
    "puntos_clave": [
        "Primer punto clave específico",
        "Segundo punto clave específico",
        "Tercer punto clave específico"
    ],
    "preguntas": [
        "Primera pregunta específica del contenido?",
        "Segunda pregunta específica del contenido?",
        "Tercera pregunta específica del contenido?"
    ]
}}"""
    elif lang == "en":
        prompt = f"""Analyze the following text and provide ONLY a valid JSON response (no additional text before or after).

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. SUMMARY: Write a 2-3 sentence summary capturing the essence without copying verbatim. Must be clear and concise.
2. KEY_POINTS: Generate exactly 3 main key points. Each should be clear and specific (not generic).
3. QUESTIONS: Create exactly 3 exam questions evaluating comprehension. Must be concrete based on specific content.

RESPOND ONLY WITH THIS JSON (no markdown, no explanations):
{{
    "resumen": "Your summary here (2-3 sentences)",
    "puntos_clave": [
        "First specific key point",
        "Second specific key point",
        "Third specific key point"
    ],
    "preguntas": [
        "First specific content question?",
        "Second specific content question?",
        "Third specific content question?"
    ]
}}"""
    else:  # French
        prompt = f"""Analysez le texte suivant et fournissez UNIQUEMENT une réponse JSON valide (sans texte supplémentaire avant ou après).

TEXTE À ANALYSER:
{text}

INSTRUCTIONS:
1. RÉSUMÉ: Rédigez un résumé de 2-3 phrases capturant l'essence sans copier textuellement. Doit être clair et concis.
2. POINTS_CLÉS: Générez exactement 3 points clés principaux. Chacun doit être clair et spécifique (pas générique).
3. QUESTIONS: Créez exactement 3 questions d'examen évaluant la compréhension. Doivent être concrètes sur la base du contenu spécifique.

RÉPONDEZ UNIQUEMENT AVEC CE JSON (pas de markdown, pas d'explications):
{{
    "resumen": "Votre résumé ici (2-3 phrases)",
    "puntos_clave": [
        "Premier point clé spécifique",
        "Deuxième point clé spécifique",
        "Troisième point clé spécifique"
    ],
    "preguntas": [
        "Première question de contenu spécifique?",
        "Deuxième question de contenu spécifique?",
        "Troisième question de contenu spécifique?"
    ]
}}"""
    return prompt


def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """
    Extrae JSON válido de la respuesta, limpiando markdown y caracteres especiales
    """
    if not response_text:
        return None
    
    # Limpia markdown code blocks
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None


def validate_and_clean_response(data: Dict) -> Dict:
    """
    Valida y limpia la respuesta asegurando formato correcto
    """
    validated = {
        "resumen": "",
        "puntos_clave": [],
        "preguntas": []
    }
    
    # Valida resumen
    if "resumen" in data and isinstance(data["resumen"], str):
        resumen = data["resumen"].strip()
        # Limpia frases cortadas
        if resumen.endswith("..."):
            resumen = resumen[:-3].strip()
        # Asegura que termina con punto
        if resumen and not resumen.endswith(('.', '?', '!')):
            resumen += "."
        validated["resumen"] = resumen
    
    # Valida puntos clave
    if "puntos_clave" in data:
        if isinstance(data["puntos_clave"], list):
            validated["puntos_clave"] = [
                str(p).strip() for p in data["puntos_clave"] 
                if p and len(str(p).strip()) > 5
            ][:3]  # Máximo 3 puntos
    
    # Valida preguntas
    if "preguntas" in data:
        if isinstance(data["preguntas"], list):
            validated["preguntas"] = [
                str(q).strip() for q in data["preguntas"]
                if q and len(str(q).strip()) > 5
            ][:3]  # Máximo 3 preguntas
            # Asegura que terminen con ?
            validated["preguntas"] = [
                q if q.endswith('?') else q + '?' 
                for q in validated["preguntas"]
            ]
    
    return validated


@lru_cache(maxsize=128)
def _cache_key_generator(text_hash: str, language: str) -> tuple:
    """Genera clave para caché"""
    return (text_hash, language)

async def call_groq_api(text: str, language: str = "es") -> Dict:
    """
    Llama a la API de Groq con prompt mejorado
    Intenta obtener JSON estructurado
    LANZA ERROR SI FALLA (sin fallback local)
    Soporta múltiples idiomas
    """
    prompt = create_analysis_prompt(text, language)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Modelos a intentar en orden de preferencia
        # Estos son los modelos más confiables y accesibles en Groq
        modelos = [
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "llama2-70b-4096"
        ]
        
        last_error = None
        for modelo in modelos:
            data = {
                "model": modelo,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 1500
            }
            
            try:
                logger.debug(f"Intentando con modelo: {modelo}")
                response = await client.post(
                    GROQ_API_URL,
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
                logger.debug(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.debug(f"Response recibida, intentando parsear JSON...")
                    
                    # Intenta extraer JSON
                    json_data = extract_json_from_response(response_text)
                    if json_data:
                        validated = validate_and_clean_response(json_data)
                        if validated["resumen"] and validated["puntos_clave"] and validated["preguntas"]:
                            logger.info(f"Groq respondió correctamente con modelo: {modelo}")
                            return validated
                        else:
                            last_error = "Respuesta JSON inválida o incompleta"
                    else:
                        last_error = f"No se pudo parsear JSON de la respuesta"
                else:
                    last_error = f"Error {response.status_code} - {response.text[:100]}"
                    logger.error(f"{last_error}")
                    
            except Exception as e:
                last_error = f"Excepción con {modelo}: {str(e)}"
                logger.error(f"{last_error}")
                continue
        
        # Si llegamos aquí, todos los modelos fallaron
        error_msg = f"Groq API falló. {last_error}"
        logger.critical(f"{error_msg}")
        raise Exception(error_msg)


async def call_ollama_api(prompt: str) -> Optional[str]:
    """
    NO USADO - Solo Groq real para portfolio
    """
    pass


async def process_text_with_ai(text: str, language: str = "es") -> dict:
    """
    Procesa el texto SOLO con Groq API real
    Si Groq falla, retorna error
    Soporta múltiples idiomas
    """
    try:
        logger.info(f"Procesando con Groq API en idioma: {language}")
        groq_result = await call_groq_api(text, language)
        
        return {
            "success": True,
            "summary": groq_result.get("resumen", ""),
            "key_points": groq_result.get("puntos_clave", []),
            "questions": groq_result.get("preguntas", [])
        }
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error en procesamiento: {error_msg}")
        return {
            "success": False,
            "error": f"Groq API Error: {error_msg}",
            "summary": "",
            "key_points": [],
            "questions": []
        }


@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Sirve la página principal"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/process")
@limiter.limit("10/minute")  # 10 solicitudes por minuto
async def process_text(request: Request):
    """Endpoint para procesar texto"""
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        language = data.get("language", "es")  # Soporte multiidioma
        
        logger.info(f"Solicitud de procesamiento recibida - Longitud: {len(text)} caracteres, Idioma: {language}")
        
        if not text or len(text) < 10:
            logger.warning("Texto muy corto rechazado")
            return {
                "success": False,
                "error": "Por favor ingresa un texto con al menos 10 caracteres"
            }
        
        if len(text) > 10000:
            logger.warning("Texto muy largo rechazado")
            return {
                "success": False,
                "error": "El texto no puede exceder 10000 caracteres"
            }
        
        # Procesar con IA
        result = await process_text_with_ai(text, language)
        
        if result["success"]:
            logger.info("Procesamiento completado exitosamente")
        else:
            logger.error(f"Error en procesamiento: {result.get('error')}")
        
        return result
    
    except Exception as e:
        logger.exception(f"Error procesando solicitud")
        return {
            "success": False,
            "error": f"Error procesando solicitud: {str(e)}"
        }


@app.get("/health")
async def health_check():
    """Endpoint para verificar que el servidor está activo"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
