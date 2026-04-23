# AI Exam Center Monitoring System

A comprehensive AI-powered exam center monitoring system that detects unethical behavior using CCTV cameras with real-time dashboard updates.

## Features

- ✅ Real-time person detection using YOLOv5
- ✅ Student tracking with unique IDs using DeepSORT
- ✅ Head pose estimation using MediaPipe
- ✅ Unethical behavior detection (head turning, talking)
- ✅ Offense logging in SQLite database
- ✅ Admin dashboard built with React
- ✅ Real-time updates using WebSocket (Socket.IO)
- ✅ RESTful API backend with Flask

## Project Structure

```
ai-exam-monitoring-system/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── database.db            # SQLite database
│   └── vision/
│       ├── detector.py        # YOLO person detector
│       ├── tracker.py         # DeepSORT tracker
│       ├── head_pose.py       # MediaPipe head pose estimator
│       └── cv_pipeline.py     # Main CV pipeline
│
└── frontend/
    ├── package.json           # React dependencies
    ├── public/
    │   └── index.html         # HTML template
    └── src/
        ├── App.js             # Main App component
        ├── index.js           # React entry point
        ├── components/
        │   ├── Dashboard.js   # Main dashboard
        │   └── FlaggedStudentCard.js
        ├── context/
        │   └── FlaggedStudentsContext.js
        ├── utils/
        │   ├── socket.js      # Socket.IO client
        │   └── api.js         # API client
        └── pages/             # Additional pages
```

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### 1. Start Backend Server

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`

### 2. Start CV Pipeline

In another terminal:

```bash
cd backend/vision
python cv_pipeline.py
```

### 3. Start Frontend

In another terminal:

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## API Endpoints

- `GET /api/flagged_students` - Get all flagged students
- `GET /api/students/<student_id>/offenses` - Get offenses for a student
- `POST /api/log_offense` - Log a new offense
- `POST /api/reset_student/<student_id>` - Reset a student
- `POST /api/clear_offenses/<student_id>` - Clear offenses for a student
- `GET /api/stats` - Get system statistics
- `GET /health` - Health check

## WebSocket Events

- `student_flagged` - Emitted when a student is flagged
- `student_reset` - Emitted when a student is reset
- `student_cleared` - Emitted when a student's offenses are cleared

## Technology Stack

### Frontend
- React 18
- React Router v6
- Socket.IO Client
- Axios
- CSS3

### Backend
- Flask
- Flask-SocketIO
- SQLite
- YOLOv5
- MediaPipe
- DeepSORT

## Configuration

### Backend Configuration (app.py)
- Database path: `database.db`
- Server host: `0.0.0.0`
- Server port: `5000`
- Debug mode: `True`

### Frontend Configuration (utils/socket.js)
- Backend URL: `http://localhost:5000`
- Reconnection attempts: 5
- Reconnection delay: 1000ms

### CV Pipeline Configuration (vision/cv_pipeline.py)
- Backend URL: `http://localhost:5000`
- Video source: `0` (webcam)
- Offense cooldown: 30 frames

## Database Schema

### offenses table
```sql
CREATE TABLE offenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT NOT NULL,
  behavior_type TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### flagged_students table
```sql
CREATE TABLE flagged_students (
  student_id TEXT PRIMARY KEY,
  offenses_count INTEGER DEFAULT 0,
  flagged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'active'
)
```

## How It Works

1. **Person Detection**: YOLOv5 detects people in each frame
2. **Tracking**: DeepSORT assigns unique IDs to detected persons
3. **Pose Estimation**: MediaPipe estimates head poses
4. **Behavior Detection**: System checks for unethical behaviors (head turning, looking back)
5. **Offense Logging**: Offenses are logged in the database
6. **Flagging**: Students with 3+ offenses are flagged
7. **Real-time Updates**: WebSocket notifies the frontend of new flags
8. **Dashboard**: React dashboard displays flagged students in real-time

## Features in Detail

### Admin Dashboard
- Real-time display of flagged students
- Offense count per student
- Statistics (total flagged, students with offenses, total offenses)
- View offense details
- Reset or clear student records
- Real-time updates without page refresh

### Unethical Behavior Detection
- Head turning (left/right): More than 10% horizontal angle difference
- Looking back: Head angle < -15 degrees on vertical axis
- Multiple offenses tracked per student

### Real-time Communication
- Socket.IO establishes persistent connection
- Backend emits events for new flags, resets, and clears
- Frontend updates UI immediately without polling

## Troubleshooting

### Backend Connection Issues
- Ensure Flask server is running on `http://localhost:5000`
- Check CORS configuration in `app.py`
- Verify Socket.IO is properly initialized

### Frontend Connection Issues
- Check browser console for Socket.IO connection errors
- Verify backend URL in `utils/socket.js`
- Clear browser cache and restart

### CV Pipeline Issues
- Ensure camera is connected and accessible
- Check YOLOv5 model download
- Verify backend is running before starting pipeline

## Future Enhancements

- [ ] Multiple camera support
- [ ] Advanced behavior detection (writing elsewhere, using phone)
- [ ] Student identification with face recognition
- [ ] Exam session management
- [ ] Report generation
- [ ] Mobile app for admins
- [ ] Alert notifications
- [ ] Video recording and playback

## License

MIT License

## Support

For issues and questions, please refer to the documentation or create an issue in the repository.
