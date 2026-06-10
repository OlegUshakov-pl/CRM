@echo off
chcp 65001 >nul
title CRM — Update

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║        CRM — Update                         ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: ──────────────────────────────────────────────
::  1. Detect project folder
:: ──────────────────────────────────────────────
if exist "manage.py" (
    set "PROJECT_DIR=%CD%"
) else if exist "CRM\manage.py" (
    cd CRM
    set "PROJECT_DIR=%CD%"
) else (
    echo  [ERROR] manage.py not found.
    echo  Run this script from the CRM folder.
    pause
    exit /b 1
)

set "PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"

:: ──────────────────────────────────────────────
::  2. Check venv
:: ──────────────────────────────────────────────
if not exist "%PYTHON%" (
    echo  [ERROR] Virtual environment not found.
    echo  Run install.bat first.
    pause
    exit /b 1
)

:: ──────────────────────────────────────────────
::  3. Check git
:: ──────────────────────────────────────────────
where git >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found.
    pause
    exit /b 1
)

:: ──────────────────────────────────────────────
::  4. Pull latest code
:: ──────────────────────────────────────────────
echo  [*] Pulling latest code...
git pull origin main
if errorlevel 1 (
    echo  [ERROR] Git pull failed.
    pause
    exit /b 1
)
echo  [OK] Code updated.
echo.

:: ──────────────────────────────────────────────
::  5. Update Python dependencies
:: ──────────────────────────────────────────────
echo  [*] Updating Python dependencies...
"%PYTHON%" -m pip install -r requirements.txt --upgrade -q
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)
echo  [OK] Python dependencies updated.
echo.

:: ──────────────────────────────────────────────
::  6. Update Node dependencies
:: ──────────────────────────────────────────────
echo  [*] Updating Node dependencies...
call npm install --silent
if errorlevel 1 (
    echo  [ERROR] npm install failed.
    pause
    exit /b 1
)
echo  [OK] Node dependencies updated.
echo.

:: ──────────────────────────────────────────────
::  7. Rebuild Tailwind CSS
:: ──────────────────────────────────────────────
echo  [*] Rebuilding Tailwind CSS...
call npm run build
if errorlevel 1 (
    echo  [ERROR] Tailwind build failed.
    pause
    exit /b 1
)
echo  [OK] Tailwind CSS rebuilt.
echo.

:: ──────────────────────────────────────────────
::  8. Run database migrations
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
::  Done
:: ──────────────────────────────────────────────
echo  ╔══════════════════════════════════════════════╗
echo  ║        Update completed!                     ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  To start the server, run:  runserver.bat
echo.
pause
