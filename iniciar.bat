@echo off
title PIPAC - Plataforma de Prediccion y Analisis de Criminalidad
cd /d "%~dp0"

echo ============================================
echo  PIPAC - Iniciando plataforma
echo ============================================
echo.

if not exist ".venv\" (
    echo [1/3] Creando entorno virtual...
    python -m venv .venv
)

echo [1/3] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [2/3] Instalando dependencias...
pip install -r requirements.txt -q

echo [3/3] Iniciando servicios...
echo.

start "PIPAC-API" cmd /c "call .venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "PIPAC-Dashboard" cmd /c "call .venv\Scripts\activate.bat && python -m dashboard.app"

echo.
echo ============================================
echo  Servicios iniciados:
echo   API:        http://localhost:8000
echo   Dashboard:  http://localhost:8050
echo ============================================
echo.
echo  Presiona cualquier tecla para cerrar ambos servicios...
pause >nul

echo Cerrando servicios...
taskkill /f /fi "WINDOWTITLE eq PIPAC-API" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq PIPAC-Dashboard" >nul 2>&1
echo Hecho.
