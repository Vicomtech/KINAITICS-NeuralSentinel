@echo off
echo ========================================
echo   NeuralSentinel - Build para Windows
echo ========================================
echo.

REM Verificar Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no esta instalado.
    pause
    exit /b 1
)

REM 1. Instalar dependencias de Frontend
echo [1/5] Instalando dependencias de Node.js...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al instalar dependencias npm.
    pause
    exit /b 1
)

REM 2. Preparar Backend (Python)
echo [2/5] Preparando entorno Python...
if not exist "backend\venv" (
    echo Creando entorno virtual...
    python -m venv backend\venv
)

call backend\venv\Scripts\activate
echo Instalando dependencias Python...
pip install -r backend\requirements.txt
pip install pyinstaller pywin32
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al instalar dependencias pip.
    pause
    exit /b 1
)

REM 3. Compilar Backend a .exe
echo [3/5] Compilando backend a ejecutable...
cd backend
pyinstaller --clean --noconfirm --onefile --name app --add-data "plugins;plugins" --hidden-import="flask" --hidden-import="flask_cors" --hidden-import="numpy" app.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al compilar el backend.
    cd ..
    pause
    exit /b 1
)

REM Mover el ejecutable y limpiar
echo Moviendo ejecutable...
move /Y "dist\app.exe" "app.exe"
rmdir /S /Q "build"
rmdir /S /Q "dist"
del "app.spec"
cd ..

echo [INFO] Backend compilado en backend/app.exe

REM 4. Generar Icono (si no existe)
if not exist "build\icon.png" (
    if not exist "build" mkdir build
    echo [WARN] Icono no encontrado, asegúrate de tener build/icon.png
)

REM 5. Construir Ejecutable de Windows
echo [5/5] Generando instalador Windows (Electron Builder)...
call npm run build:win
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo en el build de Electron.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo El instalador se encuentra en la carpeta 'dist'
echo.
REM pause - Comentado para automatizacion
exit /b 0
