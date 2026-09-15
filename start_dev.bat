@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

set "PYTHON_EXE=python"
if exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
)

set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

echo ========================================================
echo   MIMAROS Auto Posting App - Dev Server Launcher
echo ========================================================
echo.
echo [1/3] Starte Backend API Server...
start "MIMAROS Backend" cmd /k "chcp 65001 >nul && cd /d ""%BACKEND_DIR%"" && set PYTHONIOENCODING=utf-8 && set PYTHONUTF8=1 && ""%PYTHON_EXE%"" -u main.py"

echo [2/3] Starte Frontend (Next.js)...
start "MIMAROS Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev -- -p 3001"

echo [3/3] Warte 5 Sekunden auf Initialisierung...
timeout /t 5 >nul

echo.
echo ========================================================
echo   MIMAROS App laeuft lokal unter:
echo   - Frontend: http://localhost:3001
echo   - Backend:  http://127.0.0.1:8000
echo   - API Docs: http://127.0.0.1:8000/docs
echo ========================================================

