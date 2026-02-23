#!/usr/bin/env python3
"""
Script de verificación previa para la aplicación AI Text Processor
Verifica que todo está correctamente configurado
"""

import sys
import subprocess
import os
from pathlib import Path

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

def check_groq_key():
    """Verifica si la clave de Groq está configurada"""
    from pathlib import Path
    
    # Leer main.py
    main_content = Path("main.py").read_text()
    
    if 'GROQ_API_KEY = "tu_clave_groq_aqui"' in main_content:
        print("⚠️  GROQ_API_KEY no está configurada")
        print("   1. Ve a https://console.groq.com")
        print("   2. Copia tu API key")
        print("   3. En main.py línea ~50, reemplaza:")
        print("      GROQ_API_KEY = \"tu_clave_aqui...\"")
        return False
    
    print("✅ GROQ_API_KEY parece estar configurada")
    return True

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
        print("Luego abre: http://localhost:8000")
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
        ("Configuración Groq", check_groq_key),
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
