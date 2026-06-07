@echo off
echo Starting Django CRM installation...

echo Cloning the repository...
git clone https://github.com/OlegUhakov/CRM.git
cd CRM

echo Creating virtual environment...
python -m venv venv

echo Activating venv and upgrading pip...
cmd /c "venv\Scripts\activate && python -m pip install --upgrade pip"

echo Installing Python dependencies...
cmd /c "venv\Scripts\activate && python -m pip install -r requirements.txt"

echo Installing Node dependencies...
cmd /c "npm install"

echo Building Tailwind CSS styles...
cmd /c "npm run build"

echo Running database migrations...
cmd /c "venv\Scripts\activate && python manage.py migrate"

echo Creating superuser...
cmd /c "venv\Scripts\activate && python manage.py createsuperuser"

echo --------------------------------------------------
echo Installation completed successfully!
echo To start the server, run:
echo cd CRM
echo venv\Scripts\activate
echo python manage.py runserver
echo --------------------------------------------------
pause