#!/usr/bin/env python3
"""
Script de verificación previa para la aplicación AI Text Processor
Verifica que todo está correctamente configurado
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_python_version():
    """Verifica que Python 3.8+ está instalado"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        print(f"   Tu versión: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def check_files_exist():
    """Verifica que todos los archivos necesarios existen"""
    required_files = [
        "main.py",
        "requirements.txt",
        "templates/index.html",
        "static/style.css",
        "static/script.js",
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} NO ENCONTRADO")
            all_exist = False
    
    return all_exist

def check_venv():
    """Verifica si existe y está activado el entorno virtual"""
    venv_exists = Path("venv").exists()
    
    if not venv_exists:
        print("⚠️  No se encontró entorno virtual 'venv'")
        print("   Ejecuta: python -m venv venv")
        return False
    
    print("✅ Entorno virtual 'venv' encontrado")
    return True

def check_dependencies():
    """Verifica que las dependencias están instaladas"""
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} instalado")
    except ImportError:
        print("❌ FastAPI no está instalado")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn {uvicorn.__version__} instalado")
    except ImportError:
        print("❌ Uvicorn no está instalado")
        return False
    
    try:
        import httpx
        print(f"✅ HTTPX instalado")
    except ImportError:
        print("❌ HTTPX no está instalado")
        return False
    
    return True

def check_env_file():
    """Verifica que exista el archivo .env"""
    if not Path(".env").exists():
        print("❌ No se encontró archivo .env")
        print("   Crea un .env con GROQ_API_KEY, SECRET_KEY y DB_*")
        return False
    print("✅ Archivo .env encontrado")
    return True


def check_env_variables():
    """Valida variables de entorno críticas"""
    required_vars = [
        "GROQ_API_KEY",
        "SECRET_KEY",
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    ]

    all_ok = True
    for var in required_vars:
        value = os.getenv(var, "").strip()
        if value:
            print(f"✅ {var} configurada")
        else:
            print(f"❌ {var} faltante o vacía")
            all_ok = False

    return all_ok


def check_db_connection():
    """Intenta conectarse a MySQL con las variables actuales"""
    try:
        import mysql.connector
    except ImportError:
        print("❌ mysql-connector-python no está instalado")
        return False

    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "text_processor_db"),
            connection_timeout=5,
        )
        conn.close()
        print("✅ Conexión a MySQL exitosa")
        return True
    except Exception as e:
        print(f"❌ No se pudo conectar a MySQL: {e}")
        return False

def print_header():
    """Imprime el header"""
    print("\n" + "="*50)
    print("  🔍 Verificación previa - AI Text Processor")
    print("="*50 + "\n")

def print_footer(all_ok):
    """Imprime el footer"""
    print("\n" + "="*50)
    if all_ok:
        print("✅ ¡Todo está listo!")
        print("\nEjecuta: python main.py")
        print("Luego abre: http://localhost:8001")
    else:
        print("⚠️  Por favor soluciona los errores arriba")
    print("="*50 + "\n")

def main():
    print_header()
    
    checks = [
        ("Python Version", check_python_version),
        ("Archivos necesarios", check_files_exist),
        ("Entorno virtual", check_venv),
        ("Dependencias", check_dependencies),
        ("Archivo .env", check_env_file),
        ("Variables de entorno", check_env_variables),
        ("Conexión MySQL", check_db_connection),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error verificando: {e}")
            results.append(False)
    
    all_ok = all(results)
    print_footer(all_ok)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
