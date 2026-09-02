@echo off
cd /d "%~dp0backend"
call ".venv\Scripts\activate.bat"
uvicorn app.main:app --reload --port 8000
