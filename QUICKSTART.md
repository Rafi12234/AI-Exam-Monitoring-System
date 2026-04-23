# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Webcam or video feed (for CV pipeline)
- Git (optional)

## Installation Steps

### Windows Users

1. **Clone or Download the Project**
   ```bash
   cd path/to/ai-exam-monitoring-system
   ```

2. **Run Setup Script**
   ```bash
   setup.bat
   ```
   This will:
   - Create virtual environment for Python
   - Install Python dependencies
   - Install Node.js dependencies

3. **Start the Application**
   ```bash
   start.bat
   ```
   This will automatically start:
   - Backend server on `http://localhost:5000`
   - Frontend on `http://localhost:3000`

### Linux/Mac Users

1. **Clone or Download the Project**
   ```bash
   cd path/to/ai-exam-monitoring-system
   ```

2. **Make scripts executable**
   ```bash
   chmod +x setup.sh start.sh
   ```

3. **Run Setup Script**
   ```bash
   ./setup.sh
   ```

4. **Start the Application**
   ```bash
   ./start.sh
   ```

## Manual Setup (All Platforms)

### Backend Setup

```bash
cd backend

# Create virtual environment (Optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python app.py
```

### Frontend Setup (In another terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### CV Pipeline (In another terminal, optional)

```bash
cd backend/vision

# Run the CV pipeline
python cv_pipeline.py
```

## Testing Without CV Pipeline

To test the dashboard without running the CV pipeline:

1. Use the mock backend:
   ```bash
   cd backend
   python app_mock.py
   ```

2. Then start the frontend:
   ```bash
   cd frontend
   npm start
   ```

The mock backend simulates student flags and offenses for testing.

## Accessing the Application

Once everything is running:

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## First Time Usage

1. Open the dashboard at `http://localhost:3000`
2. You should see statistics at the top
3. If using the mock backend, you'll see flagged students
4. Click "Show Details" on any student card to see their offenses
5. Use buttons to:
   - **Reset**: Mark student as not flagged
   - **Clear**: Delete all offenses for the student

## Integrating the CV Pipeline

1. Update the CCTV camera or video feed in `backend/vision/cv_pipeline.py`:
   ```python
   pipeline = CVPipeline(
       backend_url='http://localhost:5000',
       video_source=0  # Change to camera index or file path
   )
   ```

2. Adjust head pose estimation parameters if needed

3. Run the CV pipeline:
   ```bash
   python backend/vision/cv_pipeline.py
   ```

## Troubleshooting

### Backend Connection Error
- Ensure backend is running: `python backend/app.py`
- Check if port 5000 is available
- Verify firewall settings

### Frontend Won't Load
- Check if Node.js is installed: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### CV Pipeline Not Connecting
- Verify backend URL in `cv_pipeline.py`
- Check network connectivity
- Ensure backend is running before starting CV pipeline

### Camera/Video Issues
- Check camera permissions
- Verify camera index (0 for default webcam)
- Try different video source

## Configuration

Edit these files to customize:

### Backend Configuration
- **Database**: `backend/database.db`
- **Server**: Change host/port in `backend/app.py` (line: `socketio.run(app, host='...', port=...)`)
- **Model**: Change YOLO model in `backend/vision/detector.py`

### Frontend Configuration
- **Backend URL**: Edit `frontend/src/utils/socket.js` and `frontend/src/utils/api.js`
- **Styles**: Modify CSS in `frontend/src/components/*.css`

### CV Pipeline Configuration
- **Backend URL**: `backend/vision/cv_pipeline.py` (line: `backend_url=...`)
- **Video Source**: `backend/vision/cv_pipeline.py` (line: `video_source=...`)
- **Offense Cooldown**: Adjust `cooldown_frames` parameter

## Next Steps

1. ✅ Customize the system for your exam center
2. ✅ Integrate with your camera systems
3. ✅ Adjust behavior detection parameters
4. ✅ Set up database backups
5. ✅ Deploy to production

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the code comments
3. Check console output for error messages
4. Verify all services are running

## Performance Tips

- Close unnecessary applications to free up resources
- Use GPU if available (set `device='cuda'` in detector.py)
- Reduce video resolution for faster processing
- Adjust YOLO confidence threshold if getting too many detections

Enjoy using the AI Exam Monitoring System! 🚀
