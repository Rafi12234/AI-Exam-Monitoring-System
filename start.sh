#!/bin/bash
# Startup script for the entire application

echo "================================"
echo "Starting AI Exam Monitoring System"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js."
    exit 1
fi

# Start backend
echo "Starting Flask backend..."
cd backend
python3 app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
echo ""

echo "================================"
echo "Application started!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo "================================"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
