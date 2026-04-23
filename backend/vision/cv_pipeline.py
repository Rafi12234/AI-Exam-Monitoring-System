import cv2
import requests
import time
from detector import PersonDetector
from tracker import PersonTracker
from head_pose import HeadPoseEstimator

class CVPipeline:
    """Main Computer Vision Pipeline."""
    
    def __init__(self, backend_url='http://localhost:5000', video_source=0):
        """
        Initialize CV pipeline.
        Args:
            backend_url: URL of Flask backend
            video_source: Video source (0 for webcam, or file path)
        """
        self.backend_url = backend_url
        self.detector = PersonDetector(model_path='yolov5s')
        self.tracker = PersonTracker(max_age=30)
        self.pose_estimator = HeadPoseEstimator()
        
        self.cap = cv2.VideoCapture(video_source)
        self.frame_count = 0
        self.offense_cooldown = {}  # Track offense cooldown per student
        self.cooldown_frames = 30  # Don't log same offense within 30 frames
    
    def run(self):
        """Run the CV pipeline."""
        print("Starting CV Pipeline...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            
            # Detect persons
            detections = self.detector.detect(frame)
            
            # Track persons
            tracks = self.tracker.update(detections)
            
            # Process each tracked person
            for track in tracks:
                track_id = track['track_id']
                bbox = track['bbox']
                student_id = f"STU_{track_id:04d}"
                
                # Estimate head pose
                pose_result = self.pose_estimator.estimate(frame, bbox)
                
                # Check for unethical behavior
                if self.pose_estimator.is_unethical_behavior(pose_result):
                    self._log_offense(student_id, pose_result['pose'])
            
            # Draw annotations
            frame = self.detector.draw_detections(frame, detections)
            frame = self.tracker.draw_tracks(frame, tracks)
            
            # Add frame info
            cv2.putText(frame, f'Frame: {self.frame_count}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('CV Pipeline', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def _log_offense(self, student_id, behavior_type):
        """Log offense to backend with cooldown."""
        current_time = self.frame_count
        
        if student_id in self.offense_cooldown:
            if current_time - self.offense_cooldown[student_id] < self.cooldown_frames:
                return  # Skip logging (still in cooldown)
        
        try:
            response = requests.post(
                f'{self.backend_url}/api/log_offense',
                json={
                    'student_id': student_id,
                    'behavior_type': behavior_type
                },
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Logged offense for {student_id}: {behavior_type} "
                      f"(Total: {data['offenses_count']}, Flagged: {data['flagged']})")
                self.offense_cooldown[student_id] = current_time
        
        except requests.exceptions.RequestException as e:
            print(f"Error logging offense: {e}")

if __name__ == '__main__':
    pipeline = CVPipeline(
        backend_url='http://localhost:5000',
        video_source=0  # Use webcam
    )
    pipeline.run()
