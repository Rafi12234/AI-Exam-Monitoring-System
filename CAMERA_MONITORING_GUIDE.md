# Camera Monitoring System Guide

## Overview
The Admin can now access the Camera Monitoring feature to observe live student behavior in real-time. The system detects unethical behavior (head turning) and automatically logs offenses.

## Features

### 1. **Live Camera View** 📹
- Access the camera feed from your webcam
- See real-time visualization of detected students
- Visual indicators for different head poses:
  - **GREEN**: Forward/Ethical behavior ✅
  - **YELLOW**: Head turned left or right (Warning) ⚠️
  - **RED**: Head turned back (Critical) 🚨

### 2. **Automatic Offense Detection** 🎯
- Detects when student's head is turned:
  - **LEFT**: Left turn for 3+ seconds
  - **RIGHT**: Right turn for 3+ seconds
  - **BACK**: Looking backward (facing away from exam)
- Each detection creates an offense log
- Students with 3+ offenses are flagged as suspicious

### 3. **Real-Time Tracking** ⏱️
- Duration display for each unethical pose
- Continuous monitoring of student behavior
- Synchronized dashboard updates

## How to Use

### Starting the Camera Monitor

1. **Navigate to Camera View**
   - Click the "📹 Camera Monitor" button in the navigation bar
   - Or go to `http://localhost:3001/camera`

2. **Start the Camera**
   - Click the "▶ Start Camera" button
   - Grant camera permissions when prompted
   - You should see the live webcam feed

3. **Enable Head Pose Detection**
   - Click the "🎯 Start Detection" button
   - The system will:
     - Detect persons in the frame
     - Assign unique IDs to each person
     - Analyze head pose (forward, left, right, back)
     - Track duration of unethical poses
     - Log offenses when threshold is exceeded

### Monitoring Offenses

**Detection Thresholds:**
- ⚠️ **Warning State**: Head turned for 1-3 seconds (displayed in yellow)
- 🚨 **Offense Logged**: Head turned for 3+ seconds continuously
- 📊 **Auto-Flagged**: Student with 3+ total offenses

**Real-Time Information Displayed:**
- **Active Detections**: Number of students currently detected
- **Pose Indicators**: Color legend for each pose type
- **Pose Duration**: Real-time tracking of how long each student maintains unethical pose
- **Student IDs**: Unique identifier (STU_0001, STU_0002, etc.)

### Dashboard Integration

All detected offenses automatically appear on the main Dashboard:
1. **Click the "📊 Dashboard" button** to switch views
2. See all flagged students with offense counts
3. View details of their violations
4. Take actions:
   - **Reset**: Remove student from flagged list
   - **Clear Offenses**: Delete all offense records

## System Architecture

### Components

```
Frontend (React)
├── Navigation (Header with Camera/Dashboard links)
├── Dashboard (View flagged students)
└── CameraView (Monitor with detection)
    ├── Video Canvas (Display webcam + overlays)
    ├── Detection Info (Stats & tracking)
    └── Controls (Start/Stop)

Backend (Flask + Socket.IO)
├── REST API (offense logging, statistics)
├── Vision Pipeline (detection thread)
├── Database (SQLite)
└── WebSocket (real-time updates)

Vision Modules
├── PersonDetector (YOLOv5)
├── PersonTracker (DeepSORT)
└── HeadPoseEstimator (MediaPipe)
```

### Data Flow

```
Webcam → Detector → Tracker → Pose Estimator → Pipeline
                                                   ↓
                                            Analyze Duration
                                                   ↓
                                    Log if 3+ seconds
                                                   ↓
                                        WebSocket Emit
                                                   ↓
                                    Frontend Dashboard Update
```

## Behavior Classification

### Ethical (Forward - GREEN)
- Student looking straight ahead at exam
- Head facing forward

### Suspicious (Left/Right - YELLOW)
- Head turned to the left or right
- Could indicate looking at neighbor's exam
- Flagged after 3+ seconds

### Critical (Back - RED)
- Head facing backward/away from exam
- Clear indication of looking at back of room
- Most suspicious behavior
- Immediately flagged after 3+ seconds

## Technical Details

### Head Pose Detection Algorithm
Uses MediaPipe Face Mesh to detect:
1. **Eye position**: Relative positions of left and right eyes
2. **Nose position**: Center face reference point
3. **Angle calculations**: 
   - Horizontal angle for left/right detection
   - Vertical angle for back detection

### Offense Logging Logic
```python
if pose_duration >= 3.0 seconds:
    if not already_logged_this_session:
        log_offense()
        count_offenses()
        
        if offense_count >= 3:
            flag_student()
            broadcast_to_dashboard()
```

### Database Schema
```sql
-- Offenses Table
CREATE TABLE offenses (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    behavior_type TEXT,  -- 'head_turned_left', 'head_turned_right', 'head_turned_back'
    timestamp DATETIME
)

-- Flagged Students Table
CREATE TABLE flagged_students (
    student_id TEXT PRIMARY KEY,
    offenses_count INTEGER,
    flagged_at DATETIME,
    status TEXT  -- 'active', 'inactive'
)
```

## API Endpoints

### Pipeline Control
```
POST /api/pipeline/toggle
- Request: { "enable": true/false }
- Response: { "running": boolean, "status": string }
```

### Detection Data (WebSocket)
```
Event: detection_data
- Data: {
    "detections": [
      {
        "track_id": "1",
        "student_id": "STU_0001",
        "bbox": [x1, y1, x2, y2],
        "pose": "left|right|back|forward",
        "duration": 3.5
      }
    ],
    "frame_count": 150
  }
```

### Offense Logging (WebSocket)
```
Event: student_flagged
- Data: {
    "student_id": "STU_0001",
    "offenses_count": 3,
    "behavior_type": "head_turned_left",
    "timestamp": "2024-04-23T10:30:45.123Z"
  }
```

## Troubleshooting

### Camera Not Starting
- **Check permissions**: Allow camera access in browser settings
- **Port conflict**: Ensure webcam isn't used by other applications
- **Hardware issue**: Try refreshing page or restarting system

### No Detections Appearing
- **Lighting**: Ensure adequate lighting in the room
- **Distance**: Position camera 1-2 meters from subjects
- **Face visibility**: Make sure faces are clearly visible to camera
- **Check backend**: Verify vision pipeline is running

### False Positives
- This is expected with ML models
- Fine-tune thresholds in `backend/app.py` (POSE_THRESHOLD = 3.0)
- Real scenario: Use multiple cameras and cross-verify

### Performance Issues
- **Reduce resolution**: Lower camera resolution in browser settings
- **Decrease detection frequency**: Increase frame skip in pipeline
- **Close other applications**: Free up CPU and GPU resources

## Configuration

### Adjusting Sensitivity

**Change offense threshold (currently 3 seconds):**
```python
# In backend/app.py
POSE_THRESHOLD = 3.0  # Change this value
```

**Lower = More sensitive (catches faster)**
**Higher = Less sensitive (catches only prolonged behavior)**

### Adjusting Detection Accuracy

**In backend/vision/head_pose.py:**
```python
# Horizontal angle threshold for left/right detection
if horizontal_angle > 0.08:  # Adjust this

# Angle threshold for back detection
if angle_x > 20:  # Adjust this
```

## Best Practices

1. **Regular Monitoring**: Check dashboard frequently during exams
2. **Multiple Angles**: For real deployment, use multiple camera angles
3. **Calibration**: Test system before actual exam with sample students
4. **Backup**: Keep traditional proctoring methods as backup
5. **Privacy**: Inform students that they are being monitored

## Example Scenarios

### Scenario 1: Student Looking Left for 4 Seconds
```
Time 0.0s: Student turns head left
Time 1.0s: Yellow indicator - "LEFT (⚠️)" - 1.0s duration
Time 2.0s: Still left - 2.0s duration  
Time 3.0s: OFFENSE LOGGED - 3.0s reached ✓
Time 3.5s: Dashboard shows: STU_0001 | Offenses: 1
Time 4.0s: Back to forward - Timer resets
```

### Scenario 2: Student Gets Flagged (3+ Offenses)
```
First offense: Looking left for 3.2s → Logged (Total: 1)
Second offense: Looking right for 3.5s → Logged (Total: 2)
Third offense: Looking back for 3.1s → Logged (Total: 3) 🚨
Result: Student appears in flagged list on Dashboard
Admin can: Reset/Clear offenses or continue monitoring
```

## Support

For issues or questions:
1. Check logs in backend terminal
2. Verify camera/microphone permissions
3. Ensure Python packages are installed: `pip install -r requirements.txt`
4. Check frontend console for JavaScript errors (F12)
5. Verify backend is running on port 5000

## Next Steps

1. ✅ Test with mock data
2. 🔄 Deploy vision models (install opencv, torch, mediapipe)
3. 📹 Test with real webcam
4. 📊 Monitor dashboard for accuracy
5. 🔧 Fine-tune thresholds based on results
6. 📈 Scale to multiple exam rooms
