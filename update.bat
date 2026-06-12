@echo off
title CRM - Update

echo.
echo ========================================
echo           CRM - Update
echo ========================================
echo.

:: Detect project folder
if exist "manage.py" (
    set "PROJECT_DIR=%CD%"
) else if exist "CRM\manage.py" (
    cd CRM
    set "PROJECT_DIR=%CD%"
) else (
    echo  [ERROR] manage.py not found.
    pause
    exit /b 1
)

set "PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"

:: Check venv
if not exist "%PYTHON%" (
    echo  [ERROR] Virtual environment not found.
    echo  Run install.bat first.
    pause
    exit /b 1
)

:: Check git
where git >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found.
    pause
    exit /b 1
)

:: Pull latest code
echo  [1/6] Pulling latest code...
git pull origin main
if errorlevel 1 (
    echo  [ERROR] Git pull failed.
    pause
    exit /b 1
)
echo  [OK] Code updated.

:: Update Python dependencies
echo  [2/6] Updating Python dependencies...
"%PYTHON%" -m pip install -r requirements.txt --upgrade -q
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)
echo  [OK] Python dependencies updated.

:: Update Node dependencies
echo  [3/6] Updating Node dependencies...
call npm install --silent
if errorlevel 1 (
    echo  [ERROR] npm install failed.
    pause
    exit /b 1
)
echo  [OK] Node dependencies updated.

:: Rebuild Tailwind CSS
echo  [4/6] Rebuilding Tailwind CSS...
call npm run build
if errorlevel 1 (
    echo  [ERROR] Tailwind build failed.
    pause
    exit /b 1
)
echo  [OK] Tailwind CSS rebuilt.

:: Run database migrations
echo  [5/6] Running database migrations...
"%PYTHON%" manage.py migrate
if errorlevel 1 (
    echo  [ERROR] Migrations failed.
    pause
    exit /b 1
)
echo  [OK] Database migrated.

:: Collect static files
echo  [6/6] Collecting static files...
"%PYTHON%" manage.py collectstatic --noinput
if errorlevel 1 (
    echo  [ERROR] collectstatic failed.
    pause
    exit /b 1
)
echo  [OK] Static files collected.

echo.
echo ========================================
echo         Update completed!
echo ========================================
echo.
echo  To start the server, run:  runserver.bat
echo.
pause
