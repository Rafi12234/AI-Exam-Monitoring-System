import React, { useEffect, useRef, useState } from 'react';
import { useContext } from 'react';
import { FlaggedStudentsContext } from '../context/FlaggedStudentsContext';
import { socket } from '../utils/socket';
import '../styles/CameraView.css';

export default function CameraView() {
  const canvasRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const frameCountRef = useRef(0);
  const { fetchFlaggedStudents } = useContext(FlaggedStudentsContext);
  const [cameraActive, setCameraActive] = useState(false);
  const [detections, setDetections] = useState([]);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [studentPoses, setStudentPoses] = useState({});
  const [systemStatus, setSystemStatus] = useState('idle');
  const [headCount, setHeadCount] = useState(null);

  useEffect(() => {
    // Listen for detection data from backend
    socket.on('detection_data', (data) => {
      setDetections(data.detections || []);
      if (data.student_id && data.pose && data.pose !== 'forward') {
        setStudentPoses(prev => ({
          ...prev,
          [data.student_id]: {
            pose: data.pose,
            duration: data.duration,
            timestamp: Date.now()
          }
        }));
      }
    });

    socket.on('offense_detected', (data) => {
      console.log('Offense detected:', data);
      fetchFlaggedStudents();
    });

    socket.on('pipeline_status', (status) => {
      setPipelineRunning(status.running);
      setSystemStatus(status.status);
    });

    // Listen for real-time head count updates
    socket.on('head_count_update', (data) => {
      console.log('📊 Head count update received:', data);
      setHeadCount(data.head_count);
    });

    return () => {
      socket.off('detection_data');
      socket.off('offense_detected');
      socket.off('pipeline_status');
      socket.off('head_count_update');
    };
  }, [fetchFlaggedStudents]);

  // Initialize webcam
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setHeadCount(null);
        frameCountRef.current = 0;
        
        console.log('🎬 Camera started - will send frames for analysis');
        
        // Wait for video to be ready before drawing
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          drawFrames();
        };
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Could not access camera. Please check permissions.');
    }
  };

  // Stop camera and detection
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      setCameraActive(false);
      setDetections([]);
      setStudentPoses({});
      setHeadCount(null);
      
      // Stop real-time detection on backend
      fetch('http://localhost:5000/api/detect_heads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enable: false })
      }).catch(error => console.error('Error stopping detection:', error));
    }
  };

  // Draw frames with detection boxes and send to backend for analysis
  const drawFrames = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) {
      if (cameraActive) {
        requestAnimationFrame(drawFrames);
      }
      return;
    }

    // Check if canvas dimensions are set
    if (canvas.width === 0 && video.videoWidth > 0) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    if (video.videoWidth > 0 && video.videoHeight > 0) {
      const ctx = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw video frame
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Send frame to backend for head detection (every 5 frames for performance)
      if (frameCountRef.current % 5 === 0) {
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        fetch('http://localhost:5000/api/detect_heads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame: frameData })
        })
          .then(response => {
            if (!response.ok) {
              console.error(`❌ API Error ${response.status}:`, response.statusText);
              return response.json().then(data => console.error('Error details:', data));
            }
            return response.json();
          })
          .then(data => {
            if (data && data.head_count !== undefined) {
              console.log(`✅ Heads detected: ${data.head_count}`);
            }
          })
          .catch(error => console.error('❌ Frame send error:', error));
      }
      
      frameCountRef.current++;

      // Draw detection boxes
      detections.forEach((detection, idx) => {
        const [x1, y1, x2, y2] = detection.bbox;
        const w = x2 - x1;
        const h = y2 - y1;

        // Color based on pose
        let color = '#00FF00'; // green for forward
        let label = `ID: ${detection.track_id} - Forward`;

        if (detection.pose === 'left') {
          color = '#FFFF00'; // yellow for left
          label = `ID: ${detection.track_id} - LEFT (⚠️)`;
        } else if (detection.pose === 'right') {
          color = '#FFFF00'; // yellow for right
          label = `ID: ${detection.track_id} - RIGHT (⚠️)`;
        } else if (detection.pose === 'back') {
          color = '#FF0000'; // red for back
          label = `ID: ${detection.track_id} - BACK (🚨)`;
        }

        // Draw bounding box
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, w, h);

        // Draw label background
        ctx.fillStyle = color;
        ctx.font = 'bold 14px Arial';
        const textWidth = ctx.measureText(label).width;
        ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);

        // Draw label text
        ctx.fillStyle = '#000';
        ctx.fillText(label, x1 + 5, y1 - 8);

        // Draw duration if pose is unethical
        if (detection.pose !== 'forward') {
          const poseData = studentPoses[detection.student_id];
          if (poseData) {
            const durationText = `Duration: ${poseData.duration.toFixed(1)}s`;
            ctx.fillStyle = color;
            ctx.fillText(durationText, x1 + 5, y1 + h + 20);
          }
        }
      });
    }

    requestAnimationFrame(drawFrames);
  };

  // Start/Stop vision pipeline on backend
  const togglePipeline = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/pipeline/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enable: !pipelineRunning })
      });
      const data = await response.json();
      setPipelineRunning(data.running);
      setSystemStatus(data.status);
    } catch (error) {
      console.error('Error toggling pipeline:', error);
    }
  };

  return (
    <div className="camera-view-container">
      <div className="camera-header">
        <h2>📹 Live Camera Monitoring</h2>
        <div className="status-indicator">
          <span className={`status-dot ${pipelineRunning ? 'active' : 'inactive'}`}></span>
          <span className="status-text">{systemStatus.toUpperCase()}</span>
        </div>
      </div>

      <div className="camera-controls">
        <button 
          className={`btn btn-primary ${cameraActive ? 'active' : ''}`}
          onClick={cameraActive ? stopCamera : startCamera}
        >
          {cameraActive ? '⏹ Stop Camera' : '▶ Start Camera'}
        </button>

        <button 
          className={`btn btn-secondary ${pipelineRunning ? 'active' : ''}`}
          onClick={togglePipeline}
          disabled={!cameraActive}
        >
          {pipelineRunning ? '🛑 Stop Detection' : '🎯 Start Detection'}
        </button>
      </div>

      {cameraActive && (
        <div className="head-detection-panel">
          {headCount === null ? (
            <div className="detecting-status">
              <span className="spinner"></span>
              <span className="detecting-text">🔍 Initializing head detection...</span>
            </div>
          ) : (
            <div className={`head-count-display ${headCount > 0 ? 'active' : 'empty'}`}>
              <div className="head-count-value">{headCount}</div>
              <div className="head-count-label">
                {headCount === 1 ? 'Head Detected' : headCount === 0 ? 'No Heads' : 'Heads Detected'}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="camera-display">
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            style={{ display: 'none' }}
          />
          <canvas
            ref={canvasRef}
            className="detection-canvas"
            style={{
              display: cameraActive ? 'block' : 'none',
              width: '100%',
              height: 'auto'
            }}
          />
          {!cameraActive && (
            <div className="camera-placeholder">
              <p>Camera Not Active</p>
              <p className="hint">Click "Start Camera" to begin monitoring</p>
            </div>
          )}
        </div>
      </div>

      <div className="detection-info">
        <div className="info-section">
          <h3>🎯 Active Detections</h3>
          <p className="info-value">{detections.length} students detected</p>
        </div>

        <div className="info-section">
          <h3>⚠️ Pose Indicators</h3>
          <div className="pose-legend">
            <div className="legend-item">
              <span className="color-box forward"></span>
              <span>Forward (Ethical)</span>
            </div>
            <div className="legend-item">
              <span className="color-box warning"></span>
              <span>Left/Right (Warning - 3s)</span>
            </div>
            <div className="legend-item">
              <span className="color-box danger"></span>
              <span>Back (Critical - Offense)</span>
            </div>
          </div>
        </div>

        <div className="info-section">
          <h3>⏱️ Pose Duration Tracking</h3>
          {Object.keys(studentPoses).length > 0 ? (
            <div className="pose-tracking">
              {Object.entries(studentPoses).map(([studentId, poseData]) => (
                <div key={studentId} className="pose-item">
                  <span className="student-id">{studentId}</span>
                  <span className={`pose-badge ${poseData.pose}`}>
                    {poseData.pose.toUpperCase()}
                  </span>
                  <span className="duration">{poseData.duration.toFixed(1)}s</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-data">No unethical poses detected</p>
          )}
        </div>
      </div>

      <div className="help-text">
        <p>💡 <strong>How it works:</strong> The system detects when a student's head turns LEFT, RIGHT, or BACK for more than 3 seconds. These are logged as offenses and shown on the dashboard in real-time.</p>
      </div>
    </div>
  );
}
