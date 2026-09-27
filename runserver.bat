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

:: Development server only: enable DEBUG for this process unless
:: the environment (.env or system) explicitly defines it.
if not defined DEBUG set "DEBUG=true"

echo.
echo  [!] Development server, bound to 127.0.0.1 only.
echo  [!] Do not expose it to the network. For production set
echo  [!] DEBUG=False in .env and run behind a WSGI server.
echo.

:: Run the server
venv\Scripts\python.exe manage.py runserver

pause
