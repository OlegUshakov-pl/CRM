@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo ========================================
echo     Starting Django Development Server
echo ========================================

:: Check venv exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Run install.bat first.
    pause
    exit /b 1
)

:: Run the server
venv\Scripts\python.exe manage.py runserver

pause
