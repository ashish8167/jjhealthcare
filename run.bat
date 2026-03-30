@echo off
title JJ Healthcare App

echo ===============================
echo   Starting JJ Healthcare App
echo ===============================

cd hospital_app

:: Activate virtual environment
call ...venv\Scripts\activate

:: Install dependencies (only first time, safe to keep)
pip install -r ..\requirements.txt

:: Run migrations
python manage.py migrate

:: Open browser
start http://127.0.0.1:8000

:: Run server
python manage.py runserver

pause
