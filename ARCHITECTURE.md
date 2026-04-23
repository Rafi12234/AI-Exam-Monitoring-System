# System Architecture

## Overview

The AI Exam Monitoring System consists of three main components:

1. **Backend API** - Flask server with real-time communication
2. **Frontend Dashboard** - React-based admin interface
3. **Computer Vision Pipeline** - YOLO + DeepSORT + MediaPipe

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   CCTV Camera   │────────▶│  CV Pipeline     │────────▶│  Flask Backend   │
│   / Webcam      │         │  + Detection     │         │  + Database      │
└─────────────────┘         │  + Tracking      │         └──────────────────┘
                             │  + Pose Est.     │                   ▲
                             └──────────────────┘                   │
                                                                    │
                                                              WebSocket
                                                                    │
                                                                    ▼
                                         ┌──────────────────────────────────┐
                                         │   React Dashboard (Frontend)     │
                                         │   + Real-time Updates            │
                                         │   + Admin Controls               │
                                         └──────────────────────────────────┘
```

## Component Details

### 1. Backend (Flask + Flask-SocketIO)

**Purpose**: API server and real-time communication hub

**Key Responsibilities**:
- Receive offense logs from CV pipeline
- Store data in SQLite database
- Flag students when threshold is reached (≥3 offenses)
- Emit real-time events via WebSocket
- Serve REST API endpoints

**Database**:
- `offenses`: Stores all detected offenses
- `flagged_students`: Stores flagged students and counts

**API Endpoints**:
```
GET    /api/flagged_students
GET    /api/students/<id>/offenses
POST   /api/log_offense
POST   /api/reset_student/<id>
POST   /api/clear_offenses/<id>
GET    /api/stats
GET    /health
```

**WebSocket Events**:
```
server → client:
  - student_flagged
  - student_reset
  - student_cleared

client → server:
  - request_flagged_students
```

### 2. Frontend (React + Socket.IO Client)

**Purpose**: Admin interface for monitoring and management

**Key Responsibilities**:
- Display flagged students
- Show real-time updates
- Provide admin controls (reset, clear)
- Manage application state with Context API

**Components**:
- `Dashboard.js`: Main interface
- `FlaggedStudentCard.js`: Individual student display
- `FlaggedStudentsContext.js`: Global state management

**Features**:
- Real-time updates via WebSocket
- Statistics display
- Responsive design
- Error handling

### 3. Computer Vision Pipeline

**Purpose**: Analyze video feed and detect unethical behavior

**Components**:

#### Person Detection (detector.py)
- Uses YOLOv5 pre-trained model
- Detects persons in each frame
- Returns bounding boxes with confidence

#### Tracking (tracker.py)
- Implements DeepSORT algorithm
- Assigns unique IDs to detected persons
- Maintains identity across frames
- Handles person entry/exit

#### Head Pose Estimation (head_pose.py)
- Uses MediaPipe Face Mesh
- Estimates head orientation
- Classifies poses: forward, back, left, right
- Detects unethical behavior

#### Main Pipeline (cv_pipeline.py)
- Orchestrates all components
- Processes video frame by frame
- Logs offenses to backend
- Implements cooldown to prevent spam

## Data Flow

### Offense Detection Flow
```
1. CV Pipeline reads frame from camera
   ↓
2. YOLOv5 detects persons (bounding boxes)
   ↓
3. DeepSORT tracks persons (assigns IDs)
   ↓
4. MediaPipe estimates head pose for each person
   ↓
5. Check if pose indicates unethical behavior
   ↓
6. If yes, POST /api/log_offense to backend
   ↓
7. Backend increments offense counter
   ↓
8. If counter >= 3:
   - Flag student in database
   - Emit 'student_flagged' event via WebSocket
   ↓
9. Frontend receives event and updates UI
```

### Real-time Update Flow
```
Backend detects flag
   ↓
Emits 'student_flagged' event
   ↓
All connected clients receive event
   ↓
Frontend updates FlaggedStudentsContext
   ↓
Components re-render with new data
   ↓
Dashboard displays updated list
```

## Technology Stack Details

### Backend
```
Flask (Web Framework)
├── Flask-CORS (Cross-origin support)
├── Flask-SocketIO (Real-time communication)
└── SQLite3 (Database)
```

### Frontend
```
React (UI Framework)
├── React Router (Navigation)
├── Socket.IO Client (Real-time updates)
├── Axios (HTTP requests)
└── CSS3 (Styling)
```

### Computer Vision
```
PyTorch (Deep learning framework)
├── YOLOv5 (Object detection)
├── DeepSORT (Tracking)
├── MediaPipe (Pose estimation)
└── OpenCV (Video processing)
```

## Database Schema

### offenses table
```sql
CREATE TABLE offenses (
  id INTEGER PRIMARY KEY,
  student_id TEXT NOT NULL,
  behavior_type TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**behavior_type values**: 'back', 'left', 'right', 'talking', 'unethical'

### flagged_students table
```sql
CREATE TABLE flagged_students (
  student_id TEXT PRIMARY KEY,
  offenses_count INTEGER DEFAULT 0,
  flagged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'active'
)
```

**status values**: 'active', 'inactive', 'cleared'

## Performance Considerations

### CV Pipeline
- Frame processing: ~30-50ms per frame (depends on resolution)
- Detection accuracy: ~95% (YOLO)
- Tracking reliability: ~90% (DeepSORT)
- Pose estimation: ~20ms per person

### Backend
- API response time: <100ms
- WebSocket latency: <50ms
- Database query time: <10ms

### Frontend
- Initial load: ~2-3 seconds
- Real-time update latency: <100ms
- Smooth 60 FPS rendering

## Scalability

### Current Limitations
- Single video feed
- Single backend instance
- In-memory tracking state

### Scaling Strategies
1. **Multiple Cameras**: Distribute processing across multiple CV pipelines
2. **Load Balancing**: Use Nginx to balance backend requests
3. **Database Optimization**: Add indexes on student_id
4. **Caching**: Redis for frequently accessed data
5. **Message Queue**: RabbitMQ/Kafka for decoupled processing

## Security Considerations

### Current Security Level
- Local network only
- No authentication
- No encryption

### Production Improvements Needed
1. HTTPS/TLS for all communications
2. JWT authentication for admin users
3. Rate limiting on API endpoints
4. Input validation and sanitization
5. Database encryption
6. Access control and logging
7. Regular security audits

## Deployment Considerations

### Development
- Runs on localhost
- File-based SQLite database
- Real-time development with hot reload

### Production
- Use external database (PostgreSQL/MySQL)
- Deploy with Gunicorn/uWSGI
- Use Nginx as reverse proxy
- Enable HTTPS/TLS
- Implement authentication
- Set up monitoring and logging
- Use Docker containers

## Integration Points

### External Systems
- CCTV Management System
- Student Information System (SIS)
- Exam Hall Management System
- Alert/Notification System

### API Integration Example
```python
# Get flagged students and send to SIS
flagged = requests.get('http://localhost:5000/api/flagged_students')
for student in flagged.json()['data']:
    # Send to SIS for recording
    sis_client.flag_student(student['student_id'])
```

## Troubleshooting Guide

### High False Positive Rate
- Adjust YOLO confidence threshold
- Retrain with more specific data
- Adjust head pose detection thresholds

### Tracking Loss
- Increase max_age in DeepSORT tracker
- Adjust IoU threshold
- Use better camera positioning

### Performance Issues
- Reduce video resolution
- Use GPU acceleration
- Optimize database queries

## Future Enhancements

1. Face recognition for student identification
2. Multi-person conversation detection
3. Phone/device usage detection
4. Writing elsewhere detection
5. Advanced behavior analytics
6. Machine learning model optimization
7. Mobile app for admins
8. Automated reporting
9. Alert notifications
10. Video evidence storage

---

For more details, see README.md and QUICKSTART.md
