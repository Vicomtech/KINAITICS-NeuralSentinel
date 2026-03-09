@echo off
echo ========================================
echo   NeuralSentinel - Instalacion para Windows
echo ========================================
echo.

REM Verificar Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no esta instalado
    echo Por favor instala Node.js desde https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no esta instalado
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias de Node.js...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo la instalacion de dependencias de Node.js
    pause
    exit /b 1
)

echo.
echo [2/4] Creando entorno virtual de Python...
cd backend
if exist venv (
    echo Entorno virtual ya existe, omitiendo...
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fallo la creacion del entorno virtual
        cd ..
        pause
        exit /b 1
    )
)

echo.
echo [3/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo [4/4] Instalando dependencias de Python...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo la instalacion de dependencias de Python
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo   Instalacion completada exitosamente!
echo ========================================
echo.
echo Para ejecutar la aplicacion, usa: start.bat
echo.
pause
