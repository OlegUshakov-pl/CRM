@echo off
echo 🔄 Checking for CRM updates...

:: 1. Go into the project directory where Git is initialized
cd CRM

:: 2. Pull the latest changes anonymously
echo Pulling latest code from GitHub...
git clone --help >nul 2>&1
git pull origin main

:: 3. Update Python dependencies inside venv
echo 📥 Updating Python dependencies...
cmd /c "venv\Scripts\activate && python -m pip install -r requirements.txt"

:: 4. Rebuild Tailwind CSS
echo 🎨 Updating Frontend and rebuilding Tailwind...
cmd /c "npm install && npm run build"

:: 5. Run any new database migrations
echo 🗄️ Running new migrations...
cmd /c "venv\Scripts\activate && python manage.py migrate"

echo --------------------------------------------------
echo 🎉 CRM successfully updated to the latest version!
echo --------------------------------------------------
pause