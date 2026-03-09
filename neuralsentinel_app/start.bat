@echo off
echo ========================================
echo   NeuralSentinel - Iniciando aplicacion
echo ========================================
echo.

REM Verificar si esta instalado
if not exist node_modules (
    echo [ERROR] Dependencias no instaladas. Ejecuta install.bat primero
    pause
    exit /b 1
)

if not exist backend\venv (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta install.bat primero
    pause
    exit /b 1
)

echo Iniciando backend de Python...
echo.
start "ML Auditor Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

echo Esperando a que el backend inicie...
timeout /t 3 /nobreak >nul

echo.
echo Iniciando aplicacion Electron...
echo.
start "ML Auditor Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   Aplicacion iniciada!
echo ========================================
echo.
echo Se han abierto dos ventanas:
echo   1. Backend (Python Flask)
echo   2. Frontend (Electron)
echo.
echo Para detener la aplicacion, cierra ambas ventanas.
echo.
pause
