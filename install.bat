@echo off
chcp 65001 >nul
title CRM — Installation

echo.
echo  ========================================
echo         CRM - Installation
echo  ========================================
echo.

:: ──────────────────────────────────────────────
::  1. Detect project folder
:: ──────────────────────────────────────────────
if exist "manage.py" (
    echo  [OK] Already inside CRM project folder.
    set "PROJECT_DIR=%CD%"
) else if exist "CRM\manage.py" (
    echo  [OK] Found CRM subfolder, switching...
    cd CRM
    set "PROJECT_DIR=%CD%"
) else (
    echo  [*] Cloning repository...
    git clone https://github.com/OlegUhakov/CRM.git
    if errorlevel 1 (
        echo  [ERROR] Git clone failed.
        pause
        exit /b 1
    )
    cd CRM
    set "PROJECT_DIR=%CD%"
)

echo  [DIR] %PROJECT_DIR%
echo.

:: ──────────────────────────────────────────────
::  2. Check prerequisites
:: ──────────────────────────────────────────────
echo  Checking prerequisites...

where python >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.14+ and add to PATH.
    pause
    exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found. Install Git and add to PATH.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js not found. Install Node.js 20+ and add to PATH.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] npm not found. Install Node.js (includes npm).
    pause
    exit /b 1
)

echo  [OK] All prerequisites found.
echo.

:: ──────────────────────────────────────────────
::  3. Python version check
:: ──────────────────────────────────────────────
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  [OK] Python %PY_VER%
echo.

:: ──────────────────────────────────────────────
::  4. Virtual environment
:: ──────────────────────────────────────────────
if exist "venv\Scripts\python.exe" (
    echo  [OK] Virtual environment already exists.
) else (
    echo  [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)

set "PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"
set "PIP=%PROJECT_DIR%\venv\Scripts\pip.exe"
echo.

:: ──────────────────────────────────────────────
::  5. Install Python dependencies
:: ──────────────────────────────────────────────
echo  [*] Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip >nul 2>&1

echo  [*] Installing Python dependencies...
"%PIP%" install -r requirements.txt
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)
echo  [OK] Python dependencies installed.
echo.

:: ──────────────────────────────────────────────
::  6. Install Node dependencies
:: ──────────────────────────────────────────────
echo  [*] Installing Node dependencies...
call npm install
if errorlevel 1 (
    echo  [ERROR] npm install failed.
    pause
    exit /b 1
)
echo  [OK] Node dependencies installed.
echo.

:: ──────────────────────────────────────────────
::  7. Build Tailwind CSS
:: ──────────────────────────────────────────────
echo  [*] Building Tailwind CSS...
call npm run build
if errorlevel 1 (
    echo  [ERROR] Tailwind build failed.
    pause
    exit /b 1
)
echo  [OK] Tailwind CSS built.
echo.

:: ──────────────────────────────────────────────
::  8. Database migrations
:: ──────────────────────────────────────────────
echo  [*] Running database migrations...
"%PYTHON%" manage.py migrate
if errorlevel 1 (
    echo  [ERROR] Migrations failed.
    pause
    exit /b 1
)
echo  [OK] Database migrated.
echo.

:: ──────────────────────────────────────────────
::  9. Create superuser
:: ──────────────────────────────────────────────
echo  [*] Creating superuser...
"%PYTHON%" manage.py createsuperuser
echo.

:: ──────────────────────────────────────────────
::  Done
:: ──────────────────────────────────────────────
echo  ========================================
echo         Installation completed!
echo  ========================================
echo.
echo  To start the server, run:  runserver.bat
echo.
pause
