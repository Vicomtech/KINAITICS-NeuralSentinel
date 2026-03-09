#!/bin/bash

echo "========================================"
echo "  NeuralSentinel - Iniciando aplicación"
echo "========================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar instalación
if [ ! -d "node_modules" ]; then
    echo -e "${RED}[ERROR]${NC} Dependencias no instaladas. Ejecuta ./install.sh primero"
    exit 1
fi

if [ ! -d "backend/venv" ]; then
    echo -e "${RED}[ERROR]${NC} Entorno virtual no encontrado. Ejecuta ./install.sh primero"
    exit 1
fi

echo -e "${GREEN}Iniciando backend de Python...${NC}"
echo ""

# Iniciar backend en segundo plano
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

echo -e "${YELLOW}Backend PID: $BACKEND_PID${NC}"
echo "Esperando a que el backend inicie..."
sleep 3

echo ""
echo -e "${GREEN}Iniciando aplicación Electron...${NC}"
echo ""

# Iniciar frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo -e "${GREEN}  Aplicación iniciada!${NC}"
echo "========================================"
echo ""
echo "Procesos:"
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Para detener la aplicación:${NC}"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "O presiona Ctrl+C para detener ambos procesos"
echo ""

# Manejar Ctrl+C
trap "echo ''; echo 'Deteniendo aplicación...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Esperar a que los procesos terminen
wait
