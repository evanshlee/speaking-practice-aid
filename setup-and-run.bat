@echo off
setlocal enabledelayedexpansion

rem Speaking Practice Aid - Complete Setup and Run Script (Windows)
rem This script installs all dependencies (backend + frontend) and runs both servers

set "PROJECT_DIR=%~dp0"
set "CLIENT_DIR=%PROJECT_DIR%client"
set "SERVER_DIR=%PROJECT_DIR%server"
set "VENV_DIR=%PROJECT_DIR%venv"

echo ========================================
echo   Speaking Practice Aid
echo   Complete Setup ^& Run
echo ========================================
echo.

rem Check prerequisites
echo Checking prerequisites...
echo.

set MISSING_DEPS=0

rem Check Python
where python >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set "PYTHON_MAJOR=%%a"
        set "PYTHON_MINOR=%%b"
    )
    if !PYTHON_MAJOR! equ 3 if !PYTHON_MINOR! geq 9 (
        echo [OK] Python !PYTHON_VERSION!
    ) else (
        echo [X] Python 3.9+ required ^(found: !PYTHON_VERSION!^)
        echo     Install from https://www.python.org/downloads/
        set MISSING_DEPS=1
    )
) else (
    echo [X] Python 3.9+ not found
    echo     Install from https://www.python.org/downloads/
    set MISSING_DEPS=1
)

rem Check Node.js
where node >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%v in ('node --version') do set "NODE_VERSION=%%v"
    echo [OK] Node.js !NODE_VERSION!
) else (
    echo [X] Node.js not found
    echo     Install from https://nodejs.org/
    set MISSING_DEPS=1
)

rem Check FFmpeg
where ffmpeg >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] FFmpeg found
) else (
    echo [X] FFmpeg not found
    echo     Install with: winget install Gyan.FFmpeg
    set MISSING_DEPS=1
)

if !MISSING_DEPS! equ 1 (
    echo.
    echo Please install missing prerequisites and try again.
    exit /b 1
)

echo.
echo All prerequisites satisfied!
echo.

rem [1/4] Create virtual environment
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [1/4] Creating Python virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo       Failed to create virtual environment.
        exit /b 1
    )
    echo       Virtual environment created
) else (
    echo [1/4] Virtual environment already exists
)
echo.

rem [2/4] Install backend dependencies
echo [2/4] Installing backend dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
pip install -q -r "%SERVER_DIR%\requirements.txt"
if errorlevel 1 (
    echo       Failed to install backend dependencies
    exit /b 1
)
echo       Backend dependencies installed
echo.

rem [3/4] Install frontend dependencies
echo [3/4] Installing frontend dependencies...
cd /d "%CLIENT_DIR%"
call npm install --silent
if errorlevel 1 (
    echo       Failed to install frontend dependencies
    exit /b 1
)
echo       Frontend dependencies installed
echo.

rem [4/4] Start servers
echo [4/4] Starting servers...
echo.
echo   Starting Backend Server (FastAPI)...
start "Backend - Speaking Practice" /d "%SERVER_DIR%" "%VENV_DIR%\Scripts\python.exe" main.py
echo       Backend URL: http://localhost:8000
echo.

echo   Starting Client Server (Vite)...
start "Client - Speaking Practice" /d "%CLIENT_DIR%" cmd /c "npm run dev"
echo.

echo ========================================
echo Setup complete! Both servers are running!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo ========================================
echo.
echo Close the server windows to stop them.
