from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import os
from datetime import datetime
import threading
import json
from collections import defaultdict
from time import time

# Optional imports - will be handled in pipeline functions
try:
    import cv2
except ImportError:
    cv2 = None

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = 'database.db'

# Vision pipeline state
pipeline_state = {
    'running': False,
    'thread': None,
    'cap': None,
    'stop_event': threading.Event(),
    'student_pose_timers': defaultdict(lambda: {'pose': 'forward', 'start_time': 0, 'duration': 0})
}

POSE_THRESHOLD = 3.0  # 3 seconds to trigger offense

def init_db():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Offenses table to log all offenses
    c.execute('''
        CREATE TABLE IF NOT EXISTS offenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            behavior_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Flagged students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS flagged_students (
            student_id TEXT PRIMARY KEY,
            offenses_count INTEGER DEFAULT 0,
            flagged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_vision_pipeline():
    """Run the computer vision pipeline for real-time detection."""
    try:
        print("🎥 Starting Vision Pipeline...")
        
        # Try to import vision modules
        try:
            from vision.detector import PersonDetector
            from vision.tracker import PersonTracker
            from vision.head_pose import HeadPoseEstimator
        except ImportError as e:
            print(f"⚠️ Vision modules not available: {e}")
            print("Using mock detection mode...")
            run_mock_pipeline()
            return
        
        # Initialize models
        detector = PersonDetector()
        tracker = PersonTracker()
        pose_estimator = HeadPoseEstimator()
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        pipeline_state['cap'] = cap
        frame_count = 0
        offenses_logged = {}  # Track logged offenses to prevent spam
        
        print("✅ Vision Pipeline running...")
        
        while not pipeline_state['stop_event'].is_set():
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Run detection every 2 frames (for performance)
            if frame_count % 2 == 0:
                try:
                    # Detect persons
                    detections = detector.detect(frame)
                    
                    # Track persons
                    tracks = tracker.update(detections)
                    
                    detection_data = []
                    
                    for track in tracks:
                        track_id = str(track.track_id)
                        bbox = track.bbox
                        
                        # Generate student_id from track_id
                        student_id = f"STU_{int(track_id):04d}"
                        
                        # Estimate head pose
                        try:
                            pose = pose_estimator.estimate(frame, bbox)
                        except:
                            pose = 'forward'
                        
                        # Update pose timer
                        current_time = time()
                        pose_timer = pipeline_state['student_pose_timers'][student_id]
                        
                        if pose != 'forward':
                            # Unethical pose detected
                            if pose_timer['pose'] == pose:
                                # Continue timing
                                pose_timer['duration'] = current_time - pose_timer['start_time']
                            else:
                                # New pose detected
                                pose_timer['pose'] = pose
                                pose_timer['start_time'] = current_time
                                pose_timer['duration'] = 0
                            
                            # Check if duration exceeded threshold
                            if pose_timer['duration'] >= POSE_THRESHOLD:
                                # Log offense if not already logged for this pose
                                log_key = f"{student_id}_{pose}_{int(pose_timer['start_time'])}"
                                
                                if log_key not in offenses_logged:
                                    # Log offense
                                    conn = get_db_connection()
                                    c = conn.cursor()
                                    c.execute(
                                        'INSERT INTO offenses (student_id, behavior_type) VALUES (?, ?)',
                                        (student_id, f'head_turned_{pose}')
                                    )
                                    c.execute('SELECT COUNT(*) FROM offenses WHERE student_id = ?', (student_id,))
                                    count = c.fetchone()[0]
                                    
                                    if count >= 3:
                                        c.execute(
                                            'INSERT OR REPLACE INTO flagged_students (student_id, offenses_count, status) VALUES (?, ?, ?)',
                                            (student_id, count, 'active')
                                        )
                                        socketio.emit('student_flagged', {
                                            'student_id': student_id,
                                            'offenses_count': count,
                                            'behavior_type': f'head_turned_{pose}',
                                            'timestamp': datetime.now().isoformat()
                                        }, broadcast=True)
                                    
                                    conn.commit()
                                    conn.close()
                                    
                                    offenses_logged[log_key] = True
                                    print(f"🚨 OFFENSE: {student_id} turned {pose} for {pose_timer['duration']:.1f}s")
                        else:
                            # Ethical pose - reset timer
                            pose_timer['pose'] = 'forward'
                            pose_timer['duration'] = 0
                        
                        # Prepare detection data for frontend
                        detection_data.append({
                            'track_id': track_id,
                            'student_id': student_id,
                            'bbox': bbox.tolist() if hasattr(bbox, 'tolist') else bbox,
                            'pose': pose,
                            'duration': pose_timer['duration']
                        })
                    
                    # Emit detection data to connected clients
                    socketio.emit('detection_data', {
                        'detections': detection_data,
                        'frame_count': frame_count
                    }, broadcast=True)
                
                except Exception as e:
                    print(f"⚠️ Error in detection: {e}")
            
            # Small delay to prevent CPU overload
            cv2.waitKey(1)
        
        cap.release()
        print("✅ Vision Pipeline stopped")
        
    except Exception as e:
        print(f"❌ Vision Pipeline Error: {e}")
    finally:
        if pipeline_state['cap']:
            pipeline_state['cap'].release()

def run_mock_pipeline():
    """Run mock pipeline when vision modules aren't available."""
    import random
    print("🎯 Running in Mock Detection Mode...")
    
    frame_count = 0
    offenses_logged = {}
    
    while not pipeline_state['stop_event'].is_set():
        frame_count += 1
        
        # Simulate 2-3 students
        detection_data = []
        for i in range(random.randint(2, 3)):
            student_id = f"STU_{(i+1):04d}"
            track_id = str(i + 1)
            
            # Random pose (80% forward, 20% other)
            pose_chance = random.random()
            if pose_chance < 0.15:
                pose = 'left'
            elif pose_chance < 0.30:
                pose = 'right'
            elif pose_chance < 0.40:
                pose = 'back'
            else:
                pose = 'forward'
            
            # Simulate pose duration
            if pose != 'forward':
                pose_timer = pipeline_state['student_pose_timers'][student_id]
                if pose_timer['pose'] == pose:
                    pose_timer['duration'] += 0.1
                else:
                    pose_timer['pose'] = pose
                    pose_timer['start_time'] = time()
                    pose_timer['duration'] = 0
                
                # Log offense if threshold exceeded
                if pose_timer['duration'] >= POSE_THRESHOLD:
                    log_key = f"{student_id}_{pose}_{int(pose_timer['start_time'])}"
                    
                    if log_key not in offenses_logged:
                        # Log offense
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute(
                            'INSERT INTO offenses (student_id, behavior_type) VALUES (?, ?)',
                            (student_id, f'head_turned_{pose}')
                        )
                        c.execute('SELECT COUNT(*) FROM offenses WHERE student_id = ?', (student_id,))
                        count = c.fetchone()[0]
                        
                        if count >= 3:
                            c.execute(
                                'INSERT OR REPLACE INTO flagged_students (student_id, offenses_count, status) VALUES (?, ?, ?)',
                                (student_id, count, 'active')
                            )
                            socketio.emit('student_flagged', {
                                'student_id': student_id,
                                'offenses_count': count,
                                'behavior_type': f'head_turned_{pose}',
                                'timestamp': datetime.now().isoformat()
                            }, broadcast=True)
                        
                        conn.commit()
                        conn.close()
                        
                        offenses_logged[log_key] = True
            else:
                pipeline_state['student_pose_timers'][student_id] = {'pose': 'forward', 'start_time': 0, 'duration': 0}
            
            detection_data.append({
                'track_id': track_id,
                'student_id': student_id,
                'bbox': [100 + i*400, 100, 300 + i*400, 500],
                'pose': pose,
                'duration': pipeline_state['student_pose_timers'][student_id]['duration']
            })
        
        socketio.emit('detection_data', {
            'detections': detection_data,
            'frame_count': frame_count
        }, broadcast=True)
        
        import time as time_module
        time_module.sleep(0.5)  # Simulate frame rate

# ======================== API Routes ========================

@app.route('/api/flagged_students', methods=['GET'])
def get_flagged_students():
    """Retrieve all flagged students."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM flagged_students WHERE status = ?', ('active',))
        students = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'status': 'success', 'data': students}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/students/<student_id>/offenses', methods=['GET'])
def get_student_offenses(student_id):
    """Retrieve offenses for a specific student."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM offenses WHERE student_id = ? ORDER BY timestamp DESC', (student_id,))
        offenses = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'status': 'success', 'data': offenses}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/log_offense', methods=['POST'])
def log_offense():
    """Log a new offense and flag student if threshold reached."""
    try:
        data = request.json
        student_id = data.get('student_id')
        behavior_type = data.get('behavior_type', 'unethical')
        
        if not student_id:
            return jsonify({'status': 'error', 'message': 'Student ID required'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Insert offense
        c.execute(
            'INSERT INTO offenses (student_id, behavior_type) VALUES (?, ?)',
            (student_id, behavior_type)
        )
        
        # Count total offenses for this student
        c.execute('SELECT COUNT(*) FROM offenses WHERE student_id = ?', (student_id,))
        count = c.fetchone()[0]
        
        # Flag student if count >= 3
        if count >= 3:
            c.execute(
                'INSERT OR REPLACE INTO flagged_students (student_id, offenses_count, status) VALUES (?, ?, ?)',
                (student_id, count, 'active')
            )
            conn.commit()
            
            # Emit real-time update to all connected clients
            flagged_data = {
                'student_id': student_id,
                'offenses_count': count,
                'behavior_type': behavior_type,
                'timestamp': datetime.now().isoformat()
            }
            socketio.emit('student_flagged', flagged_data, broadcast=True)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'offenses_count': count,
            'flagged': count >= 3
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reset_student/<student_id>', methods=['POST'])
def reset_student(student_id):
    """Reset a student's offense count."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE flagged_students SET status = ? WHERE student_id = ?', ('inactive', student_id))
        conn.commit()
        conn.close()
        
        socketio.emit('student_reset', {'student_id': student_id}, broadcast=True)
        return jsonify({'status': 'success', 'message': 'Student reset'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clear_offenses/<student_id>', methods=['POST'])
def clear_offenses(student_id):
    """Clear all offenses for a student."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM offenses WHERE student_id = ?', (student_id,))
        c.execute('DELETE FROM flagged_students WHERE student_id = ?', (student_id,))
        conn.commit()
        conn.close()
        
        socketio.emit('student_cleared', {'student_id': student_id}, broadcast=True)
        return jsonify({'status': 'success', 'message': 'Offenses cleared'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM flagged_students WHERE status = ?', ('active',))
        flagged_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(DISTINCT student_id) FROM offenses')
        total_offenses_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM offenses')
        total_offenses = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'flagged_students': flagged_count,
                'students_with_offenses': total_offenses_count,
                'total_offenses': total_offenses
            }
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/pipeline/toggle', methods=['POST'])
def toggle_pipeline():
    """Start or stop the vision pipeline."""
    try:
        data = request.json
        enable = data.get('enable', False)
        
        if enable and not pipeline_state['running']:
            # Start pipeline
            pipeline_state['stop_event'].clear()
            pipeline_state['thread'] = threading.Thread(target=run_vision_pipeline, daemon=True)
            pipeline_state['thread'].start()
            pipeline_state['running'] = True
            
            socketio.emit('pipeline_status', {
                'running': True,
                'status': 'Pipeline active - monitoring students'
            }, broadcast=True)
            
            return jsonify({
                'status': 'success',
                'running': True,
                'message': 'Pipeline started'
            }), 200
        
        elif not enable and pipeline_state['running']:
            # Stop pipeline
            pipeline_state['stop_event'].set()
            if pipeline_state['thread']:
                pipeline_state['thread'].join(timeout=5)
            pipeline_state['running'] = False
            pipeline_state['student_pose_timers'].clear()
            
            socketio.emit('pipeline_status', {
                'running': False,
                'status': 'Pipeline stopped'
            }, broadcast=True)
            
            return jsonify({
                'status': 'success',
                'running': False,
                'message': 'Pipeline stopped'
            }), 200
        
        return jsonify({
            'status': 'success',
            'running': pipeline_state['running'],
            'message': 'Pipeline already in requested state'
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/pipeline/status', methods=['GET'])
def pipeline_status():
    """Get pipeline status."""
    try:
        return jsonify({
            'status': 'success',
            'running': pipeline_state['running'],
            'message': 'Pipeline active' if pipeline_state['running'] else 'Pipeline inactive'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ======================== WebSocket Events ========================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connection_response', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('request_flagged_students')
def handle_request(data):
    """Handle request for flagged students."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM flagged_students WHERE status = ?', ('active',))
    students = [dict(row) for row in c.fetchall()]
    conn.close()
    emit('flagged_students_update', {'data': students})

# ======================== Health Check ========================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

# ======================== Main ========================

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        # Ensure tables exist
        init_db()
    
    print("Starting Flask-SocketIO server on 0.0.0.0:5000...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
