#!/bin/bash

echo "========================================"
echo "  NeuralSentinel - Instalación para Linux"
echo "========================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Node.js no está instalado"
    echo "Por favor instala Node.js desde https://nodejs.org/"
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} npm no está instalado"
    echo "Por favor instala npm"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python3 no está instalado"
    echo "Por favor instala Python3"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} pip3 no está instalado"
    echo "Por favor instala pip3"
    exit 1
fi

echo -e "${GREEN}[1/4]${NC} Instalando dependencias de Node.js..."
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Falló la instalación de dependencias de Node.js"
    exit 1
fi

echo ""
echo -e "${GREEN}[2/4]${NC} Creando entorno virtual de Python..."
cd backend

if [ -d "venv" ]; then
    echo -e "${YELLOW}Entorno virtual ya existe, omitiendo...${NC}"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Falló la creación del entorno virtual"
        cd ..
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}[3/4]${NC} Activando entorno virtual..."
source venv/bin/activate

echo ""
echo -e "${GREEN}[4/4]${NC} Instalando dependencias de Python..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Falló la instalación de dependencias de Python"
    cd ..
    exit 1
fi

cd ..

echo ""
echo "========================================"
echo -e "${GREEN}  Instalación completada exitosamente!${NC}"
echo "========================================"
echo ""
echo "Para ejecutar la aplicación, usa: ./start.sh"
echo ""
