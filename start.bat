@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==============================================
echo   NGO Survey Management System - Start Script
echo ==============================================
echo.

REM ---------- Backend setup ----------
echo [1/4] Checking backend environment...
cd backend

if not exist ".venv" (
    echo   Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo   ERROR: Python was not found. Install Python 3.11+ and re-run this script.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo   No backend\.env found - copying from .env.example.
    echo   Edit backend\.env with your real DATABASE_URL and APP_SECRET_KEY before continuing.
    copy ".env.example" ".env" >nul
)

echo   Installing/updating backend dependencies...
call ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo   ERROR: pip install failed.
    pause
    exit /b 1
)

echo [2/4] Applying database migrations...
call ".venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 (
    echo   ERROR: Alembic migration failed. Check backend\.env DATABASE_URL.
    pause
    exit /b 1
)

echo   Seeding demo data (safe to skip if already seeded)...
call ".venv\Scripts\python.exe" -m app.seed

cd ..

REM ---------- Frontend setup ----------
echo [3/4] Checking frontend environment...
cd frontend

if not exist ".env.local" (
    echo   No frontend\.env.local found - copying from .env.local.example.
    copy ".env.local.example" ".env.local" >nul
)

if not exist "node_modules" (
    echo   Installing frontend dependencies, this may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo   ERROR: npm install failed. Ensure Node.js 18+ is installed.
        pause
        exit /b 1
    )
)

cd ..

REM ---------- Launch ----------
echo [4/4] Starting servers...
echo   Backend  -> http://localhost:8000  (docs at /docs)
echo   Frontend -> http://localhost:3000
echo.

start "NGO Backend (FastAPI)" "%~dp0run-backend.bat"
start "NGO Frontend (Next.js)" "%~dp0run-frontend.bat"

echo Both servers are launching in separate windows.
echo Close those windows (or Ctrl+C inside them) to stop the app.
pause
