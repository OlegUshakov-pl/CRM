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

:: Step 2: Find proper Python (skip Inkscape/minimal Pythons)
set "PYTHON_EXE="

:: Try py launcher first (most reliable)
where py >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%p in ('py -3 --version 2^>^&1') do set "PY_CHECK=%%p"
    echo !PY_CHECK! | findstr /r "Python 3\." >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py -3"
    )
)

:: Fallback: search PATH for python with pip support
if not defined PYTHON_EXE (
    for /f "tokens=*" %%p in ('where python 2^>nul') do (
        if not defined PYTHON_EXE (
            "%%p" -m pip --version >nul 2>&1
            if !errorlevel! equ 0 (
                set "PYTHON_EXE=%%p"
            )
        )
    )
)

:: Fallback: try python3
if not defined PYTHON_EXE (
    where python3 >nul 2>&1
    if !errorlevel! equ 0 (
        python3 -m pip --version >nul 2>&1
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=python3"
        )
    )
)

if not defined PYTHON_EXE (
    echo  [ERROR] Python 3.10+ with pip not found.
    echo  Install Python from https://python.org and make sure to check
    echo  "Add Python to PATH" during installation.
    echo.
    echo  If you have multiple Python versions, uninstall the old one or
    echo  make sure the Python.org version comes first in PATH.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('!PYTHON_EXE! --version 2^>^&1') do set "PY_VER=%%v"
echo  [OK] Python !PY_VER! ^(!PYTHON_EXE!^)
echo.

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
    !PYTHON_EXE! -m venv "!PROJECT_DIR!\venv"
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)

set "PYTHON=!PROJECT_DIR!\venv\Scripts\python.exe"
echo.

:: Step 5: Ensure pip is available in venv
"!PYTHON!" -m pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo  [*] pip not found in venv, installing via ensurepip...
    "!PYTHON!" -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to install pip.
        pause
        exit /b 1
    )
    echo  [OK] pip installed.
)

:: Step 6: Install Python dependencies
echo  [*] Upgrading pip...
"!PYTHON!" -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo  [WARNING] pip upgrade failed, continuing...
)

echo  [*] Installing Python dependencies...
"!PYTHON!" -m pip install -r "!PROJECT_DIR!\requirements.txt"
if !errorlevel! neq 0 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)
echo  [OK] Python dependencies installed.
echo.

:: Step 7: Install Node dependencies
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

:: Step 8: Build Tailwind CSS
echo  [*] Building Tailwind CSS...
call npm run build
if !errorlevel! neq 0 (
    echo  [ERROR] Tailwind build failed.
    pause
    exit /b 1
)
echo  [OK] Tailwind CSS built.
echo.

:: Step 9: Create local configuration (.env)
if exist "!PROJECT_DIR!\.env" (
    echo  [OK] .env already exists, keeping current configuration.
) else (
    echo  [*] Generating .env with a random SECRET_KEY...
    "!PYTHON!" -c "import sys,pathlib;from django.core.management.utils import get_random_secret_key as g;p=pathlib.Path(sys.argv[1]);p.write_text('DJANGO_SECRET_KEY='+g()+'\n# Optional settings, see README.md section Configuration and Security\n# DEBUG=False\n# ALLOWED_HOSTS=localhost,127.0.0.1\n# SECURE_COOKIES=True when using HTTPS\n',encoding='utf-8')" "!PROJECT_DIR!\.env"
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to create .env
        pause
        exit /b 1
    )
    echo  [OK] .env created with a generated SECRET_KEY.
    echo        See README.md, section Configuration and Security.
)
echo.

:: Step 10: Database migrations
echo  [*] Running database migrations...
"!PYTHON!" "!PROJECT_DIR!\manage.py" migrate
if !errorlevel! neq 0 (
    echo  [ERROR] Migrations failed.
    pause
    exit /b 1
)
echo  [OK] Database migrated.
echo.

:: Step 11: Seed AI providers
echo  [*] Seeding AI providers...
"!PYTHON!" "!PROJECT_DIR!\manage.py" seed_ai_providers
if !errorlevel! neq 0 (
    echo  [ERROR] AI providers seeding failed.
    pause
    exit /b 1
)
echo  [OK] AI providers seeded.
echo.

:: Step 12: Collect static files
echo  [*] Collecting static files...
"!PYTHON!" "!PROJECT_DIR!\manage.py" collectstatic --noinput
if !errorlevel! neq 0 (
    echo  [ERROR] collectstatic failed.
    pause
    exit /b 1
)
echo  [OK] Static files collected.
echo.

:: Step 13: Create superuser
echo  [*] Creating superuser account...
set "SU_USERNAME=admin"
set /p "SU_USERNAME=Username [admin]: "
if "!SU_USERNAME!"=="" set "SU_USERNAME=admin"

set "SU_PASSWORD="
set /p "SU_PASSWORD=Password, leave empty to generate a strong one: "

set "PASSWORD_GENERATED=0"
if "!SU_PASSWORD!"=="" (
    set "CRM_PW_FILE=%TEMP%\crm_generated_password.txt"
    "!PYTHON!" -c "import os,secrets,pathlib; pathlib.Path(os.environ['CRM_PW_FILE']).write_text(secrets.token_urlsafe(16))"
    set /p SU_PASSWORD=<"!CRM_PW_FILE!"
    del /q "!CRM_PW_FILE!" >nul 2>&1
    set "PASSWORD_GENERATED=1"
)
if "!SU_PASSWORD!"=="" (
    echo  [ERROR] Failed to generate a password
    pause
    exit /b 1
)

set "CRM_SU_USERNAME=!SU_USERNAME!"
set "CRM_SU_PASSWORD=!SU_PASSWORD!"

"!PYTHON!" "!PROJECT_DIR!\manage.py" shell -v 0 -c "import os,sys; from django.contrib.auth import get_user_model; sys.exit(0 if get_user_model().objects.filter(username=os.environ['CRM_SU_USERNAME']).exists() else 1)"
set "SU_ERR=!errorlevel!"

if "!SU_ERR!"=="0" (
    echo  [*] User "!SU_USERNAME!" already exists, setting a new password...
    "!PYTHON!" "!PROJECT_DIR!\manage.py" shell -v 0 -c "import os; from django.contrib.auth import get_user_model; u=get_user_model().objects.get(username=os.environ['CRM_SU_USERNAME']); u.set_password(os.environ['CRM_SU_PASSWORD']); u.save()"
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to set password for "!SU_USERNAME!"
        pause
        exit /b 1
    )
) else (
    echo  [*] Creating user "!SU_USERNAME!"...
    set "DJANGO_SUPERUSER_PASSWORD=!SU_PASSWORD!"
    "!PYTHON!" "!PROJECT_DIR!\manage.py" createsuperuser --noinput --username "!SU_USERNAME!" --email "!SU_USERNAME!@localhost"
    set "SU_ERR=!errorlevel!"
    set "DJANGO_SUPERUSER_PASSWORD="
    if !SU_ERR! neq 0 (
        echo  [ERROR] Failed to create superuser
        pause
        exit /b 1
    )
)
set "CRM_SU_USERNAME="
set "CRM_SU_PASSWORD="
echo  [OK] Superuser ready: !SU_USERNAME!
echo.

echo.
echo ========================================
echo       Installation completed!
echo ========================================
echo.
echo  Superuser: !SU_USERNAME!
if "!PASSWORD_GENERATED!"=="1" (
    echo  Password:  !SU_PASSWORD!
    echo             ^>^> Save it now, it is shown only once ^<^<
) else (
    echo  Password:  the one you entered above.
)
echo.
echo  Security checklist:
echo    - Change the superuser password after first login.
echo    - Configuration lives in .env: SECRET_KEY is generated,
echo      DEBUG defaults to False, ALLOWED_HOSTS for LAN access.
echo    - runserver.bat starts a development server bound to
echo      127.0.0.1. Do not expose it beyond this machine:
echo      deploy behind a real WSGI server with DEBUG=False.
echo.
echo  To start the server, run:  runserver.bat
echo.
pause
