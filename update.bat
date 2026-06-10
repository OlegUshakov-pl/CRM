@echo off
chcp 65001 >nul
echo ==================================================
echo     CRM — Update
echo ==================================================
echo.

:: Auto-detect project folder
if exist "manage.py" (
    set "PROJECT_DIR=%CD%"
) else if exist "CRM\manage.py" (
    cd CRM
    set "PROJECT_DIR=%CD%"
) else (
    echo [!] manage.py not found. Run this script from the CRM folder.
    pause
    exit /b 1
)

set "PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"

echo [*] Pulling latest code from GitHub...
git pull origin main
if errorlevel 1 (
    echo [!] Git pull failed.
    pause
    exit /b 1
)

echo [*] Running database migrations...
"%PYTHON%" manage.py migrate
if errorlevel 1 (
    echo [!] Migrations failed.
    pause
    exit /b 1
)

echo [*] Rebuilding Tailwind CSS...
call npm run build

echo.
echo ==================================================
echo     Update completed!
echo ==================================================
pause
