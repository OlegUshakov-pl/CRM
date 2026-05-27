@echo off
echo ========================================
echo     Starting Django Development Server
echo ========================================

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if activation was successful
if errorlevel 1 (
    echo Error: Could not activate virtual environment!
    pause
    exit /b 1
)

echo Virtual environment activated successfully.
echo Starting Django server...

:: Run the server
python manage.py runserver

pause
