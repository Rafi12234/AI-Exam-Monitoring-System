@echo off
REM Startup script for Windows

echo ================================
echo Starting AI Exam Monitoring System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js.
    pause
    exit /b 1
)

REM Start backend
echo Starting Flask backend...
cd backend
start cmd /k python app.py
echo Backend started
echo.

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo Starting React frontend...
cd ..\frontend
start cmd /k npm start
echo Frontend started
echo.

echo ================================
echo Application started!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5000
echo ================================
echo.

pause
