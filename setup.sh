#!/bin/bash
# Quick setup script

echo "================================"
echo "Setting up AI Exam Monitoring System"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

# Setup backend
echo ""
echo "Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
fi
source venv/bin/activate
pip install -r requirements.txt
echo "Backend setup complete!"
cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "Frontend dependencies installed"
fi
echo "Frontend setup complete!"
cd ..

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Run './start.sh' to start the application"
echo "2. Or manually start:"
echo "   - Backend: cd backend && python app.py"
echo "   - Frontend: cd frontend && npm start"
echo ""
