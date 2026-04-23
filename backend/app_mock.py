"""
Mock backend endpoints for testing the frontend without actual CV pipeline
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import random
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import cv2
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load face cascade classifier for real head detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Mock data
mock_flagged_students = [
    {
        'student_id': 'STU_0001',
        'offenses_count': 5,
        'status': 'active',
        'flagged_at': (datetime.now() - timedelta(hours=2)).isoformat()
    },
    {
        'student_id': 'STU_0002',
        'offenses_count': 3,
        'status': 'active',
        'flagged_at': (datetime.now() - timedelta(hours=1)).isoformat()
    },
    {
        'student_id': 'STU_0003',
        'offenses_count': 4,
        'status': 'active',
        'flagged_at': (datetime.now() - timedelta(minutes=30)).isoformat()
    }
]

mock_offenses = {
    'STU_0001': [
        {'behavior_type': 'back', 'timestamp': (datetime.now() - timedelta(minutes=i*5)).isoformat()}
        for i in range(1, 6)
    ],
    'STU_0002': [
        {'behavior_type': 'left', 'timestamp': (datetime.now() - timedelta(minutes=i*10)).isoformat()}
        for i in range(1, 4)
    ],
    'STU_0003': [
        {'behavior_type': 'right', 'timestamp': (datetime.now() - timedelta(minutes=i*8)).isoformat()}
        for i in range(1, 5)
    ]
}

@app.route('/api/flagged_students', methods=['GET'])
def get_flagged_students():
    return jsonify({'status': 'success', 'data': mock_flagged_students}), 200

@app.route('/api/students/<student_id>/offenses', methods=['GET'])
def get_student_offenses(student_id):
    offenses = mock_offenses.get(student_id, [])
    return jsonify({'status': 'success', 'data': offenses}), 200

@app.route('/api/log_offense', methods=['POST'])
def log_offense():
    data = request.json
    student_id = data.get('student_id')
    behavior_type = data.get('behavior_type', 'unethical')
    
    return jsonify({
        'status': 'success',
        'offenses_count': random.randint(1, 5),
        'flagged': True
    }), 200

@app.route('/api/reset_student/<student_id>', methods=['POST'])
def reset_student(student_id):
    return jsonify({'status': 'success', 'message': 'Student reset'}), 200

@app.route('/api/clear_offenses/<student_id>', methods=['POST'])
def clear_offenses(student_id):
    return jsonify({'status': 'success', 'message': 'Offenses cleared'}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'status': 'success',
        'data': {
            'flagged_students': len(mock_flagged_students),
            'students_with_offenses': len(mock_offenses),
            'total_offenses': sum(len(v) for v in mock_offenses.values())
        }
    }), 200

@app.route('/api/detect_heads', methods=['POST'])
def detect_heads():
    """Analyze frame from frontend and detect heads"""
    try:
        # Check if request has JSON data
        if not request.json:
            print("❌ No JSON data in request")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        frame_data = request.json.get('frame')
        
        if not frame_data or not isinstance(frame_data, str):
            print(f"❌ Invalid frame data: {type(frame_data)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid frame data format'
            }), 400
        
        # Decode base64 image from frontend
        try:
            # Remove data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Decode base64 to bytes
            frame_bytes = base64.b64decode(frame_data, validate=True)
            
            # Load image from bytes
            image = Image.open(BytesIO(frame_bytes))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect faces/heads
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            head_count = len(faces)
            print(f"✅ Frame analyzed: {head_count} head(s) detected")
            
            # Broadcast via WebSocket to all connected clients
            with app.app_context():
                socketio.emit('head_count_update', {
                    'head_count': head_count,
                    'timestamp': datetime.now().isoformat()
                }, skip_sid=None)
            
            return jsonify({
                'status': 'success',
                'head_count': head_count,
                'message': f'{head_count} head(s) detected'
            }), 200
            
        except base64.binascii.Error as e:
            print(f"❌ Base64 decode error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Invalid base64 data: {str(e)}'
            }), 400
        except Exception as e:
            print(f"❌ Frame processing error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'Frame processing failed: {str(e)}'
            }), 400
            
    except Exception as e:
        print(f"❌ Request error: {type(e).__name__}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'data': 'Connected to mock server'})

if __name__ == '__main__':
    print("Starting Mock Backend Server on 0.0.0.0:5000...")
    print("This is for testing purposes only. Use app.py for production.")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
