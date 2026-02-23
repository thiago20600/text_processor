@echo off
REM Script para instalar y ejecutar la aplicación en Windows

echo.
echo ========================================
echo AI Text Processor - Setup Script
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado o no está en PATH
    echo Descarga Python desde https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo Error al crear el entorno virtual
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error al activar el entorno virtual
    pause
    exit /b 1
)

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error al instalar dependencias
    pause
    exit /b 1
)

echo [4/4] Configuración completada!
echo.
echo ========================================
echo Próximos pasos:
echo ========================================
echo.
echo 1. Abre el archivo main.py
echo 2. En la línea ~50, reemplaza:
echo    GROQ_API_KEY = "tu_clave_groq_aqui"
echo    con tu clave de API de Groq (gratuita en https://console.groq.com)
echo.
echo 3. Ejecuta: python main.py
echo.
echo 4. Abre en tu navegador: http://localhost:8000
echo.
echo ========================================
echo.
pause
