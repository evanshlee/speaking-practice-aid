@echo off
setlocal

rem Speaking Practice Aid - Start Script (Windows)
rem Runs Vite client and FastAPI backend simultaneously.

set "PROJECT_DIR=%~dp0"
set "CLIENT_DIR=%PROJECT_DIR%client"
set "SERVER_DIR=%PROJECT_DIR%server"
set "VENV_DIR=%PROJECT_DIR%venv"

echo ========================================
echo   Speaking Practice Aid
echo ========================================
echo.

echo [1/2] Starting Backend Server (FastAPI)...
start "Backend - Speaking Practice" /d "%SERVER_DIR%" "%VENV_DIR%\Scripts\python.exe" main.py
echo       Backend URL: http://localhost:8000
echo.

echo [2/2] Starting Client Server (Vite)...
start "Client - Speaking Practice" /d "%CLIENT_DIR%" cmd /c "npm run dev"
echo.

echo ========================================
echo Both servers are running!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo ========================================
echo.
echo Close the server windows to stop them.
