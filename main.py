"""
Aplicación FastAPI para procesar textos con IA
Genera resúmenes, puntos clave y preguntas de examen
"""

from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import pytesseract
from PIL import Image
import io
import json
from typing import Optional, Dict
import re
from collections import Counter
import os
import logging
from functools import lru_cache
import pytesseract
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF
from models import UserCreate, UserLogin, Token, SummarySave
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from db import get_connection

# Cargar variables de entorno
load_dotenv()

# Configurar ruta de Tesseract solo si se define explícitamente
# (evita romper deploys Linux por rutas locales de Windows)
tesseract_cmd = os.getenv("TESSERACT_CMD", "").strip()
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


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

# Endpoint para OCR de imagen
@app.post("/api/ocr")
@limiter.limit("10/minute")
async def ocr_image(request: Request, file: UploadFile = File(...)):
    """Endpoint para extraer texto de una imagen usando OCR"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image, lang="spa+eng")
        if not text.strip():
            return {"success": False, "error": "No se detectó texto en la imagen."}
        return {"success": True, "text": text}
    except Exception as e:
        logger.exception("Error procesando imagen para OCR")
        return {"success": False, "error": f"Error procesando imagen: {str(e)}"}

# Endpoint para OCR de PDF
@app.post("/api/pdf-ocr")
@limiter.limit("5/minute")
async def ocr_pdf(request: Request, file: UploadFile = File(...)):
    """Endpoint para extraer texto de un PDF usando OCR"""
    try:
        contents = await file.read()
        # Intentar extraer texto directo (PDF digital)
        text = ""
        with fitz.open(stream=contents, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        # Si no se extrajo texto (PDF escaneado), usar OCR
        if not text.strip():
            images = convert_from_bytes(contents)
            for image in images:
                text += pytesseract.image_to_string(image, lang="spa+eng") + "\n"
        if not text.strip():
            return {"success": False, "error": "No se detectó texto en el PDF."}
        return {"success": True, "text": text}
    except Exception as e:
        logger.exception("Error procesando PDF para OCR")
        return {"success": False, "error": f"Error procesando PDF: {str(e)}"}

# Validar que la API key está configurada
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

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


def get_summary_length_guidance(text: str, language: str) -> tuple[str, str]:
    char_count = len(text or "")

    if char_count <= 1000:
        ranges = {
            "es": ("2-3 oraciones", "2-3 oraciones"),
            "en": ("2-3 sentences", "2-3 sentences"),
            "fr": ("2-3 phrases", "2-3 phrases"),
        }
    elif char_count <= 4000:
        ranges = {
            "es": ("4-6 oraciones", "4-6 oraciones"),
            "en": ("4-6 sentences", "4-6 sentences"),
            "fr": ("4-6 phrases", "4-6 phrases"),
        }
    elif char_count <= 8000:
        ranges = {
            "es": ("6-8 oraciones", "6-8 oraciones"),
            "en": ("6-8 sentences", "6-8 sentences"),
            "fr": ("6-8 phrases", "6-8 phrases"),
        }
    else:
        ranges = {
            "es": ("8-10 oraciones", "8-10 oraciones"),
            "en": ("8-10 sentences", "8-10 sentences"),
            "fr": ("8-10 phrases", "8-10 phrases"),
        }

    return ranges[language]

def create_analysis_prompt(text: str, language: str = "es") -> str:
    """
    Crea un prompt muy específico y estructurado que fuerza JSON como respuesta
    Soporta múltiples idiomas
    """
    lang = language.lower() if language.lower() in LANGUAGE_PROMPTS else "es"
    summary_range_text, summary_example_text = get_summary_length_guidance(text, lang)
    
    if lang == "es":
        prompt = f"""Analiza el siguiente texto y proporciona una respuesta ÚNICAMENTE en formato JSON válido (sin texto adicional antes o después).

TEXTO A ANALIZAR:
{text}

INSTRUCCIONES:
1. RESUMEN: Redacta un resumen de {summary_range_text} que capture la esencia del texto sin copiarlo textualmente. Debe ser claro y conciso.
2. PUNTOS_CLAVE: Genera exactamente 3 puntos clave principales. Cada punto debe ser una frase clara y específica (no genérica).
3. PREGUNTAS: Crea exactamente 3 preguntas de examen que evalúen comprensión. Deben ser preguntas concretas basadas en el contenido específico.

RESPONDE ÚNICAMENTE CON ESTE JSON (sin markdown, sin explicaciones):
{{
    "resumen": "Tu resumen aquí ({summary_example_text})",
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
1. SUMMARY: Write a {summary_range_text} summary capturing the essence without copying verbatim. Must be clear and concise.
2. KEY_POINTS: Generate exactly 3 main key points. Each should be clear and specific (not generic).
3. QUESTIONS: Create exactly 3 exam questions evaluating comprehension. Must be concrete based on specific content.

RESPOND ONLY WITH THIS JSON (no markdown, no explanations):
{{
    "resumen": "Your summary here ({summary_example_text})",
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
1. RÉSUMÉ: Rédigez un résumé de {summary_range_text} capturant l'essence sans copier textuellement. Doit être clair et concis.
2. POINTS_CLÉS: Générez exactement 3 points clés principaux. Chacun doit être clair et spécifique (pas générique).
3. QUESTIONS: Créez exactement 3 questions d'examen évaluant la compréhension. Doivent être concrètes sur la base du contenu spécifique.

RÉPONDEZ UNIQUEMENT AVEC CE JSON (pas de markdown, pas d'explications):
{{
    "resumen": "Votre résumé ici ({summary_example_text})",
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


@app.post("/api/register", response_model=Token)
def register(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        hashed_pw = get_password_hash(user.password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed_pw))
        conn.commit()
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/token", response_model=Token)
def login(form_data: UserLogin):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/save-summary")
def save_summary(summary: SummarySave, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO summaries (user_id, title, summary, key_points, questions) VALUES (%s, %s, %s, %s, %s)",
            (user['id'], summary.title, summary.summary, summary.key_points, summary.questions)
        )
        conn.commit()
        return {"success": True, "message": "Resumen guardado"}
    finally:
        cursor.close()
        conn.close()

@app.get("/api/my-summaries")
def get_my_summaries(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, title, summary, key_points, questions, created_at FROM summaries WHERE user_id = %s ORDER BY created_at DESC", (user['id'],))
        summaries = cursor.fetchall()
        return {"success": True, "summaries": summaries}
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
