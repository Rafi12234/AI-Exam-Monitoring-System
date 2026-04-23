@echo off
REM Quick setup script for Windows

echo ================================
echo Setting up AI Exam Monitoring System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

REM Setup backend
echo.
echo Setting up backend...
cd backend
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo Backend setup complete!
cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend
if not exist "node_modules" (
    call npm install
    echo Frontend dependencies installed
)
echo Frontend setup complete!
cd ..

echo.
echo ================================
echo Setup complete!
echo ================================
echo.
echo Next steps:
echo 1. Run 'start.bat' to start the application
echo 2. Or manually start:
echo    - Backend: cd backend && python app.py
echo    - Frontend: cd frontend && npm start
echo.

pause
