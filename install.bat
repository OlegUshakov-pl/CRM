@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title CRM - Installation

echo.
echo ========================================
echo         CRM - Installation
echo ========================================
echo.
echo Current directory: !CD!
echo.

:: Step 1: Find project folder with manage.py
set "PROJECT_DIR=!CD!"

if exist "!PROJECT_DIR!\manage.py" (
    echo  [OK] Already inside CRM project folder.
    goto deps
)

if exist "!PROJECT_DIR!\CRM\manage.py" (
    echo  [OK] Found CRM subfolder.
    set "PROJECT_DIR=!PROJECT_DIR!\CRM"
    cd /d "!PROJECT_DIR!"
    goto deps
)

:: Try to clone
echo  [*] Cloning repository...
git clone https://github.com/OlegUshakov-pl/CRM.git
if !errorlevel! neq 0 (
    echo  [ERROR] Git clone failed. Make sure Git is installed.
    echo  Try deleting the CRM folder and running again.
    pause
    exit /b 1
)

if exist "!CD!\CRM\manage.py" (
    set "PROJECT_DIR=!CD!\CRM"
    cd /d "!PROJECT_DIR!"
) else (
    echo  [ERROR] Cloned repository does not contain manage.py
    pause
    exit /b 1
)

:deps
echo  [DIR] !PROJECT_DIR!
echo.

:: Step 2: Check Python
where python >nul 2>&1
if !errorlevel! neq 0 (
    echo  [ERROR] Python not found.
    echo  Install Python 3.10+ from https://python.org and add to PATH.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  [OK] Python !PY_VER!

:: Step 3: Check Node.js
where node >nul 2>&1
if !errorlevel! neq 0 (
    echo  [ERROR] Node.js not found.
    echo  Install Node.js 20+ from https://nodejs.org and add to PATH.
    pause
    exit /b 1
)
echo  [OK] Node.js found.
echo.

:: Step 4: Create virtual environment
if exist "!PROJECT_DIR!\venv\Scripts\python.exe" (
    echo  [OK] Virtual environment already exists.
) else (
    echo  [*] Creating virtual environment...
    python -m venv "!PROJECT_DIR!\venv"
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)

set "PYTHON=!PROJECT_DIR!\venv\Scripts\python.exe"
set "PIP=!PROJECT_DIR!\venv\Scripts\pip.exe"
echo.

:: Step 5: Install Python dependencies
echo  [*] Upgrading pip...
"!PYTHON!" -m pip install --upgrade pip >nul 2>&1

echo  [*] Installing Python dependencies...
"!PIP!" install -r "!PROJECT_DIR!\requirements.txt"
if !errorlevel! neq 0 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)
echo  [OK] Python dependencies installed.
echo.

:: Step 6: Install Node dependencies
cd /d "!PROJECT_DIR!"
echo  [*] Installing Node dependencies...
call npm install
if !errorlevel! neq 0 (
    echo  [ERROR] npm install failed.
    pause
    exit /b 1
)
echo  [OK] Node dependencies installed.
echo.

:: Step 7: Build Tailwind CSS
echo  [*] Building Tailwind CSS...
call npm run build
if !errorlevel! neq 0 (
    echo  [ERROR] Tailwind build failed.
    pause
    exit /b 1
)
echo  [OK] Tailwind CSS built.
echo.

:: Step 8: Database migrations
echo  [*] Running database migrations...
"!PYTHON!" "!PROJECT_DIR!\manage.py" migrate
if !errorlevel! neq 0 (
    echo  [ERROR] Migrations failed.
    pause
    exit /b 1
)
echo  [OK] Database migrated.
echo.

:: Step 9: Seed AI providers
echo  [*] Seeding AI providers...
"!PYTHON!" "!PROJECT_DIR!\manage.py" seed_ai_providers
if !errorlevel! neq 0 (
    echo  [ERROR] AI providers seeding failed.
    pause
    exit /b 1
)
echo  [OK] AI providers seeded.
echo.

:: Step 10: Collect static files
echo  [*] Collecting static files...
"!PYTHON!" "!PROJECT_DIR!\manage.py" collectstatic --noinput
if !errorlevel! neq 0 (
    echo  [ERROR] collectstatic failed.
    pause
    exit /b 1
)
echo  [OK] Static files collected.
echo.

:: Step 11: Create superuser and set password
echo  [*] Creating superuser...
"!PYTHON!" "!PROJECT_DIR!\manage.py" createsuperuser --noinput --username admin --email admin@example.com 2>nul

echo  [*] Setting password to "admin"...
"!PYTHON!" "!PROJECT_DIR!\manage.py" shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='admin'); u.set_password('admin'); u.save()" >nul 2>&1
echo  [OK] Superuser created (username: admin, password: admin)
echo.

echo.
echo ========================================
echo       Installation completed!
echo ========================================
echo.
echo  To start the server, run:  runserver.bat
echo.
pause
