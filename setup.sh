#!/bin/bash
# Script para instalar y ejecutar la aplicación en macOS/Linux

echo ""
echo "========================================"
echo "AI Text Processor - Setup Script"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    echo "Instálalo con: brew install python3 (macOS) o apt-get install python3 (Linux)"
    exit 1
fi

echo "[1/4] Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error al crear el entorno virtual"
    exit 1
fi

echo "[2/4] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error al activar el entorno virtual"
    exit 1
fi

echo "[3/4] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error al instalar dependencias"
    exit 1
fi

echo "[4/4] Configuración completada!"
echo ""
echo "========================================"
echo "Próximos pasos:"
echo "========================================"
echo ""
echo "1. Abre el archivo main.py"
echo "2. En la línea ~50, reemplaza:"
echo "   GROQ_API_KEY = \"tu_clave_groq_aqui\""
echo "   con tu clave de API de Groq (gratuita en https://console.groq.com)"
echo ""
echo "3. Ejecuta: python main.py"
echo ""
echo "4. Abre en tu navegador: http://localhost:8000"
echo ""
echo "========================================"
echo ""
