@echo off
chcp 65001 >nul
echo ==================================================
echo     Django CRM — Installation
echo ==================================================
echo.

:: Detect if we're inside CRM folder
if exist "manage.py" (
    echo [*] Already inside CRM project folder.
    set "PROJECT_DIR=%CD%"
) else (
    if exist "CRM\manage.py" (
        echo [*] Found CRM subfolder, switching...
        cd CRM
        set "PROJECT_DIR=%CD%"
    ) else (
        echo [*] Cloning repository...
        git clone https://github.com/OlegUhakov/CRM.git
        if errorlevel 1 (
            echo [!] Git clone failed. Aborting.
            pause
            exit /b 1
        )
        cd CRM
        set "PROJECT_DIR=%CD%"
    )
)

echo [*] Project directory: %PROJECT_DIR%

:: Virtual environment
if exist "venv\Scripts\python.exe" (
    echo [*] Virtual environment already exists.
) else (
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [!] Failed to create venv. Aborting.
        pause
        exit /b 1
    )
)

set "PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"
set "PIP=%PROJECT_DIR%\venv\Scripts\pip.exe"

echo [*] Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip

echo [*] Installing Python dependencies...
"%PIP%" install -r requirements.txt
if errorlevel 1 (
    echo [!] pip install failed.
    pause
    exit /b 1
)

echo [*] Installing Node dependencies...
call npm install
if errorlevel 1 (
    echo [!] npm install failed.
    pause
    exit /b 1
)

echo [*] Building Tailwind CSS styles...
call npm run build
if errorlevel 1 (
    echo [!] Tailwind build failed.
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

echo [*] Creating superuser...
"%PYTHON%" manage.py createsuperuser

echo.
echo ==================================================
echo     Installation completed!
echo ==================================================
echo.
echo To start the development server:
echo     cd %PROJECT_DIR%
echo     venv\Scripts\activate
echo     python manage.py runserver
echo.
pause
